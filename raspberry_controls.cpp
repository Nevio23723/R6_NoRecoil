#include <Mouse.h>

// --- EINSTELLUNGEN ---
// Wir nutzen genau 15ms wie im Lua-Skript, damit die Werte passen!
const int PULL_DELAY = 22; 

int currentWeaponID = 0;
unsigned long lastShotTime = 0;

void setup() {
  Serial.begin(115200);
  Mouse.begin();
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Start-Signal: 3x Blinken
  for(int i=0; i<3; i++) {
    digitalWrite(LED_BUILTIN, HIGH); delay(100);
    digitalWrite(LED_BUILTIN, LOW); delay(100);
  }
}

void loop() {
  // 1. Daten empfangen
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    int newID = input.toInt();
    currentWeaponID = newID;

    // LED Status: AN wenn aktiv, AUS wenn inaktiv
    digitalWrite(LED_BUILTIN, (currentWeaponID > 0) ? HIGH : LOW);
  }

  // 2. Recoil ausführen
  if (currentWeaponID > 0) {
    applyRecoil(currentWeaponID);
  }
}

void applyRecoil(int id) {
  if (millis() - lastShotTime < PULL_DELAY) return;
  lastShotTime = millis();

  signed char moveY = 0;
  signed char moveX = 0;

  switch (id) {
    // ==========================================================
    // --- SECONDARIES (PISTOLEN) ---
    // Fast kein Recoil nötig
    // ==========================================================
    case 100: case 102: case 103: case 104: case 105: 
    case 106: case 107: case 108: case 109: case 110:
    case 111: case 112: case 114: case 115: case 116:
    case 117: case 118: case 119: case 120: case 121: 
    case 122: case 126: case 127:
      moveY = 5; moveX = 0;
      break;

    // ==========================================================
    // --- LANGSAME DEFENDER SMGS (UMP-Klasse) ---
    // UMP, C1, M12 - Schiessen sehr langsam
    // ==========================================================
    case 52: // UMP
    case 58: // C1
      moveY = 5; moveX = 0;
      break;

    case 60: // M12
      moveY = 6; moveX = 0;
      break;

    // ==========================================================
    // --- STABILE DEFENDER SMGS (Russian/Lesion) ---
    // 9x19VSN, T-5, Mx4 - Etwas schneller, aber stabil
    // ==========================================================
    case 55: // 9x19VSN
      moveY = 9; moveX = 2;
      break;
    case 62: // T-5
    case 66: // Mx4
    case 69: // UZK
      moveY = 8; moveX = 0;
      break;

    // ==========================================================
    // --- SAS RIFLES (Thatcher/Sledge) ---
    // L85, AR33 - Klassische ARs
    // ==========================================================
    case 1:  // L85
    case 2:  // AR33
      moveY = 14; moveX = 0;
      break;

    // ==========================================================
    // --- HARD HITTERS (Thermite/IQ/Capitao) ---
    // Langsame Feuerrate, hoher Schaden
    // ==========================================================
    case 5:  // 556XI
    case 8:  // 552 Commando
    case 20: // Para-308
    case 24: // SC3000K
      moveY = 14; moveX = 0;
      break;

    // ==========================================================
    // --- LMGs & DRUM MAGS ---
    // Meistens sehr viel Munition, stabiler Recoil
    // ==========================================================
    case 9:  // G8A1
    case 12: // T-95
    case 19: // M249
    case 10: // C7E (Jackal - hier gruppiert wegen ähnlichem Feel)
      moveY = 14; moveX = 0;
      break;

    // ==========================================================
    // --- STANDARD DEFENDER MP5/MPX ---
    // Doc, Rook, Valkyrie - Mittlere RPM
    // ==========================================================
    case 50: // FMG-9
    case 53: // MP5
    case 54: // P90
    case 59: // MPX
    case 67: // AUG A3
    case 68: // P10 Roni
      moveY = 14; moveX = 0;
      break;

    // ==========================================================
    // --- SCHNELLE ARs (Ash G36 / Hibana) ---
    // ==========================================================
    case 4:  // G36C
    case 21: // Type-89
    case 25: // POF-9
    case 16: // Spear
    case 18: // F90
      moveY = 17; moveX = 4;
      break;

    // ==========================================================
    // --- SCHNELLE SMGs (Bandit/Mute) ---
    // Hohe Feuerrate, ziehen schnell hoch
    // ==========================================================
    case 51: // MP5K
    case 57: // MP7
    case 61: // Vector
    case 65: // Alda
    case 56: // 416-C (Jäger)
      moveY = 17; moveX = 4;
      break;

    // ==========================================================
    // --- ASH (R4-C) - SOLO TUNING ---
    // Ash spielt man oft, hier einzeln tunen!
    // ==========================================================
    case 3:  // R4-C
      moveY = 24; moveX = -1;
      break;

    // ==========================================================
    // --- ZOFIA / NOMAD / LION ---
    // Ähnlich wie Ash, aber oft etwas weniger aggressiv
    // ==========================================================
    case 13: // M762
    case 14: // LMG-E
    case 15: // V308
    case 17: // ARX
      moveY = 24; moveX = -1;
      break;

    // ==========================================================
    // --- ACE / FUZE (AK-12) ---
    // AK-12 zieht stark nach rechts oben
    // ==========================================================
    case 7:  // AK-12
      moveY = 20; moveX = 3;
      break;

    // ==========================================================
    // --- BUCK / BLACKBEARD ---
    // C8 hat extremen vertikalen Recoil
    // ==========================================================
    case 22: // C8
    case 23: // MK17
      moveY = 20; moveX = 3;
      break;

    // ==========================================================
    // --- TWITCH (F2) - SOLO TUNING ---
    // F2 ist ein Monster, braucht eigene Werte
    // ==========================================================
    case 6: // F2
      moveY = 34; moveX = 3;
      break;

    // ==========================================================
    // --- ELA (Scorpion) ---
    // Zufalls-Komponente bleibt
    // ==========================================================
    case 63: // Scorpion EVO
      moveY = 15; 
      moveX = (random(0, 10) > 5) ? 2 : -2; 
      break;

    // ==========================================================
    // --- SMG-11 (Smoke/Mute) ---
    // Höchster vertikaler Zug im Spiel
    // ==========================================================
    case 101: // SMG-11
      moveY = 50; moveX = 4;
      break;

    // ==========================================================
    // --- CHAOS SMGs (Dokkaebi/Echo/Clash) ---
    // SMG-12, Bearing-9
    // ==========================================================
    case 113: // Bearing-9
    case 123: // C75
    case 124: // SMG-12
    case 125: // SPSMG
      moveY = 50; moveX = 4;
      break;

    default:
      moveY = 0; moveX = 0;
      break;
  }

  if (moveY != 0 || moveX != 0) {
    Mouse.move(moveX, moveY);
  }
}
