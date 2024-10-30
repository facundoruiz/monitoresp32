
# main.py
from conector_wifi import ConectorWIFI
import machine

def main():
    try:
        # ACCESS POINT - instancia  con debug para ver mensajes 
        wifi = ConectorWIFI(
            ssid='TestESP32',
            password='password123',
            debug=True
        )
       # Iniciar la conexión WIFI con credenciales
       # wifi.wifi_connect('MI_WIFI_CASA','fdsfsdfsdfsdf',1)
       # wifi.connect() #Intenta conectarse con las claves guardadas, si falla se accede al AP
       # wifi.start_ap() #Crea el Access Point directamente.
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