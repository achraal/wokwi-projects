# main.py — MicroPython ESP32 + DHT22 → HiveMQ Cloud
import network
import time
import json
from machine import Pin
import dht

from umqtt.simple import MQTTClient
import ssl

# ── WiFi ────────────────────────────────────────────────────
SSID     = "Wokwi-GUEST"
PASSWORD = ""

# ── HiveMQ Cloud ─────────────────────────────────────────────
MQTT_SERVER = "67a6ff59658b49a09a71ebe31994f5cb.s1.eu.hivemq.cloud"
MQTT_PORT   = 8883
MQTT_USER   = "achraf"       # Remplacez par votre username
MQTT_PASS   = "Emsi123456"         # Remplacez par votre password

# ── Topics ──────────────────────────────────────────────────
TOPIC_DATA   = b"emsi/esp32/dht22"
TOPIC_STATUS = b"emsi/esp32/status"
CLIENT_ID    = b"ESP32_Wokwi"

# ── Capteur DHT22 ────────────────────────────────────────────
dht_sensor = dht.DHT22(Pin(15))

# ── Connexion WiFi ───────────────────────────────────────────
def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, PASSWORD)
    print("Connexion WiFi...", end="")
    while not wifi.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\n[WiFi] Connecte :", wifi.ifconfig()[0])

# ── Connexion MQTT avec TLS ──────────────────────────────────
def connect_mqtt():
    client = MQTTClient(
        client_id = CLIENT_ID,
        server    = MQTT_SERVER,  port = MQTT_PORT,
        user      = MQTT_USER, password  = MQTT_PASS,
        keepalive = 60,   ssl       = True,
        ssl_params = {
            "server_hostname": MQTT_SERVER,
            "cert_reqs": ssl.CERT_NONE      # TLS sans vérif. certificat (Wokwi)
        }
    )
    print("[MQTT] Tentative de connexion...")
    client.connect()
    print("[MQTT] Connecte !")
    client.publish(TOPIC_STATUS, b"online", retain=True)
    return client

# ── Programme principal ──────────────────────────────────────
connect_wifi()
client = connect_mqtt()

while True:
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum  = dht_sensor.humidity()

        if temp is not None and hum is not None:
            payload = json.dumps({
                "temperature": round(temp, 1),
                "humidite"   : round(hum, 1)
            })
            client.publish(TOPIC_DATA, payload)
            print("[MQTT] Publie :", payload)

    except Exception as e:
        print("Erreur :", e)

    time.sleep(3)
