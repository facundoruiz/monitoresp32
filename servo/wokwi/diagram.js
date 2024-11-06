{
  "version": 1,
  "author": "Mohit Uzumaki",
  "editor": "wokwi",
  "parts": [
    {
      "type": "board-esp32-devkit-v1",
      "id": "esp",
      "top": 26.08,
      "left": -43.2,
      "attrs": { "env": "micropython-20231227-v1.22.0" }
    },
    { "type": "wokwi-servo", "id": "servo1", "top": 199.6, "left": 182.4, "attrs": {} },
    {
      "type": "wokwi-buzzer",
      "id": "bz1",
      "top": -26.4,
      "left": 261,
      "attrs": { "volume": "0.1" }
    },
    {
      "type": "wokwi-pir-motion-sensor",
      "id": "pir1",
      "top": -72.8,
      "left": -132.18,
      "attrs": {}
    }
  ],
  "connections": [
    [ "esp:TX", "$serialMonitor:RX", "", [] ],
    [ "esp:RX", "$serialMonitor:TX", "", [] ],
    [ "servo1:GND", "esp:GND.1", "black", [ "h-86.4", "v-76.8" ] ],
    [ "servo1:V+", "esp:3V3", "red", [ "h0" ] ],
    [ "bz1:1", "esp:GND.1", "black", [ "v0" ] ],
    [ "bz1:2", "esp:D21", "red", [ "v28.8", "h-240.4" ] ],
    [ "pir1:GND", "esp:GND.2", "black", [ "v0" ] ],
    [ "pir1:VCC", "esp:VIN", "red", [ "v0" ] ],
    [ "pir1:OUT", "esp:D34", "green", [ "v0" ] ],
    [ "esp:D33", "servo1:PWM", "green", [ "h-28.8", "v163" ] ]
  ],
  "dependencies": {}
}