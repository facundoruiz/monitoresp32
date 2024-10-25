

from network import WLAN,STA_IF
from urequests import post
from machine import ADC,Pin # importamos los módulos machine de ADC y de Pin
from time import sleep,time
from json import dumps
import gc

# Credenciales WIFI
WIFI_SSID = ''
WIFI_PASS = ''

# Credenciales Firebase
APP_URL = ""
APP_KEY = ""
# Datos usuario dentro de firebase
USER_EMAIL = "tu_correo_electronico@gmail.com"
USER_PASS = "tu_contraseña"

potenciometro = ADC(34)  # Definimos el pin que se va a usar como ADC
led = Pin(2,Pin.OUT)
potenciometro.atten(ADC.ATTN_11DB)  # Configuramos el rango de voltaje a 3,6v para tener mayor resolución


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
    sleep(10)

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


intentos_reconexión = 0
max_intentos_reconexión = 5

while True:
    try:
        v = potenciometro.read()
        sleep(1)
        led.off()
        if (v > 100):
            data_json = dumps({"sensor1": v, "sensor2": 0, "timestamp": time()})
            response = enviar_datos(data_json)
            if response:
                led.on()
                sleep(0.5)
                led.off()
    except Exception as e:
        print(f"Error: {str(e)}")
        if intentos_reconexión < max_intentos_reconexión:
            intentos_reconexión += 1
            print(f"Reconectando... (Intento {intentos_reconexión}/{max_intentos_reconexión})")
            sleep(10)
        else:
            print("Demasiados intentos de reconexión. Deteniendo el programa.")
            break

    # Liberar memoria no utilizada
    gc.collect()