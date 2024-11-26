# Proyecto ESP32 con Conector WIFI y OLED

Este proyecto utiliza un ESP32 para conectarse a redes WiFi y mostrar información en una pantalla OLED. Asegúrate de seguir las instrucciones a continuación para configurar correctamente tu dispositivo.

## Requisitos



- **ESP32**: Un microcontrolador ESP32.
- MicroPython instalado en el ESP32.
- Un LED y una resistencia adecuada.
- **Pantalla OLED**: Una pantalla OLED compatible con el controlador SSD1306.
- **Módulo SSD1306** (opcional): Asegúrate de cargar el módulo `ssd1306` en tu ESP32. Este módulo es necesario para controlar la pantalla OLED desde el código.


## Instalación

1. **Cargar el módulo SSD1306**: Antes de ejecutar el código, debes cargar el módulo `ssd1306` en tu ESP32. Puedes hacerlo utilizando herramientas como `Thonny` para transferir archivos a tu dispositivo.

2. **Subir el código**: Sube los archivos del proyecto al ESP32, asegurándote de incluir todos los scripts necesarios.

3. **Conectar los componentes**: Conecta la pantalla OLED y cualquier otro componente necesario al ESP32 según el esquema de conexiones.

## Uso

Una vez que el módulo SSD1306 esté cargado y el código esté en el ESP32, puedes ejecutar el script principal para iniciar el servidor web y controlar el dispositivo.

## Notas

- Si encuentras un error relacionado con la importación del módulo `ssd1306`, verifica que el módulo esté correctamente cargado en el ESP32.
- Asegúrate de que todos los cables y conexiones estén firmes y correctos.

#Ejemplo de uso
1. Conecta el LED al pin 2 del ESP32.
2. Ejecuta el script `main.py` en el ESP32.
3. Conéctate al punto de acceso creado por el ESP32.
4. Abre un navegador web y accede a la dirección IP del ESP32.
5. Usa la interfaz web para encender o apagar el LED.

## Funciones de la Clase `ConectorWIFI`

| Función                  | Descripción                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `__init__`               | Inicializa la conexión WiFi y la pantalla OLED si está disponible.          |
| `show_message`           | Muestra un mensaje en la consola y en la pantalla OLED.                     |
| `start_dual_mode`        | Inicia el modo dual (AP + STA) y configura el servidor web.                 |
| `connect`                | Intenta conectar con credenciales guardadas o inicia el AP si falla.        |
| `start_ap`               | Inicia el Access Point para la configuración.                               |
| `setup_web_server`       | Configura el servidor web con manejo de timeouts.                           |
| `send_response`          | Envía una respuesta HTTP.                                                   |
| `wifi_connect`           | Intenta conectar a WiFi con limitación de intentos.                         |


## Ejemplo de Uso de `show_message`

Para mostrar un mensaje en la pantalla OLED, puedes usar la función `show_message` de la siguiente manera:

```python
from conector_wifi import ConectorWIFI

# Inicializar la clase ConectorWIFI
wifi = ConectorWIFI()

# Mostrar un mensaje en la pantalla OLED
wifi.show_message("Hola, Mundo!", line=0, clear=True)
```

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
