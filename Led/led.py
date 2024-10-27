from network import WLAN,STA_IF
from urequests import post
from machine import Pin
from time import sleep,time
from json import dumps
import random

# Credenciales WIFI
WIFI_SSID = ""
WIFI_PASS = ""

# Credenciales Firebase
APP_URL = ""
APP_KEY = ""
# Datos usuario dentro de firebase
USER_EMAIL = ""
USER_PASS = ""

# Configurar el pin GPIO 2 como salida (LED incorporado)
led = Pin(2, Pin.OUT)

red = WLAN(STA_IF)

red.active(True)
red.connect(WIFI_SSID, WIFI_PASS)

while red.isconnected() == False:
  pass

print('Conexión correcta')
print(red.ifconfig())

ultima_peticion = 0
intervalo_peticiones = 30

def reconectar():
    print('Fallo de conexión. Reconectando...')
    time.sleep(10)
    machine.reset()
 
def autenticar():
    try:
        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + APP_KEY
        data = {
            "email": USER_EMAIL,
            "password": USER_PASS,
            "returnSecureToken": True
        }
        headers = {"Content-Type": "application/json"}
        response = post(url, data=dumps(data), headers=headers)
        if response.status_code == 200:
            token_id = response.json()["idToken"]
            refresh_token = response.json()["refreshToken"]
            return token_id, refresh_token
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error de autenticación: {str(e)}")
        return None, None
       
# Simular lecturas de sensores
def simular_lecturas():
    temperatura = random.uniform(10, 30)
    humedad = random.uniform(10, 70)
    return dumps({ "sensor1": humedad,   "sensor2": temperatura,  "timestamp": time() })

# Función para enviar datos a Firebase
def enviar_datos(datos):
    try:
        token_id, refresh_token = autenticar()
        if token_id is None:
            print("Autenticación fallida")
            exit()

        url = APP_URL + 'entradas.json?auth=' + token_id
        headers = {"Authorization": f"Bearer {token_id}"}
        # Enviar los datos
        response = post(url, data=datos, headers=headers, timeout=10)
       
              
        if response.status_code != 200:
          raise Exception(f"Error {response.status_code}: {response.text}")
        return True
    except OSError as e:
        print(f"Error de conexión: {str(e)}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    

while True:
    try:
        if (time() - ultima_peticion) > intervalo_peticiones:
           
            # Datos a enviar
            # Convertir los datos a formato JSON
            data_json = simular_lecturas()
           
            response = enviar_datos(data_json)
           
            # Verificar la respuesta
            if response:
                led.on()  # Encender el LED
                sleep(1)  # Esperar 1 segundo
                          
                
            led.off()  # Apagar el LED    

            ultima_peticion = time()
    except OSError as e:
        reconectar()