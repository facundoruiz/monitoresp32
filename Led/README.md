# Encender LEd
==========================================

![imagen](led.png)

## Práctica: Usar el Led de ESP32

Esta práctica tiene como objetivo aprender a utilizar un LED en un módulo ESP32.

<video width="320" height="240" controls>
  <source src="./video.mp4" type="video/mp4">
</video>

## Material Consultado

* [Código de Conexión](https://raw.githubusercontent.com/ComputadorasySensores/Capitulo45/refs/heads/main/main.py)
* [Firebase Authentication](https://www.telerik.com/blogs/firebase-authentication-using-custom-token)
* [ESP32 y Firebase](https://medium.com/firebase-developers/getting-started-with-esp32-and-firebase-1e7f19f63401)

## Código de Ejemplo

```python
import machine

# Configuración del pin del LED
led_pin = machine.Pin(2, machine.Pin.OUT)

# Encender el LED
led_pin.value(1)

# Apagar el LED
led_pin.value(0)
