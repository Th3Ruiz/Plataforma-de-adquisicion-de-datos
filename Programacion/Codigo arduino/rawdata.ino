#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <MPU9250_asukiaaa.h>

// --- Configuración Wi-Fi ---
const char* ssid = "pruebas2";
const char* password = "yolo15@A";

// --- Configuración MQTT ---
const char* mqtt_server = "10.194.189.60"; // IP de tu Raspberry Pi
WiFiClient espClient;
PubSubClient client(espClient);

// --- Sensor ---
MPU9250_asukiaaa mpu;

// --- Configuración del Bucle ---
unsigned long lastUpdate = 0;
const unsigned int updateInterval = 100; // 100 ms = 10 Hz

// --- Función de Reconexión MQTT ---
void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando reconexión MQTT...");
    if (client.connect("ESP32_IMU_Client")) {
      Serial.println("reconectado");
    } else {
      Serial.print("falló, rc=");
      Serial.print(client.state());
      Serial.println(" reintentando en 5 segundos");
      delay(5000);
    }
  }
}

// --- SETUP ---
void setup() {
  Serial.begin(115200);
  Wire.begin(27, 26); // Pines SDA, SCL

  mpu.setWire(&Wire);
  mpu.beginAccel();
  mpu.beginGyro();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nWiFi conectado");

  client.setServer(mqtt_server, 1883);
  reconnect(); // Usar la función de reconexión
  
  lastUpdate = millis();
}

// --- LOOP ---
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (millis() - lastUpdate < updateInterval) {
    return;
  }
  lastUpdate = millis();

  mpu.accelUpdate();
  mpu.gyroUpdate();

  // Acelerómetro en 'g's
  float ax = mpu.accelX();
  float ay = mpu.accelY();
  float az = mpu.accelZ();

  // Giroscopio en rad/s (como espera ROS)
  float gx_rad = (mpu.gyroX() ) * DEG_TO_RAD;
  float gy_rad = (mpu.gyroY() ) * DEG_TO_RAD;
  float gz_rad = (mpu.gyroZ() ) * DEG_TO_RAD;

  // JSON simple con datos crudos
  String payload = "{";
  payload += "\"accel\":[" + String(ax, 4) + "," + String(ay, 4) + "," + String(az, 4) + "],";
  payload += "\"gyro\":[" + String(gx_rad, 4) + "," + String(gy_rad, 4) + "," + String(gz_rad, 4) + "]";
  payload += "}";

  client.publish("mpu9250/raw", payload.c_str());
  Serial.println(payload);
}