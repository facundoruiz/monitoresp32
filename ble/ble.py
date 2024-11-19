import network
import socket
import ure as re
import ubluetooth
import ubinascii
import time
import math
from machine import reset

# Wi-Fi connection parameters
SSID = ""
PASSWORD = ""

# Global variables
ble = ubluetooth.BLE()
ble.active(True)
scanned_devices = {}
BLE_MSG_SCAN = const(5)

def calculate_distance(rssi, tx_power=-59):
    """
    Calcula la distancia aproximada basada en RSSI
    usando el modelo de pérdida de ruta logarítmico
    """
    if rssi == 0:
        return -1.0
    # Usar el modelo de pérdida de ruta más preciso
    n = 2.0  # Factor de pérdida de ruta (2.0 para espacio libre)
    distance = 10 ** ((tx_power - rssi) / (10 * n))
    return round(distance, 2)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a WiFi...')
        wlan.connect(SSID, PASSWORD)
        timeout = 0
        while not wlan.isconnected() and timeout < 10:
            time.sleep(1)
            timeout += 1
        if not wlan.isconnected():
            raise Exception("No se pudo conectar al WiFi")
    print('Configuración de red:', wlan.ifconfig())
    return wlan.ifconfig()[0]

def decode_name(payload):
    """Decode the device name from raw advertising data"""
    i = 0
    while i < len(payload):
        try:
            length = payload[i]
            if i + length + 1 > len(payload):
                break
            
            ad_type = payload[i + 1]
            # Buscar tipos de nombre (Complete Local Name o Shortened Local Name)
            if ad_type == 0x09 or ad_type == 0x08:
                name_bytes = payload[i + 2:i + length + 1]
                try:
                    return name_bytes.decode('utf-8')
                except:
                    return "Nombre inválido"
            i += length + 1
        except:
            break
    return "Desconocido"

def ble_scan_callback(event, data):
    if event != BLE_MSG_SCAN:
        return
    
    addr_type, addr, adv_type, rssi, adv_data = data
    if rssi < -90:  # Filtrar dispositivos muy lejanos
        return
        
    addr_hex = ubinascii.hexlify(addr).decode()
    device_name = decode_name(adv_data)
    distance = calculate_distance(rssi)
    
    # Actualizar o agregar dispositivo
    scanned_devices[addr_hex] = {
        "name": device_name,
        "rssi": rssi,
        "distance": distance,
        "last_seen": time.time(),
        "type": determine_device_type(device_name),
        "connected": False
    }
    print(f"Dispositivo encontrado: {device_name} ({addr_hex}) - {distance}m")

def determine_device_type(name):
    """Determina el tipo de dispositivo basado en el nombre"""
    name_lower = name.lower()
    if any(word in name_lower for word in ["watch", "reloj"]):
        return "Reloj Inteligente"
    elif any(word in name_lower for word in ["phone", "telefono", "móvil"]):
        return "Teléfono"
    elif any(word in name_lower for word in ["headphone", "auricular", "airpod"]):
        return "Auriculares"
    elif any(word in name_lower for word in ["speaker", "altavoz"]):
        return "Altavoz"
    return "Dispositivo"

def start_ble_scan(duration=10):
    """Inicia un nuevo escaneo BLE"""
    print("Iniciando escaneo BLE...")
    scanned_devices.clear()  # Limpiar dispositivos anteriores
    ble.gap_scan(duration * 1000, 30000, 30000, True)
    time.sleep(duration)  # Esperar a que termine el escaneo
    ble.gap_scan(None)  # Detener el escaneo

def connect_ble_device(addr):
    """Conecta o desconecta un dispositivo BLE"""
    try:
        if addr not in scanned_devices:
            return False
            
        device = scanned_devices[addr]
        if device['connected']:
            # Desconectar
            ble.gap_disconnect(0)  # Asumiendo que solo manejamos una conexión
            device['connected'] = False
            print(f"Desconectado: {device['name']}")
        else:
            # Conectar
            addr_bytes = ubinascii.unhexlify(addr)
            ble.gap_connect(0, addr_bytes)
            device['connected'] = True
            print(f"Conectado a: {device['name']}")
        return True
    except Exception as e:
        print("Error en conexión:", e)
        return False

HTML_STYLE = """
<style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }
    .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1 { text-align: center; color: #2c3e50; }
    .scan-btn { display: block; width: 200px; margin: 20px auto; padding: 10px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; }
    .device-card { background: white; margin: 10px 0; padding: 15px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); position: relative; }
    .device-name { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
    .device-info { font-size: 14px; color: #666; }
    .device-distance { position: absolute; right: 15px; top: 15px; font-size: 20px; font-weight: bold; color: #3498db; }
    .connect-btn { background: #2ecc71; color: white; border: none; padding: 5px 15px; border-radius: 3px; cursor: pointer; }
    .connect-btn:hover { background: #27ae60; }
    .status { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
    .status.connected { background: #2ecc71; }
    .status.disconnected { background: #e74c3c; }
    #last-scan { text-align: center; color: #95a5a6; margin-top: 20px; }
</style>
"""

def generate_device_html(addr, device):
    """Genera el HTML para un dispositivo individual"""
    status_class = "connected" if device['connected'] else "disconnected"
    button_text = "Desconectar" if device['connected'] else "Conectar"
    
    return f"""
    <div class="device-card">
        <div class="device-name">
            <span class="status {status_class}"></span>
            {device['name']}
        </div>
        <div class="device-info">
            <div>Tipo: {device['type']}</div>
            <div>RSSI: {device['rssi']} dBm</div>
            <div>Dirección: {addr}</div>
        </div>
        <div class="device-distance">{device['distance']}m</div>
        <button class="connect-btn" onclick="window.location.href='/connect?addr={addr}'">{button_text}</button>
    </div>
    """

def web_page():
    """Genera la página web completa"""
    devices_html = ""
    if scanned_devices:
        devices_html = "".join([generate_device_html(addr, device) 
                              for addr, device in sorted(scanned_devices.items(), 
                                                       key=lambda x: x[1]['rssi'], 
                                                       reverse=True)])
    else:
        devices_html = "<p style='text-align:center'>No se encontraron dispositivos</p>"

    current_time = time.localtime()
    time_str = "{:02d}:{:02d}:{:02d}".format(current_time[3], current_time[4], current_time[5])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 BLE Scanner</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta charset="UTF-8">
        {HTML_STYLE}
    </head>
    <body>
        <div class="container">
            <h1>ESP32 BLE Scanner</h1>
            <button class="scan-btn" onclick="window.location.href='/scan'">Buscar Dispositivos</button>
            <div id="devices">{devices_html}</div>
            <div id="last-scan">Última actualización: {time_str}</div>
        </div>
    </body>
    </html>
    """

def web_server(ip):
    """Maneja el servidor web"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, 80))
    s.listen(5)
    
    while True:
        try:
            conn, addr = s.accept()
            request = conn.recv(1024).decode()
            
            if "GET /scan" in request:
                start_ble_scan()
                response = "HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n"
            elif "GET /connect" in request:
                match = re.search(r"GET /connect\?addr=([0-9a-fA-F]+)", request)
                if match:
                    connect_ble_device(match.group(1))
                response = "HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n"
            else:
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{web_page()}"
            
            conn.send(response.encode())
            conn.close()
            
        except Exception as e:
            print("Error en servidor web:", e)
            try:
                conn.close()
            except:
                pass

def main():
    try:
        print("Iniciando sistema...")
        if not ble.active():
            ble.active(True)
        
        # Conectar WiFi
#         ip = connect_wifi()
#         print(f"Servidor web disponible en http://{ip}")
        
        # Configurar BLE
        ble.irq(ble_scan_callback)
        print("BLE configurado")
        
        # Escaneo inicial
        start_ble_scan()
        
        # Iniciar servidor web
#         web_server(ip)
        
    except Exception as e:
        print("Error en main:", e)
        print("Reiniciando en 5 segundos...")
        time.sleep(5)
        reset()

if __name__ == "__main__":
    main()