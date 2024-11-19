# main.py
from conector_wifi import ConectorWIFI


def main():
    try:
        # ACCESS POINT - instancia  con debug para ver mensajes 
        wifi = ConectorWIFI()
   # Iniciar la conexión AL WIFI si falla se accede al AP
   
 
        # Intentar conectar
        if not wifi.connect():
            print("Error en la conexión WiFi")
            # Opcional: reiniciar el dispositivo
            # machine.reset()
    except Exception as e:
        print(f"Error: {e}")
     

if __name__ == '__main__':
    main()