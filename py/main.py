# Codigo : https://raw.githubusercontent.com/ComputadorasySensores/Capitulo45/refs/heads/main/main.py

import machine, network, time, urequests
from machine import Pin, I2C
from time import sleep
import json

import random

# Credenciales WIFI
WIFI_SSID = ''
WIFI_PASS = ''

# Credenciales Firebase
APP_URL = ""
APP_KEY = ""

# Configurar el pin GPIO 2 como salida (LED incorporado)
led = Pin(2, Pin.OUT)

red = network.WLAN(network.STA_IF)

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
    
# Simular lecturas de sensores
def simular_lecturas():
    temperatura = random.uniform(10, 30)
    humedad = random.uniform(10, 70)
    return json.dumps({ "sensor1": humedad,   "sensor2": temperatura,  "timestamp": time.time() })

# Función para enviar datos a Firebase
def enviar_datos(datos):
    try:
        # Preparar la URL y los headers
        url = APP_URL + 'entradas.json?auth=' + APP_KEY
             
        # Enviar los datos
        response = urequests.post(url,  data=datos)
      
        if response.status_code == 200:
            print("Datos enviados exitosamente")
            return True
        else:
            print(f"Error al enviar datos: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    

while True:
    try:
        if (time.time() - ultima_peticion) > intervalo_peticiones:
           
            # Datos a enviar
            # Convertir los datos a formato JSON
            data_json = simular_lecturas()
           
            response = enviar_datos(data_json)
           
            # Verificar la respuesta
            if response:
                led.on()  # Encender el LED
                sleep(1)  # Esperar 1 segundo
                          
                
            led.off()  # Apagar el LED    

            ultima_peticion = time.time()
    except OSError as e:
        reconectar()
        