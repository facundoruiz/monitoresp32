import ure as re
import ubluetooth
import ubinascii
import time
import math
from machine import reset
from conector_wifi import ConectorWIFI

import ure as re
import ubluetooth

import ubinascii
import time
from machine import reset
from conector_wifi import ConectorWIFI
from micropython import const

# Global variables
ble = ubluetooth.BLE()
ble.active(True)
scanned_devices = {}
selected_device = None
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

def decode_name(payload):
    """Decodificar el nombre del dispositivo desde los datos de advertising"""
    i = 0
    result = "Unknown"
    while i < len(payload):
        try:
            length = payload[i]
            if i + length + 1 > len(payload):
                break
            
            ad_type = payload[i + 1]
            # Buscar tipos de nombre (Complete Local Name o Shortened Local Name)
            if ad_type  in [0x08, 0x09]:
                name_bytes = payload[i + 2:i + length + 1]
                try:
                    return str(name_bytes, "utf-8") if name_bytes else ""
                except:
                    pass
            i += length + 1
        except Exception as e:
             print("Error decodificando nombre:", e)
    return result
    

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
    print(f"Dispositivo : {device_name} ({addr_hex}) - {distance}m")



def start_ble_scan(duration=10):
    """Inicia un nuevo escaneo BLE"""
    try:
            print("Iniciando escaneo BLE...")
            scanned_devices = []  # Reiniciar la lista de dispositivos
   
            ble.gap_scan(duration * 1000, 30000, 30000, True)
            time.sleep(duration)  # Esperar a que termine el escaneo
            ble.gap_scan(None)  # Detener el escaneo
            print(f"Escaneo terminado. Dispositivos encontrados: {len(scanned_devices)}")
    except Exception as e:
            print(f"Error durante el escaneo BLE: {e}")



def main():
    try:
        '''    # ACCESS POINT - instancia  con debug para ver mensajes 
                wifi = ConectorWIFI(
                    ssid='TestESP32',
                    password='password123',
                    debug=True
                )
                    # Iniciar la conexión AL WIFI si falla se accede al AP
                wifi.wifi_connect('MI_WIFI_CASA','fdsfsdfsdfsdf',1)
        
                # Intentar conectar
                if not wifi.connect():
                    print("Error en la conexión WiFi")
                    # Opcional: reiniciar el dispositivo
                    #reset()  '''
        if not ble.active():
            ble.active(True)    

            ble.irq(ble_scan_callback)
            print("BLE configurado")
            devices_html = "" 
            start_ble_scan(),  # Escaneo BLE en bucle
            if len(scanned_devices) > 0:
                for device in scanned_devices:
                    devices_html += '<span class="rssi">RSSI: {} - {}</span>'.format(device["rssi"],device["type"])
            else:
                    devices_html = 'No se encontraron dispositivos.'
            print(f" {devices_html}")
    except Exception as e:
        print(f"Error: {e}")
        reset()

if __name__ == '__main__':
    main()