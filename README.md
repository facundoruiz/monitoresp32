# Monitor frontend muestra datos desde Firebase
------------------------------------------

![Imagen de ejemplo](/Image%202024-10-20%20at%2023.08.49.jpeg)

## Práctica: Conexión ESP32 con Firebase utilizando MicroPython
### Objetivo:
Conectar un ESP32 DevKit1 con Firebase utilizando MicroPython, simular lecturas de sensores y visualizar los datos en una gráfica web.
### Requisitos:
ESP32 DevKit1
MicroPython
Firebase (cuenta gratuita)
Archivo HTML para visualización de datos y plugins (CDN)

## Librerías Python
```cmd

```

## Variables de Entornos
Dashboard
En la carpeta dashboard, hay que crear un archivo env.js e copiar la configuración de Firebase.

Py
Se agregan los datos de wifi y firebase

```code
# Credenciales WIFI
WIFI_SSID = ''
WIFI_PASS = ''

# Credenciales Firebase
APP_URL = ""
APP_KEY = ""
```

## Rule en Firebase
las reglas de la DB de la siguiente manera:

```json
{
  "rules": {
    ".read": true,
    ".write": true,
  }
}
```
Download Node.js v20.18.0
Node.js includes npm (10.8.2).

npm install -g firebase-tools

firebase login


firebase init

"site": "monitoresp32",


firebase deploy --only hosting:monitoresp32


Conclusión:
En esta práctica, se ha demostrado cómo conectar un ESP32 con Firebase utilizando MicroPython, simular lecturas de sensores y visualizar los datos en una gráfica web. Esta combinación de tecnologías permite desarrollar proyectos de IoT de manera efectiva y eficiente.