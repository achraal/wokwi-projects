import machine
import time
import dht
import ssd1306

# ─────────── INITIALISATION DES PINS ───────────

# Capteur Ultrason HC-SR04
TRIG = machine.Pin(5, machine.Pin.OUT)
ECHO = machine.Pin(18, machine.Pin.IN)

# Capteur DHT22
capteur_dht = dht.DHT22(machine.Pin(4))

# I2C pour l'Ecran OLED (SDA=8, SCL=9)
i2c = machine.SoftI2C(scl=machine.Pin(9), sda=machine.Pin(8), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Actionneurs : LED et Buzzer
led_alerte = machine.Pin(1, machine.Pin.OUT)
# On utilise le PWM sur la Pin 19 pour l'aide au stationnement
buzzer = machine.PWM(machine.Pin(19))
buzzer.freq(1000)
buzzer.duty(0)

# Seuils
SEUIL_TEMP = 30.0
SEUIL_HUM = 70.0

# ─────────── FONCTIONS ───────────

def mesurer_distance():
    TRIG.value(0)
    time.sleep_us(2)
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)
    try:
        duree = machine.time_pulse_us(ECHO, 1, 30000)
        if duree < 0: return -1
        return (duree * 0.0343) / 2
    except:
        return -1

def lire_meteo():
    try:
        capteur_dht.measure()
        return capteur_dht.temperature(), capteur_dht.humidity()
    except:
        return None, None

def biper_stationnement(dist):
    """Gère le buzzer pour la distance (prioritaire sur l'alerte météo)"""
    if dist < 0 or dist > 80:
        buzzer.duty(0)
        return False # Pas de bip actif

    if dist < 10:
        buzzer.duty(512) # Continu
    elif dist < 20:
        buzzer.duty(512); time.sleep(0.05); buzzer.duty(0)
    elif dist < 40:
        buzzer.duty(512); time.sleep(0.1); buzzer.duty(0)
    elif dist < 80:
        buzzer.duty(512); time.sleep(0.1); buzzer.duty(0)
    return True

def mettre_a_jour_oled(temp, hum, dist):
    oled.fill(0)
    oled.text("SSTATION MULTI", 10, 0)
    oled.hline(0, 10, 128, 1)
    
    # Affichage Météo
    if temp is not None:
        oled.text("T:{}C H:{}%".format(temp, hum), 0, 18)
    else:
        oled.text("Erreur DHT22", 0, 18)
        
    # Affichage Distance
    if dist >= 0:
        oled.text("Dist: {:.1f} cm".format(dist), 0, 35)
        status = "STOP!" if dist < 10 else "Parking..."
        oled.text(status, 0, 50)
    else:
        oled.text("Dist: Erreur", 0, 35)
        
    oled.show()

# ─────────── BOUCLE PRINCIPALE ───────────
print("Système Fusionné Démarré")
derniere_lecture_meteo = 0

while True:
    # 1. Mesure de distance (très fréquent)
    distance = mesurer_distance()
    
    # 2. Lecture météo (toutes les 2 secondes seulement pour ne pas bloquer)
    maintenant = time.time()
    if maintenant - derniere_lecture_meteo >= 2:
        t, h = lire_meteo()
        derniere_lecture_meteo = maintenant
        
        # Gestion LED Alerte Météo
        if t is not None and (t > SEUIL_TEMP or h > SEUIL_HUM):
            led_alerte.value(1)
        else:
            led_alerte.value(0)
            
        # Mise à jour de l'écran
        mettre_a_jour_oled(t, h, distance)

    # 3. Gestion du bip sonore
    biper_stationnement(distance)
    
    # Petite pause pour la stabilité
    time.sleep(0.1)