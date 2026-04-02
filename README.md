# wokwi-projects
# 🚀 ESP32 IoT Monitoring - HiveMQ Cloud Integration

This project demonstrates the implementation of an IoT monitoring station connected to a Cloud MQTT broker (**HiveMQ**). It uses an **ESP32-S3** programmed with **MicroPython** to collect environmental data and transmit it securely.

## 🛠️ Tech Stack
- **Microcontroller**: ESP32-S3 (Simulated on Wokwi)
- **Language**: MicroPython v1.22.0
- **Sensor**: DHT22 (Temperature & Humidity)
- **Protocol**: MQTT over TCP/IP with **TLS** security layer
- **Cloud Broker**: HiveMQ Cloud (SaaS)

## 📡 Data Workflow
The system follows this lifecycle:
1. Connects to the WiFi network (**Wokwi-GUEST**).
2. Initializes a secure connection with HiveMQ on port **8883**.
3. Reads data from the DHT22 sensor every 3 seconds.
4. Publishes a **JSON** payload to the dedicated topic.

### MQTT Topics
- `emsi/esp32/dht22`: Sensor readings (Temp/Hum).
- `emsi/esp32/status`: Device presence message (Online/Offline).

## 🔧 Setup & Configuration
1. Clone this repository.
2. Ensure the `umqtt.simple` library is present in a `/lib` folder.
3. Update your credentials in `main.py`:
   ```python
   MQTT_USER = "your_username"
   MQTT_PASS = "your_password"
