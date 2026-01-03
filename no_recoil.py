import keyboard
import mss
import cv2
import numpy as np
import pytesseract
import time
import serial
import pyautogui
import ctypes 

# --- KONFIGURATION ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# WICHTIG: Prüfe im Geräte-Manager deinen Port!
try:
    ser = serial.Serial('COM4', 115200, timeout=0.01)
    print("Verbunden mit Pico!")
except Exception as e:
    print(f"Fehler beim Verbinden: {e}")
    ser = None

BOX_WIDTH = 250
BOX_HEIGHT = 17

# --- WAFFEN-DATENBANK ---
weapon_db = {
    # === ATTACKER PRIMARY (1-49) ===
    "L85": 1, "AR33": 2, "R4": 3, "G36": 4, "556": 5, "F2": 6, 
    "AK-12": 7, "552": 8, "COMMANDO": 8, "G8": 9, "C7E": 10, 
    "PDW": 11, "T-95": 12, "M762": 13, "LMG-E": 14, "V308": 15, 
    "SPEAR": 16, "ARX": 17, "F90": 18, "M249": 19, "PARA": 20, 
    "TYPE": 21, "C8": 22, "MK17": 23, "SC3000": 24, "POFW": 25, "POF": 25,

    # === DEFENDER PRIMARY (50-99) ===
    "FMG": 50, "MP5K": 51, "UMP": 52, "MP5": 53, "P90": 54, 
    "9X19": 55, "VSN": 55, "416": 56, "MP7": 57, "C1": 58, 
    "MPX": 59, "M12": 60, "VECTOR": 61, "T-5": 62, "SCORPION": 63, 
    "K1A": 64, "ALDA": 65, "MX4": 66, "AUG": 67, "P10": 68, 
    "RONI": 68, "UZK": 69, "9MM": 58,

    # === SECONDARIES (100+) ===
    "P226": 100, "SMG-11": 101, "5.7": 102, "USG": 102, "M45": 103, 
    "P9": 104, "LFP": 105, "GSH": 106, "PMM": 107, "P12": 108, 
    "MK1": 109, "D-50": 110, "PRB": 111, "P229": 112, "BEARING": 113, 
    "USP": 114, "Q-929": 115, "RG15": 116, "BAILIFF": 117, "KERATOS": 118, 
    "1911": 119, "P-10C": 120, "44 MAG": 121, "SDP": 122, "C75": 123, 
    "SMG-12": 124, "SPSMG": 125, "ITA12": 126, "SUPER": 127
}

# --- HILFSFUNKTIONEN ---
def is_left_click_held():
    # 0x01 ist der Code für Linke Maustaste
    return ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000 != 0

def is_right_click_held():
    # 0x02 ist der Code für Rechte Maustaste
    return ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000 != 0

current_weapon_id = 0

print("--- READY ---")
print("1. 'Insert' drücken zum Scannen (Maus unter Name)")
print("2. Aim (Rechts) + Feuer (Links) zum Testen")
print("3. 'Home' zum Beenden")

with mss.mss() as sct:
    while True:
        # 1. SCANNEN (Nur wenn INSERT gedrückt wird)
        if keyboard.is_pressed('insert'):
            mx, my = pyautogui.position()
            roi = {"top": int(my - BOX_HEIGHT), "left": int(mx - BOX_WIDTH/2), "width": BOX_WIDTH, "height": BOX_HEIGHT}
            
            img = np.array(sct.grab(roi))
            img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            _, thresh = cv2.threshold(gray, 195, 255, cv2.THRESH_BINARY_INV)

            try:
                config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-."
                text = pytesseract.image_to_string(thresh, config=config).strip()
                print(f"Scan: '{text}'")

                found_id = 0
                for name in sorted(weapon_db.keys(), key=len, reverse=True):
                    if name in text:
                        found_id = weapon_db[name]
                        print(f"-> Waffe erkannt: {name} (ID {found_id})")
                        break
                
                current_weapon_id = found_id
                
            except:
                pass
            
            time.sleep(0.2) 

        # 2. SCHIESS-LOGIK (JETZT MIT RECHTSKLICK-CHECK)
        if ser:
            # Bedingung: Links gedrückt UND Rechts gedrückt UND Waffe aktiv
            if is_left_click_held() and is_right_click_held() and current_weapon_id > 0:
                msg = f"{current_weapon_id}\n"
                ser.write(msg.encode())
            else:
                ser.write(b"0\n")
        
        # 3. BEENDEN
        if keyboard.is_pressed('home'):
            if ser: ser.write(b"0\n") 
            break
            
        time.sleep(0.01)
