import dht
import machine
import ssd1306
import time

# ── Initialisation des périphériques ──

# Capteur DHT22 sur Pin 4 (OK avec JSON)
capteur_dht = dht.DHT22(machine.Pin(4)) 

# I2C : Doit correspondre au JSON (SDA=8, SCL=9)
i2c = machine.SoftI2C(
    scl=machine.Pin(9), 
    sda=machine.Pin(8), 
    freq=400_000
)

oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# LED : Doit correspondre au JSON (Pin 1)
led = machine.Pin(1, machine.Pin.OUT)

# Optionnel : Initialisation du Buzzer (Pin 5 dans le JSON)
buzzer = machine.Pin(5, machine.Pin.OUT)

SEUIL_TEMP = 30.0
SEUIL_HUM = 70.0

def lire_dht22():
    try:
        capteur_dht.measure()
        return capteur_dht.temperature(), capteur_dht.humidity()
    except OSError as e:
        print(f"Erreur DHT22 : {e}")
        return None, None

def afficher_oled(temp, hum, alerte):
    oled.fill(0)
    oled.text("=== Station IoT ===", 0, 0)
    oled.hline(0, 10, 128, 1)
    
    if temp is not None:
        oled.text("Temp : {:.1f} C".format(temp), 0, 16)
        oled.text("Hum  : {:.1f} %".format(hum), 0, 28)
    else:
        oled.text("Erreur capteur", 0, 16)
    
    oled.hline(0, 42, 128, 1)
    
    if alerte:
        oled.text("!! ALERTE !!", 20, 50)
    else:
        oled.text("Etat : Normal", 0, 50)
    
    oled.show()

print('Station météo IoT démarrée (ESP32-S3)')
print('-' * 35)

while True:
    temp, hum = lire_dht22()
    
    if temp is not None:
        alerte = (temp > SEUIL_TEMP) or (hum > SEUIL_HUM)
        
        # Actionneur LED
        led.value(1 if alerte else 0)
        
        # Actionneur Buzzer (Simple ON/OFF)
        buzzer.value(1 if alerte else 0)
        
        print(f'Temp={temp:.1f}C Hum={hum:.1f}% Alerte={alerte}')
        afficher_oled(temp, hum, alerte)
    else:
        led.value(0)
        buzzer.value(0)
        afficher_oled(None, None, False)
        
    time.sleep(2)