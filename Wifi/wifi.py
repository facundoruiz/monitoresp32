
# main.py
from enhanced_wifi_manager.py import EnhancedWifiManager
import machine

def main():
    try:
        # ACCESS POINT - instancia  con debug para ver mensajes 
        wifi = EnhancedWifiManager(
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
            # machine.reset()
    except Exception as e:
        print(f"Error: {e}")
        machine.reset()

if __name__ == '__main__':
    main()