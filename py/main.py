# Codigo : https://raw.githubusercontent.com/ComputadorasySensores/Capitulo45/refs/heads/main/main.py

import machine, network, time, urequests
from machine import Pin, I2C
from time import sleep
import json
import random

# Credenciales WIFI
ssid = ''
password = ''

# Credenciales Firebase
firebase_url = ''
firebase_key = ''

# Configurar el pin GPIO 2 como salida (LED incorporado)
led = Pin(2, Pin.OUT)




red = network.WLAN(network.STA_IF)

red.active(True)
red.connect(ssid, password)


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

while True:
    try:
        if (time.time() - ultima_peticion) > intervalo_peticiones:
           
            # Datos a enviar
            data = {
                "sensor1": random.randint(0,35),
                "sensor2": 15.5,
                "timestamp": time.time()
            }

            # Convertir los datos a formato JSON
            data_json = json.dumps(data)

            # URL completa para la base de datos
            url = firebase_url + "/entradas.json?auth=" + firebase_key

            # Enviar los datos a Firebase
            response = urequests.post(url, data=data_json)

            # Verificar la respuesta
            if response.status_code == 200:
                led.on()  # Encender el LED
                print("Datos enviados correctamente a Firebase")
                sleep(1)  # Esperar 1 segundo
            else:
                print("Error al enviar datos a Firebase")
                
            led.off()  # Apagar el LED    

            # Cerrar la conexión
            response.close()
            ultima_peticion = time.time()
    except OSError as e:
        reconectar()