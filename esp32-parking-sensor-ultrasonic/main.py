# TP2 — Exercice 2 : HC-SR04 + Buzzer (Aide au stationnement)
# ESP32 / MicroPython

import machine
import time

# ─────────── INITIALISATION ───────────
TRIG = machine.Pin(5, machine.Pin.OUT)
ECHO = machine.Pin(18, machine.Pin.IN)

buzzer = machine.PWM(machine.Pin(19))
buzzer.freq(1000)      # Fréquence 1 kHz
buzzer.duty(0)         # Buzzer éteint au départ


# ─────────── MESURE DISTANCE ───────────
def mesurer_distance_cm():
    # Impulsion TRIG 10µs
    TRIG.value(0)
    time.sleep_us(2)
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    try:
        duree = machine.time_pulse_us(ECHO, 1, 30000)
        if duree < 0:
            return -1
        distance = (duree * 0.0343) / 2
        return distance
    except OSError:
        return -1


# ─────────── GESTION BUZZER ───────────
def biper(dist):
    if dist < 0:
        buzzer.duty(0)
        return

    if dist < 10:
        # Très proche → son continu
        buzzer.duty(512)

    elif dist < 20:
        buzzer.duty(512)
        time.sleep(0.1)
        buzzer.duty(0)
        time.sleep(0.1)

    elif dist < 40:
        buzzer.duty(512)
        time.sleep(0.1)
        buzzer.duty(0)
        time.sleep(0.3)

    elif dist < 80:
        buzzer.duty(512)
        time.sleep(0.1)
        buzzer.duty(0)
        time.sleep(0.8)

    else:
        buzzer.duty(0)


# ─────────── BOUCLE PRINCIPALE ───────────
print("Aide au stationnement démarrée")
print("-" * 35)

while True:

    distance = mesurer_distance_cm()

    if distance < 0:
        print("Erreur : pas de réponse du capteur")
        buzzer.duty(0)
    else:

        if distance < 10:
            zone = "STOP !"
        elif distance < 20:
            zone = "Très proche"
        elif distance < 40:
            zone = "Proche"
        elif distance < 80:
            zone = "Normal"
        else:
            zone = "Loin"

        print("Distance : {:.1f} cm  |  Zone : {}".format(distance, zone))
        biper(distance)

    time.sleep(0.1)