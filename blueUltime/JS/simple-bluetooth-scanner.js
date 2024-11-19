// Configuración inicial
const scanButton = document.getElementById('scanButton');
const deviceList = document.getElementById('deviceList');
let isScanning = false;

// Función para formatear los detalles del dispositivo
function getDeviceDetails(device) {
    return {
        name: device.name || 'Dispositivo Desconocido',
        id: device.id,
        connected: device.gatt.connected,
        timestamp: new Date().toLocaleTimeString()
    };
}

        // Función para conectar a un dispositivo
        async function connectToDevice(device) {
            try {
                await device.gatt.connect();
                console.log("Conectado al dispositivo:", device.name);
                // ... acceder a los servicios y características del dispositivo ...
            } catch (error) {
                console.error("Error al conectar:", error);
            }
        }

// Función para mostrar el dispositivo en la lista
function displayDevice(deviceInfo) {
    const deviceElement = document.createElement('div');
    deviceElement.className = 'device-item';
    deviceElement.innerHTML = `
        <h3>${deviceInfo.name}</h3>
        <p>ID: ${deviceInfo.id}</p>
        <p>Estado: ${deviceInfo.connected ? 'Conectado' : 'Desconectado'}</p>
        <p>Detectado: ${deviceInfo.timestamp}</p>
    `;
    deviceList.appendChild(deviceElement);
}

// Función principal de escaneo
async function startBluetoothScan() {
    if (isScanning) return;
    
    try {
        isScanning = true;
        scanButton.textContent = 'Escaneando...';
        
        const device = await navigator.bluetooth.requestDevice({
            acceptAllDevices: true,
            optionalServices: [
                'battery_service',
                'device_information',
                'heart_rate',
                'environmental_sensing'
            ]
        });
        
        const deviceInfo = getDeviceDetails(device);
        displayDevice(deviceInfo);
        
        // Escuchar eventos de conexión/desconexión
        device.addEventListener('gattserverdisconnected', () => {
            console.log(`${device.name} desconectado`);
        });
        
    } catch (error) {
        if (error.name === 'NotFoundError' && error.message.includes('User cancelled')) {
            alert('La selección de dispositivo fue cancelada. Por favor, asegúrate de que el dispositivo Bluetooth esté encendido y detectable.');
          } else {
            console.error('Error durante el escaneo:', error);
            alert(`Error: ${error.message}`);
          }
        } finally {
          isScanning = false;
          scanButton.textContent = 'Iniciar Escaneo';
        }
}

// Verificar soporte de Bluetooth
if (navigator.bluetooth) {
    scanButton.addEventListener('click', startBluetoothScan);
} else {
    scanButton.disabled = true;
    alert('Este navegador no soporta Web Bluetooth API');
}
