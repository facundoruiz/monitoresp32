from network import WLAN, STA_IF, AP_IF, AUTH_WPA2_PSK
import socket
from time import sleep,time
import re
from json import dumps,loads
from machine import  unique_id

class ConectorWIFI:
    def __init__(self, ssid='WifiManager', password='wifimanager', debug=False):
        # Inicialización de interfaces
        self.wlan_sta = WLAN(STA_IF)
        self.wlan_ap = WLAN(AP_IF)
        self.wlan_sta.active(True)
        self.ap_ssid = ssid
        self.ap_password = password
        self.ap_authmode = AUTH_WPA2_PSK
        self.debug = debug
        self.connection_timeout = 15
        self.server_socket = None

        # Security features
        self.wifi_credentials = 'wifi.dat.enc'
        self._salt = unique_id()
        self.max_failed_attempts = 5
        self.failed_attempts = {}
    
    def _encrypt_credentials(self, data):
        encrypted = bytearray()
        key = self._salt
        for i, byte in enumerate(dumps(data).encode()):
            encrypted.append(byte ^ key[i % len(key)])
        return encrypted

    def _decrypt_credentials(self, encrypted_data):
        decrypted = bytearray()
        key = self._salt
        for i, byte in enumerate(encrypted_data):
            decrypted.append(byte ^ key[i % len(key)])
        try:
            return loads(decrypted.decode())
        except:
            return {}
        
    def connect(self):
        """Intento de conexión con credenciales guardadas; si falla, inicia AP"""
        # Desconectar STA si está conectado
        if self.wlan_sta.isconnected():
            print("Ya conectado a WiFi.")
            return True

        # Intentar conectar con credenciales guardadas
        profiles = self.read_credentials()
        for ssid, password in profiles.items():
            if self.wifi_connect(ssid, password):
                return True

        # Si falla, iniciar modo AP
        print("Conexión fallida. Iniciando Access Point...")
        self.wlan_sta.disconnect()
        sleep(1)

        # Iniciar AP y servidor web para configuración
        if not self.start_ap():
            print("Error al iniciar AP.")
            return False
        self.setup_web_server()
        print(f"\nConéctate a '{self.ap_ssid}' y abre http://{self.wlan_ap.ifconfig()[0]} en tu navegador.")

        # Bucle de servidor web
        while True:
            try:
                self.handle_client_connection()
            except Exception as e:
                print(f"Error en manejo de conexión: {e}")
                sleep(1)

    def start_ap(self):
        """Inicia el Access Point para la configuración"""
        self.wlan_ap.active(False)  # Desactivar cualquier AP previo
        sleep(1)
        self.wlan_ap.active(True)
        self.wlan_ap.config(
            essid=self.ap_ssid,
            password=self.ap_password,
            authmode=self.ap_authmode,
            channel=11
        )
        
        # Confirmar que el AP esté activo
        if self.wlan_ap.active():
            print(f"AP activo en {self.wlan_ap.ifconfig()[0]}")
            return True
        return False

    def setup_web_server(self):
        """Configura el servidor web en el AP"""
        if self.server_socket:
            self.server_socket.close()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Intentar enlazar al puerto 80 (puerto HTTP)
        try:
            self.server_socket.bind(('', 80))
            self.server_socket.listen(1)
            self.server_socket.settimeout(10)  # Aumentar tiempo de espera
            print("Servidor web activo en el puerto 80.")
            return True
        except Exception as e:
            print(f"Error configurando servidor web: {e}")
            return False

    def handle_client_connection(self):
        """Manejo de conexión entrante en el servidor web"""
        conn, addr = self.server_socket.accept()
        conn.settimeout(10)
        request = conn.recv(1024).decode()

        # Extraer URL
        url = re.search('(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP', request)
        if url:
            url = url.group(1).rstrip('/')
            if url == '':  # Página raíz
                self.handle_root(conn)
            elif url == 'configure':  # Configuración de WiFi
                self.handle_configure(conn, request,addr)
            else:
                self.send_response(conn, "Página no encontrada", 404)
        conn.close()

    def handle_root(self, conn):
        """Genera y envía la página principal HTML para elegir WiFi"""
        networks = self.wlan_sta.scan()
        html_content = """
          <!DOCTYPE html>
            <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        .network-item { padding: 10px; margin: 5px 0; border: 1px solid #ddd; }
                        .signal-strength { float: right; }
                        .stats { margin: 20px 0; padding: 10px; background: #f5f5f5; }
                    </style>
                    <title>Conector WIFI</title></head>
                <body>
                    <h2>Redes WiFi disponibles</h2>
                     
                    <form action="/configure" method="post">
        """
        for ssid, bssid, channel, rssi, authmode, hidde in networks:
            ssid = ssid.decode('utf-8')
            signal_strength = min(100, max(0, int((rssi + 100) * 2)))
          #  html_content += f'<input type="radio" name="ssid" value="{ssid}"> {ssid}<br>'
            html_content += f'<div class="network-item"><input type="radio" name="ssid" value="{ssid}" id="{ssid}"><label for="{ssid}">{ssid}</label><span class="signal-strength">Signal: {signal_strength}%</span></div>'

        html_content += """
                        <p>Contraseña: <input type="password" name="password"></p>
                        <p><input type="submit" value="Conectar"></p>
                    </form>
                    </body>
            </html>
        """
        self.send_response(conn, html_content)

    def handle_configure(self, conn, request,addr):
        """Manejo de la configuración con protección contra intentos fallidos"""
        client_ip = str(addr)
        if client_ip in self.failed_attempts and self.failed_attempts[client_ip] >= 5:
            self.send_response(conn, "Demasiados intentos fallidos. Intenta más tarde.", 403)     

        """Extrae y guarda las credenciales de la solicitud POST"""
        match_ssid = re.search(r'ssid=([^&]+)', request)
        match_password = re.search(r'password=([^&]*)', request)
        if match_ssid:
            ssid = match_ssid.group(1)
            password = match_password.group(1) if match_password else ""
            print(f"Recibido SSID: {ssid} y contraseña: {password}")
            if self.wifi_connect(ssid, password):
                # Guardar y probar conexión
                self.write_credentials({ssid: password})
                self.send_response(conn, "Conectado exitosamente.")
            else:
                 # Si hay un fallo de autenticación:
                self.send_response(conn, "Error de conexión. Verifica tus credenciales.")
                self.failed_attempts[client_ip] = self.failed_attempts.get(client_ip, 0) + 1
        else:
            self.send_response(conn, "SSID no válido.", 400)
 
 

    def send_response(self, conn, content, status_code=200):
        """Envía una respuesta HTTP"""
        response = f"HTTP/1.1 {status_code} OK\r\nContent-Type: text/html\r\n\r\n{content}"
        conn.send(response.encode())

    def wifi_connect(self, ssid, password, max_retries=3):
        """Intento de conexión a WiFi con limitación de intentos"""
        for attempt in range(max_retries):
            print(f"Intentando conectar a {ssid}, intento {attempt + 1}/{max_retries}")
            self.wlan_sta.connect(ssid, password)
            start_time = time()
            while time() - start_time < self.connection_timeout:
                if self.wlan_sta.isconnected():
                    print(f"\nConectado a WiFi: {ssid}")
                    print("Configuración de red:", self.wlan_sta.ifconfig())
                    return self.wlan_sta.ifconfig()[0]
                sleep(0.5)

            # Desconectar si falla y esperar antes del próximo intento
            self.wlan_sta.disconnect()
            print(f"Intento fallido {attempt + 1}/{max_retries}. Esperando antes de reintentar...")
            sleep(2)

        print("Conexión fallida después de múltiples intentos.")
        return False

    def read_credentials(self):
        """Lee credenciales guardadas desde el archivo JSON"""
        try:
            with open(self.wifi_credentials, 'rb') as file:
                encrypted = file.read()
            return self._decrypt_credentials(encrypted)
        except:
            return {}

    def write_credentials(self, profiles):
        """Guarda credenciales en un archivo JSON"""
        encrypted = self._encrypt_credentials(profiles)
        with open(self.wifi_credentials, 'wb') as file:
            file.write(encrypted)
            
  