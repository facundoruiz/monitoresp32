# Enhanced WiFi Manager for ESP32
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Platform ESP32](https://img.shields.io/badge/platform-ESP32-blue.svg)
![MicroPython](https://img.shields.io/badge/MicroPython-Latest-green.svg)
[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

Una solución robusta y segura para gestionar conexiones WiFi en dispositivos ESP32 usando MicroPython.

## Características Principales

- 🔒 Almacenamiento seguro de credenciales WiFi
- 📊 Interfaz web responsive para configuración
- 🔄 Reconexión automática y sistema de watchdog
- 📈 Monitoreo de estadísticas de conexión
- 🛡️ Protección contra intentos fallidos
- 📶 Indicador de intensidad de señal

## Requisitos Previos

- ESP32 con MicroPython instalado
- Thonny IDE o herramienta similar para cargar archivos
- Versión mínima de MicroPython: 1.19.1

## Instalación

1. Descarga el archivo `conector_wifi.py`
2. Cárgalo en tu ESP32 usando Thonny IDE o tu herramienta preferida
3. Crea un archivo `main.py` con el código de inicialización

## Uso Básico

```python
# main.py
from conector_wifi import ConectorWIFI

# Configuración básica
wifi = ConectorWIFI(
    ssid='MiESP32',          # Nombre del punto de acceso
    password='password123',   # Contraseña del punto de acceso (mín. 8 caracteres)
    reboot=True,             # Reiniciar después de la configuración
    debug=True               # Mostrar mensajes de depuración
)

# Iniciar la conexión
wifi.connect()
```

## Proceso de Conexión

1. Al iniciar, el dispositivo intentará conectarse a una red WiFi previamente guardada
2. Si no hay redes guardadas o la conexión falla:
   - Se crea un punto de acceso con el SSID y contraseña configurados
   - Conéctate a este punto de acceso desde tu dispositivo
   - Accede a `192.168.4.1` en tu navegador
   - Selecciona tu red WiFi y configura las credenciales

## Configuración Avanzada

```python
wifi = ConectorWIFI(
    ssid='MiESP32',
    password='password123',
    debug=True,
)
```

## Estructura de Archivos
```
/
├── conector_wifi.py    # Clase principal
├── main.py             # Script de inicio
└── wifi.dat.enc        # Archivo de credenciales (generado automáticamente)
```

## Características de Seguridad

- Encriptación de credenciales usando ID único del dispositivo
- Autenticación WPA2-PSK para el punto de acceso
- Seguimiento de intentos fallidos
- Limpieza automática de recursos

## Manejo de Errores

El sistema maneja automáticamente varios escenarios de error:

- Pérdida de conexión WiFi
- Credenciales inválidas
- Timeout de conexión
- Errores de archivo
- Errores de red

## Consejos de Uso

1. **Modo Debug**: Active el modo debug durante el desarrollo para ver mensajes detallados:
   ```python
   wifi = ConectorWIFI(debug=True)
   ```

2. **Limpieza de Recursos**: Use el método `clean_up()` antes de reiniciar o cuando necesite liberar recursos:
   ```python
   wifi.clean_up()
   ```

## Solución de Problemas

1. **No se puede conectar al punto de acceso**
   - Verifique que la contraseña.
   - Asegúrese de estar en rango del dispositivo
   - Intente reiniciar el ESP32

2. **Pérdidas frecuentes de conexión**
   - Verifique la intensidad de la señal
   - Considere usar un repetidor WiFi

3. **Error al guardar credenciales**
   - Verifique permisos de escritura
   - Asegúrese de tener espacio suficiente
   - Intente formatear el sistema de archivos


## Contacto

Facundo Ruiz - [@el_facu](https://x.com/el_facu)


Link del proyecto: [https://github.com/facundoruiz/monitoresp32](https://github.com/facundoruiz/monitoresp32)


# Inspiración
https://github.com/tayfunulu/WiFiManager.git