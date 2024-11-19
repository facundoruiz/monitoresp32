from conector_wifi import ConectorWIFI
import socket
import re
from time import sleep

class CaptivePortal:
    def __init__(self, ap_ssid='Wifi-FREE', ap_password='password'):
        self.wifi = ConectorWIFI(ap_ssid, ap_password)
        self.dns_socket = None

    def start_dns_server(self):
        try:
            self.dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dns_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.dns_socket.bind(('', 53))
            return True
        except Exception as e:
            print(f"Error DNS: {e}")
            return False

    def handle_dns_request(self):
        try:
            if self.dns_socket is None:
                return
            
            self.dns_socket.settimeout(0.1)
            try:
                request, addr = self.dns_socket.recvfrom(1024)
                response = b'\x81\x80' + request[2:4] + b'\x00\x01\x00\x01\x00\x00\x00\x00' + \
                          request[12:] + b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x0a\x00\x04' + \
                          bytes(map(int, self.wifi.wlan_ap.ifconfig()[0].split('.')))
                self.dns_socket.sendto(response, addr)
            except socket.timeout:
                pass
        except Exception as e:
            print(f"Error DNS handler: {e}")

    def get_html_content(self):
        networks = self.wifi.wlan_sta.scan()
        options = ''.join([f'<option value="{ssid.decode()}">{ssid.decode()} ({abs(rssi)}dBm)</option>'
                           for ssid, _, _, rssi, _, _ in networks])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ESP32 WiFi Config</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial; margin: 0; padding: 20px; background: #f0f0f0; }}
                .container {{ max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; }}
                select, input {{ width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }}
                input[type="submit"] {{ background-color: #4CAF50; color: white; border: none; cursor: pointer; }}
                input[type="submit"]:hover {{ background-color: #45a049; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>ESP32 WiFi Configuration</h1>
                <form action="/configure" method="post">
                    <select name="ssid" required>
                        <option value="">Select WiFi Network</option>
                        {options}
                    </select>
                    <input type="password" name="password" placeholder="WiFi Password" required>
                    <input type="submit" value="Connect">
                </form>
            </div>
        </body>
        </html>
        """

    def handle_web_request(self, conn, request):
        try:
            if "captive.apple.com" in request or "connectivitycheck" in request:
                response = "HTTP/1.1 302 Found\r\n"
                response += f"Location: http://{self.wifi.wlan_ap.ifconfig()[0]}\r\n\r\n"
                conn.send(response.encode())
            elif "POST /configure" in request:
                self.handle_configure(conn, request)
            else:
                self.wifi.send_response(conn, self.get_html_content())
        except Exception as e:
            print(f"Error manejando petición web: {e}")
        finally:
            conn.close()

    def handle_configure(self, conn, request):
        match_ssid = re.search(r'ssid=([^&]+)', request)
        match_password = re.search(r'password=([^&]*)', request)
        if match_ssid and match_password:
            ssid = match_ssid.group(1)
            password = match_password.group(1)
            if self.wifi.wifi_connect(ssid, password):
                response = "Conectado exitosamente a WiFi. El ESP32 se reiniciará."
                self.wifi.send_response(conn, response)
                sleep(2)
                import machine
                machine.reset()
            else:
                response = "Error de conexión. Verifica tus credenciales."
                self.wifi.send_response(conn, response)
        else:
            self.wifi.send_response(conn, "SSID o contraseña no válidos.", 400)

    def run(self):
        self.wifi.show_message("Iniciando Portal")
        ap_ip = self.wifi.start_ap()
        if not ap_ip:
            self.wifi.show_message("Error AP")
            return

        if not self.start_dns_server():
            self.wifi.show_message("Error DNS")
            return

        if not self.wifi.setup_web_server():
            self.wifi.show_message("Error Web")
            return

        self.wifi.show_message("Portal Activo")
        self.wifi.show_message(f"SSID:{self.wifi.ap_ssid}", line=1)
        self.wifi.show_message(f"IP:{ap_ip}", line=2)

        while True:
            try:
                self.handle_dns_request()
                
                self.wifi.server_socket.settimeout(0.1)
                try:
                    conn, addr = self.wifi.server_socket.accept()
                    conn.settimeout(3.0)
                    request = conn.recv(1024).decode()
                    self.handle_web_request(conn, request)
                except socket.timeout:
                    pass
            except Exception as e:
                if 'ETIMEDOUT' not in str(e):
                    print(f"Error en el bucle principal: {e}")
            
            sleep(0.1)

# Uso
def main():
    portal = CaptivePortal()
    portal.run()

if __name__ == "__main__":
    main()