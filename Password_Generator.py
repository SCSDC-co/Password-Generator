import customtkinter as ctk
from PIL import Image, ImageTk
import os
import random
import string
import json
from tkinter import messagebox

# === Percorso del file di configurazione per memorizzare il tema ===
# === Percorso sicuro dove salvare il config ===
config_dir = os.path.join(os.path.expanduser("~"), ".password_generator")
os.makedirs(config_dir, exist_ok=True)  
config_file = os.path.join(config_dir, "theme_config.json")


# === Stato iniziale dello switch ===
tema_scuro = False

# Funzione per caricare il tema dal file di configurazione
def carica_tema():
    global tema_scuro
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
            tema_scuro = config.get("switch_attivo", False)
            return config.get("tema", "Light")
    return "Light"

# Funzione per salvare il tema nel file di configurazione
def salva_tema(tema):
    with open(config_file, "w") as f:
        json.dump({"tema": tema, "switch_attivo": tema == "Dark"}, f)

# === Imposta tema iniziale ===
ctk.set_appearance_mode(carica_tema())  
ctk.set_default_color_theme("blue")

# Funzione per cambiare il tema
def cambia_tema():
    global tema_scuro
    tema_scuro = not tema_scuro
    nuovo_tema = "Dark" if tema_scuro else "Light"
    ctk.set_appearance_mode(nuovo_tema)
    salva_tema(nuovo_tema)  
    aggiorna_icone()
    aggiorna_colore_footer()

# === Funzione per aggiornare l'icona della finestra ===
def aggiorna_icone():
    if tema_scuro:
        img_ico = os.path.join(os.getcwd(), "assets", "dark_theme.ico")
    else:
        img_ico = os.path.join(os.getcwd(), "assets", "light_theme.ico")

    app.iconbitmap(img_ico)

# === Funzione per cambiare il colore del footer ===
def aggiorna_colore_footer():
    colore = "#FFFFFF" if tema_scuro else "#000000"
    footer_label.configure(text_color=colore)


# === Funzione per generare una password ===
def genera_password(lunghezza, lettere, numeri, simboli):
    caratteri = ""
    if lettere: caratteri += string.ascii_letters
    if numeri: caratteri += string.digits
    if simboli: caratteri += string.punctuation
    if not caratteri: raise ValueError("Seleziona almeno una categoria di caratteri!")
    return ''.join(random.choices(caratteri, k=lunghezza))

# === Funzione di generazione password e aggiornamento dell'output ===
def genera():
    try:
        lunghezza = int(entry_lunghezza.get())
        if lunghezza < 4: raise ValueError("Minimo 4 caratteri")
        password = genera_password(
            lunghezza, check_lettere.get(), check_numeri.get(), check_simboli.get()
        )
        output_var.set(password)
        forza, colore = valuta_forza(password)
        strength_label.configure(text=f"Forza: {forza}", text_color=colore)
        strength_label.pack(pady=(5, 10))
    except ValueError as e:
        messagebox.showerror("Errore", str(e))

# === Funzione per valutare la forza della password ===
def valuta_forza(password):
    score = 0
    if len(password) >= 8: score += 1
    if any(c.islower() for c in password) and any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in string.punctuation for c in password): score += 1
    if score <= 1: return "Debole", "red"
    elif score <= 3: return "Media", "orange"
    return "Forte", "green"

# === Funzione per copiare la password negli appunti ===
def copia_password():
    password = output_var.get()
    if password:
        app.clipboard_clear()
        app.clipboard_append(password)
        messagebox.showinfo("Copiata!", "Password copiata!")

# === Funzione per salvare la password in un file ===
def salva_password():
    password = output_var.get()
    if password:
        path = os.path.join(os.path.expanduser("~/Documents"), "passwords.txt")
        with open(path, "a") as f: 
            f.write(password + "\n")
        messagebox.showinfo("Salvata", f"Salvata in {path}")
    else:
        messagebox.showwarning("Vuota", "Genera prima una password.")

# === GUI ===
app = ctk.CTk()
app.title("Generatore di Password")
app.geometry("500x420")
app.resizable(False, False)

# Inizializza l'icona in base al tema corrente
aggiorna_icone()

# === Header con tre sezioni ===
header_frame = ctk.CTkFrame(app, fg_color="transparent")
header_frame.pack(fill="x", pady=(10, 0), padx=10)

# Sezione sinistra
left_space = ctk.CTkLabel(header_frame, text="", width=100)
left_space.pack(side="left")

# Sezione centrale
center_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
center_frame.pack(side="left", expand=True)

titolo = ctk.CTkLabel(center_frame, text="Generatore di Password", font=("Helvetica", 20, "bold"))
titolo.pack(anchor="center")

# Sezione destra
right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
right_frame.pack(side="right")

theme_switch = ctk.CTkSwitch(right_frame, text="", command=cambia_tema)
theme_switch.pack(anchor="e")
theme_switch.select() if tema_scuro else theme_switch.deselect()  # Imposta lo stato al caricamento

# === Opzioni lunghezza ===
frame_lunghezza = ctk.CTkFrame(app, fg_color="transparent")
frame_lunghezza.pack(pady=5)

ctk.CTkLabel(frame_lunghezza, text="Lunghezza:", font=("Helvetica", 14)).pack(side="left", padx=(0, 10))
entry_lunghezza = ctk.CTkEntry(frame_lunghezza, width=60, font=("Helvetica", 14))
entry_lunghezza.insert(0, "12")
entry_lunghezza.pack(side="left")

# === Checkboxes per lettere, numeri e simboli ===
check_lettere = ctk.CTkCheckBox(app, text="Lettere", font=("Helvetica", 14))
check_numeri = ctk.CTkCheckBox(app, text="Numeri", font=("Helvetica", 14))
check_simboli = ctk.CTkCheckBox(app, text="Simboli", font=("Helvetica", 14))

check_lettere.select()
check_numeri.select()
check_simboli.select()

check_lettere.pack(pady=3)
check_numeri.pack(pady=3)
check_simboli.pack(pady=3)

# === Bottone per generare la password ===
ctk.CTkButton(app, text="🎲 Genera Password", command=genera, font=("Helvetica", 16, "bold"), corner_radius=15).pack(pady=15)

# === Output della password ===
output_var = ctk.StringVar()
ctk.CTkEntry(app, textvariable=output_var, width=300, font=("Helvetica", 14)).pack(pady=(5, 0))
strength_label = ctk.CTkLabel(app, text="", font=("Helvetica", 14, "bold"))

# === Pulsanti per copiare e salvare la password ===
ctk.CTkButton(app, text="📋 Copia Password", command=copia_password, font=("Helvetica", 16, "bold"), corner_radius=15).pack(pady=10)
ctk.CTkButton(app, text="💾 Salva Password", command=salva_password, font=("Helvetica", 16, "bold"), corner_radius=15).pack(pady=10)

# === Footer con copyright ===
footer_label = ctk.CTkLabel(
    app,
    text="© 2025 SCSDC. Tutti i diritti riservati",
    font=("Helvetica", 12, "italic")
)
footer_label.place(relx=0.5, rely=1, anchor="s")
aggiorna_colore_footer()

# === Avvio dell'app ===
app.mainloop()
