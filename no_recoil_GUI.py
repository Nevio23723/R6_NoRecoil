import customtkinter as ctk
import serial
import time
import threading
import ctypes

# --- KONFIGURATION ---
COM_PORT = 'COM4' 

# --- OPERATOR DATENBANK ---
# Hier ordnen wir Waffen den Operators zu.
# Format: "Operator": [("Waffe Name", ID), ("Waffe 2", ID)]
operators_db = {
    "ATTACKERS": {
        "Sledge":   [("L85A2", 1), ("SMG-11", 101)],
        "Thatcher": [("L85A2", 1), ("AR33", 2)],
        "Ash":      [("R4-C", 3), ("G36C", 4)],
        "Thermite": [("556XI", 5)],
        "Twitch":   [("F2", 6)],
        "Fuze":     [("AK-12", 7)],
        "Glaz":     [("OTs-03", 0)], # DMRs haben meist ID 0 (kein Recoil nötig)
        "IQ":       [("552 Commando", 8), ("G8A1", 9), ("AUG A2", 67)],
        "Buck":     [("C8-SFW", 22)],
        "Blackbeard":[("MK17 CQB", 23)],
        "Capitao":  [("Para-308", 20), ("M249", 19)],
        "Hibana":   [("Type-89", 21), ("Bearing-9", 113)],
        "Jackal":   [("C7E", 10), ("PDW9", 11), ("ITA12L", 0)],
        "Ying":     [("T-95 LSW", 12)],
        "Zofia":    [("M762", 13), ("LMG-E", 14)],
        "Dokkaebi": [("SMG-12", 124), ("C75", 123)], # Sekundär als Primär nutzen
        "Lion":     [("V308", 15)],
        "Finka":    [("Spear .308", 16)],
        "Maverick": [("M4", 0)], # Falls M4 noch fehlt, ID eintragen
        "Nomad":    [("ARX200", 17), ("AK-74M", 0)],
        "Gridlock": [("F90", 18), ("M249 SAW", 19)],
        "Nokk":     [("FMG-9", 50)],
        "Amaru":    [("G8A1", 9), ("SMG-11", 101)],
        "Kali":     [("SPSMG9", 125)],
        "Iana":     [("G36C", 4), ("ARX200", 17)],
        "Ace":      [("AK-12", 7)],
        "Zero":     [("SC3000K", 24), ("MP7", 57)],
        "Flores":   [("AR33", 2)],
        "Osa":      [("556XI", 5), ("PDW9", 11)],
        "Sens":     [("POF-9", 25)],
        "Grim":     [("552 Commando", 8)],
        "Ram":      [("R4-C", 3), ("LMG-E", 14)]
    },
    "DEFENDERS": {
        "Smoke":    [("FMG-9", 50), ("SMG-11", 101)],
        "Mute":     [("MP5K", 51), ("SMG-11", 101)],
        "Castle":   [("UMP45", 52)],
        "Pulse":    [("UMP45", 52)],
        "Doc":      [("MP5", 53), ("P90", 54)],
        "Rook":     [("MP5", 53), ("P90", 54)],
        "Kapkan":   [("9x19VSN", 55)],
        "Tachanka": [("9x19VSN", 55)],
        "Jäger":    [("416-C", 56)],
        "Bandit":   [("MP7", 57)],
        "Frost":    [("9mm C1", 58)],
        "Valkyrie": [("MPX", 59)],
        "Caveira":  [("M12", 60)],
        "Echo":     [("MP5SD", 53), ("Bearing-9", 113)],
        "Mira":     [("Vector .45", 61)],
        "Lesion":   [("T-5 SMG", 62)],
        "Ela":      [("Scorpion EVO", 63)],
        "Vigil":    [("K1A", 64), ("SMG-12", 124)],
        "Maestro":  [("ALDA 5.56", 65)],
        "Alibi":    [("Mx4 Storm", 66)],
        "Kaid":     [("AUG A3", 67)],
        "Mozzie":   [("P10 Roni", 68), ("Commando 9", 0)],
        "Warden":   [("MPX", 59), ("SMG-12", 124)],
        "Goyo":     [("Vector .45", 61)],
        "Wamai":    [("MP5K", 51), ("AUG A2", 67)],
        "Oryx":     [("T-5 SMG", 62)],
        "Melusi":   [("MP5", 53)],
        "Aruni":    [("P10 Roni", 68)],
        "Thunderbird":[("Spear .308", 16)],
        "Thorn":    [("UZK50GI", 69)],
        "Azami":    [("9x19VSN", 55)],
        "Solis":    [("P90", 54), ("SMG-11", 101)],
        "Fenrir":   [("MP7", 57)],
        "Tubarao":  [("MPX", 59)]
    }
}

# Globale Variablen
current_id = 0
current_weapon_name = "Keine"
app_running = True
ser = None

# --- SERIAL SETUP ---
try:
    ser = serial.Serial(COM_PORT, 115200, timeout=0.01)
    print(f"Pico verbunden auf {COM_PORT}")
except:
    print("Kein Pico gefunden (oder Port belegt).")

# --- LOGIC LOOP (Hintergrund) ---
def logic_loop():
    global current_id
    while app_running:
        if ser and current_id > 0:
            # Check Linksklick (0x01) & Rechtsklick (0x02)
            lc = ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000 != 0
            rc = ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000 != 0
            
            if lc and rc:
                ser.write(f"{current_id}\n".encode())
            else:
                ser.write(b"0\n")
        elif ser:
            ser.write(b"0\n")
        time.sleep(0.01)

# --- GUI LOGIK ---
def update_weapon_list(operator_name, team):
    # Lösche alte Buttons
    for widget in weapon_scroll.winfo_children():
        widget.destroy()
    
    # Hole Waffenliste für den Operator
    weapons = operators_db[team][operator_name]
    
    ctk.CTkLabel(weapon_scroll, text=f"Waffen für {operator_name}:", font=("Arial", 14, "bold")).pack(pady=5)

    for w_name, w_id in weapons:
        # Erstelle Button für jede Waffe
        btn = ctk.CTkButton(weapon_scroll, text=w_name, 
                            command=lambda i=w_id, n=w_name: set_weapon(i, n))
        btn.pack(pady=5, padx=10, fill="x")

def set_weapon(w_id, w_name):
    global current_id, current_weapon_name
    current_id = w_id
    current_weapon_name = w_name
    
    if w_id > 0:
        status_lbl.configure(text=f"AKTIV: {w_name}", text_color="#2CC985") # Grün
        debug_lbl.configure(text=f"Sende ID: {w_id}")
    else:
        status_lbl.configure(text="PASSIV (Kein Recoil)", text_color="gray")
        debug_lbl.configure(text="ID: 0")

def on_close():
    global app_running
    app_running = False
    if ser: ser.close()
    app.destroy()

# --- GUI DESIGN ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("R6 Operator Selector")
app.geometry("600x450")

# 1. HEADER
header = ctk.CTkFrame(app, height=50)
header.pack(fill="x", padx=10, pady=5)
status_lbl = ctk.CTkLabel(header, text="Wähle einen Operator", font=("Arial", 18, "bold"))
status_lbl.pack(side="left", padx=20)
debug_lbl = ctk.CTkLabel(header, text="ID: 0", text_color="gray")
debug_lbl.pack(side="right", padx=20)

# 2. MAIN AREA (Tabs)
tabview = ctk.CTkTabview(app)
tabview.pack(fill="both", expand=True, padx=10, pady=5)

tab_atk = tabview.add("ATTACKERS")
tab_def = tabview.add("DEFENDERS")

# Layout innerhalb der Tabs (Links Ops, Rechts Waffen)
# Wir brauchen eine Funktion, um die Tabs zu füllen
def create_op_grid(parent, team_name):
    # Frame für Operators (Links)
    op_frame = ctk.CTkScrollableFrame(parent, width=250, label_text="Operators")
    op_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    # Sortierte Liste der Ops
    ops = sorted(operators_db[team_name].keys())
    
    for op in ops:
        btn = ctk.CTkButton(op_frame, text=op, fg_color="#333333", hover_color="#555555",
                            command=lambda o=op, t=team_name: update_weapon_list(o, t))
        btn.pack(pady=2, padx=5, fill="x")

create_op_grid(tab_atk, "ATTACKERS")
create_op_grid(tab_def, "DEFENDERS")

# 3. WAFFEN AREA (Rechts - Global für beide Tabs sichtbar machen ist schwer, 
# daher machen wir den "Waffenbereich" ausserhalb der Tabs oder in jedem Tab neu.
# Besser: Wir machen ihn rechts neben den Tabview oder nutzen eine dynamische Spalte.)

# KORREKTUR: Wir packen den Tabview nach LINKS und die Waffenliste nach RECHTS in einen Main Container
tabview.pack_forget() # Reset

main_container = ctk.CTkFrame(app)
main_container.pack(fill="both", expand=True, padx=10, pady=5)

# Linke Seite: Tabs für Ops
tabview = ctk.CTkTabview(main_container, width=300)
tabview.pack(side="left", fill="both", padx=5, pady=5)
tab_atk = tabview.add("ATTACKERS")
tab_def = tabview.add("DEFENDERS")
create_op_grid(tab_atk, "ATTACKERS")
create_op_grid(tab_def, "DEFENDERS")

# Rechte Seite: Waffen Liste
weapon_scroll = ctk.CTkScrollableFrame(main_container, label_text="Loadout", width=250)
weapon_scroll.pack(side="right", fill="both", expand=True, padx=5, pady=5)

# Start Message
ctk.CTkLabel(weapon_scroll, text="<-- Wähle Operator", text_color="gray").pack(pady=50)

# Thread starten
t = threading.Thread(target=logic_loop)
t.start()

app.protocol("WM_DELETE_WINDOW", on_close)
app.mainloop()
