from conector_wifi import ConectorWIFI
import socket
import re
import select
from time import sleep, ticks_ms, ticks_diff
from machine import Pin

class CaptivePortal:
    def __init__(self, ap_ssid='ESP32-AP', ap_password='password'):
        self.wifi = ConectorWIFI(ap_ssid, ap_password)
        self.dns_socket = None
        self.poller = select.poll()
        self.led = Pin(2, Pin.OUT)  # Usamos el pin 2 para el LED (puede variar según tu ESP32)

    def start_dns_server(self):
        try:
            self.dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dns_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.dns_socket.bind(('', 53))
            self.dns_socket.setblocking(False)
            self.poller.register(self.dns_socket, select.POLLIN)
            return True
        except Exception as e:
            print(f"Error DNS: {e}")
            return False

    def handle_dns_request(self):
        try:
            if self.dns_socket is None:
                return
            
            events = self.poller.poll(100)  # Poll for 100ms
            for sock, _ in events:
                if sock == self.dns_socket:
                    request, addr = self.dns_socket.recvfrom(1024)
                    response = b'\x81\x80' + request[2:4] + b'\x00\x01\x00\x01\x00\x00\x00\x00' + \
                              request[12:] + b'\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x0a\x00\x04' + \
                              bytes(map(int, self.wifi.wlan_ap.ifconfig()[0].split('.')))
                    self.dns_socket.sendto(response, addr)
        except Exception as e:
            print(f"Error DNS handler: {e}")


    def get_led_control_html(self):
        led_status = "Encendido" if self.led.value() else "Apagado"
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ESP32 LED Control</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial; margin: 0; padding: 20px; background: #f0f0f0; }}
                .container {{ max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; }}
                .button {{ display: inline-block; padding: 10px 20px; font-size: 18px; cursor: pointer; text-align: center; text-decoration: none; outline: none; color: #fff; background-color: #4CAF50; border: none; border-radius: 15px; box-shadow: 0 9px #999; }}
                .button:hover {{background-color: #3e8e41}}
                .button:active {{ background-color: #3e8e41; box-shadow: 0 5px #666; transform: translateY(4px); }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>ESP32 LED Control</h1>
                <p>Estado actual del LED: {led_status}</p>
                <form action="/led" method="post">
                    <input type="submit" class="button" value="Cambiar estado del LED">
                </form>
            </div>
        </body>
        </html>
        """

    def handle_web_request(self, conn):
        try:
            request = b""
            start_time = ticks_ms()
            while ticks_diff(ticks_ms(), start_time) < 3000:  # 3 second timeout
                if self.poller.poll(100):  # Poll for 100ms
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    request += chunk
                    if b"\r\n\r\n" in request:
                        break
            
            request = request.decode()
            
            if "captive.apple.com" in request or "connectivitycheck" in request:
                response = "HTTP/1.1 302 Found\r\n"
                response += f"Location: http://{self.wifi.wlan_ap.ifconfig()[0]}\r\n\r\n"
                conn.send(response.encode())
            elif "POST /configure" in request:
                self.handle_configure(conn, request)
            elif "POST /led" in request:
                self.handle_led_control(conn)
            else:
                self.wifi.send_response(conn, self.get_led_control_html())
        except Exception as e:
            print(f"Error manejando petición web: {e}")
        finally:
            conn.close()

    def handle_led_control(self, conn):
        self.led.value(not self.led.value())  # Cambiar el estado del LED
        self.wifi.send_response(conn, self.get_led_control_html())

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

        self.wifi.server_socket.setblocking(False)
        self.poller.register(self.wifi.server_socket, select.POLLIN)

        while True:
            try:
                self.handle_dns_request()
                
                events = self.poller.poll(100)  # Poll for 100ms
                for sock, _ in events:
                    if sock == self.wifi.server_socket:
                        conn, addr = self.wifi.server_socket.accept()
                        conn.setblocking(False)
                        self.handle_web_request(conn)
            except Exception as e:
                print(f"Error en el bucle principal: {e}")
            
            sleep(0.1)

# Uso
def main():
    portal = CaptivePortal()
    portal.run()

if __name__ == "__main__":
    main()