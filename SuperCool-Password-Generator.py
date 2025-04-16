import customtkinter as ctk
from tkinter import messagebox
import os
import random
import string
import json
from tkinter.simpledialog import askstring

# === Percorso sicuro ===
config_dir = os.path.join(os.path.expanduser("~"), ".password_generator")
os.makedirs(config_dir, exist_ok=True)
config_file = os.path.join(config_dir, "theme_config.json")
json_password_file = os.path.join(config_dir, "passwords.json")
password_utente_file = os.path.join(config_dir, "password_utente.json")

# === Stato tema ===
tema_scuro = False
def carica_tema():
    global tema_scuro
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
            tema_scuro = config.get("switch_attivo", False)
            return config.get("tema", "Light")
    return "Light"

def salva_tema(tema):
    with open(config_file, "w") as f:
        json.dump({"tema": tema, "switch_attivo": tema == "Dark"}, f)

ctk.set_appearance_mode(carica_tema())
ctk.set_default_color_theme("blue")

def cambia_tema():
    global tema_scuro
    tema_scuro = not tema_scuro
    nuovo_tema = "Dark" if tema_scuro else "Light"
    ctk.set_appearance_mode(nuovo_tema)
    salva_tema(nuovo_tema)
    aggiorna_icone()
    aggiorna_colore_footer()

def aggiorna_icone():
    pass  # Rimosso il codice per l'aggiornamento dell'icona

def aggiorna_colore_footer():
    colore = "#FFFFFF" if tema_scuro else "#000000"
    footer_label.configure(text_color=colore)

def genera_password(lunghezza, lettere, numeri, simboli):
    caratteri = ""
    if lettere: caratteri += string.ascii_letters
    if numeri: caratteri += string.digits
    if simboli: caratteri += string.punctuation
    if not caratteri: raise ValueError("Seleziona almeno una categoria!")
    return ''.join(random.choices(caratteri, k=lunghezza))

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

def valuta_forza(password):
    score = 0
    if len(password) >= 8: score += 1
    if any(c.islower() for c in password) and any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in string.punctuation for c in password): score += 1
    if score <= 1: return "Debole", "red"
    elif score <= 3: return "Media", "orange"
    return "Forte", "green"

def copia_password():
    password = output_var.get()
    if password:
        app.clipboard_clear()
        app.clipboard_append(password)
        messagebox.showinfo("Copiata!", "Password copiata!")

def salva_password():
    password = output_var.get()
    if password:
        if os.path.exists(json_password_file):
            with open(json_password_file, "r") as f:
                data = json.load(f)
        else:
            data = {"passwords": []}
        data["passwords"].append(password)
        with open(json_password_file, "w") as f:
            json.dump(data, f, indent=4)
        messagebox.showinfo("Salvata", "Password salvata nel file JSON!")
    else:
        messagebox.showwarning("Vuota", "Genera prima una password.")

def richiedi_password_visualizzazione():
    if os.path.exists(password_utente_file):
        mostra_finestra_password()
    else:
        imposta_password_iniziale()

def imposta_password_iniziale():
    def salva_password():
        nuova = entry.get()
        if nuova:
            with open(password_utente_file, "w") as f:
                json.dump({"password": nuova}, f)
            messagebox.showinfo("Password impostata", "Password impostata con successo!")
            pw_window.destroy()

    pw_window = ctk.CTkToplevel(app)
    pw_window.title("Imposta password")
    pw_window.geometry("350x100")
    pw_window.resizable(False, False)
    # Rimosso il .iconbitmap(img_ico)

    frame = ctk.CTkFrame(pw_window)
    frame.pack(pady=10, padx=10)

    entry = ctk.CTkEntry(frame, show="*")
    entry.pack(side="left", padx=(0, 5))

    mostra = ctk.CTkButton(frame, text="Mostra", width=40,
                           command=lambda: toggle_password(entry, mostra))
    mostra.pack(side="left")

    ctk.CTkButton(pw_window, text="OK", command=salva_password).pack(pady=5)
    centra_finestra(pw_window)  # Centra la finestra

def mostra_finestra_password():
    pw_window = ctk.CTkToplevel(app)
    pw_window.title("Inserisci password")
    pw_window.geometry("350x100")
    pw_window.resizable(False, False)
    # Rimosso il .iconbitmap(img_ico)

    def verifica():
        inserita = entry.get()
        if not inserita: return
        with open(password_utente_file, "r") as f:
            password_salvata = json.load(f)["password"]
        if inserita == password_salvata:
            pw_window.destroy()
            visualizza_passwords()
        else:
            messagebox.showerror("Errore", "Password errata!")

    frame = ctk.CTkFrame(pw_window)
    frame.pack(pady=10, padx=10)

    entry = ctk.CTkEntry(frame, show="*")
    entry.pack(side="left", padx=(0, 5))

    mostra = ctk.CTkButton(frame, text="Mostra", width=40,
                           command=lambda: toggle_password(entry, mostra))
    mostra.pack(side="left")

    ctk.CTkButton(pw_window, text="OK", command=verifica).pack(pady=5)
    centra_finestra(pw_window)  # Centra la finestra

def toggle_password(entry, button):
    if entry.cget("show") == "":
        entry.configure(show="*")
        button.configure(text="Mostra")
    else:
        entry.configure(show="")
        button.configure(text="Nascondi")

def visualizza_passwords():
    if os.path.exists(json_password_file):
        with open(json_password_file, "r") as f:
            data = json.load(f)
        passwords = data.get("passwords", [])

        if passwords:
            pw_win = ctk.CTkToplevel(app)
            pw_win.title("Password Salvate")
            pw_win.geometry("400x400")
            pw_win.resizable(False, False)
            # Rimosso il .iconbitmap(img_ico)

            box = ctk.CTkFrame(pw_win, fg_color="transparent")
            box.pack(fill="both", expand=True, padx=10, pady=10)

            for password in passwords:
                frame = ctk.CTkFrame(box, fg_color="transparent")
                frame.pack(fill="x", pady=5)

                colore_tema = "white" if tema_scuro else "black"

                password_entry = ctk.CTkEntry(frame, state="normal", font=("Helvetica", 14))
                password_entry.insert(0, password)
                password_entry.configure(
                    state="readonly",
                    text_color=colore_tema,
                    fg_color=ctk.CTk().cget("fg_color"),
                    border_width=0,
                    border_color=ctk.CTk().cget("fg_color")
                )
                password_entry.pack(side="left", fill="x", expand=True)
                password_entry.select_range(0, len(password))
            centra_finestra(pw_win)  # Centra la finestra
        else:
            messagebox.showinfo("Nessuna Password", "Nessuna password salvata.")
    else:
        messagebox.showinfo("Nessuna Password", "Nessuna password salvata.")

def centra_finestra(finestra):
    finestra.update_idletasks()
    w = finestra.winfo_width()
    h = finestra.winfo_height()
    x = (finestra.winfo_screenwidth() // 2) - (w // 2)
    y = (finestra.winfo_screenheight() // 2) - (h // 2)
    finestra.geometry(f"+{x}+{y}")

# === GUI Principale ===
app = ctk.CTk()
app.title("Generatore di Password")
app.geometry("500x470")
app.resizable(False, False)

# Header
header_frame = ctk.CTkFrame(app, fg_color="transparent")
header_frame.pack(fill="x", pady=(10, 0), padx=10)

left_space = ctk.CTkLabel(header_frame, text="", width=100)
left_space.pack(side="left")

center_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
center_frame.pack(side="left", expand=True)
titolo = ctk.CTkLabel(center_frame, text="Generatore di Password", font=("Helvetica", 20, "bold"))
titolo.pack(anchor="center")

right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
right_frame.pack(side="right")
theme_switch = ctk.CTkSwitch(right_frame, text="", command=cambia_tema)
theme_switch.pack(anchor="e")
theme_switch.select() if tema_scuro else theme_switch.deselect()

# Input
frame_lunghezza = ctk.CTkFrame(app, fg_color="transparent")
frame_lunghezza.pack(pady=5)
ctk.CTkLabel(frame_lunghezza, text="Lunghezza:", font=("Helvetica", 14)).pack(side="left", padx=(0, 10))
entry_lunghezza = ctk.CTkEntry(frame_lunghezza, width=60, font=("Helvetica", 14))
entry_lunghezza.insert(0, "12")
entry_lunghezza.pack(side="left")

# Checkboxes
check_lettere = ctk.CTkCheckBox(app, text="Lettere", font=("Helvetica", 14))
check_numeri = ctk.CTkCheckBox(app, text="Numeri", font=("Helvetica", 14))
check_simboli = ctk.CTkCheckBox(app, text="Simboli", font=("Helvetica", 14))
check_lettere.select()
check_numeri.select()
check_simboli.select()
check_lettere.pack(pady=3)
check_numeri.pack(pady=3)
check_simboli.pack(pady=3)

# Pulsanti
ctk.CTkButton(app, text="🎲 Genera Password", command=genera, font=("Helvetica", 16, "bold")).pack(pady=15)

output_var = ctk.StringVar()
ctk.CTkEntry(app, textvariable=output_var, width=300, font=("Helvetica", 14)).pack(pady=(5, 0))
strength_label = ctk.CTkLabel(app, text="", font=("Helvetica", 14, "bold"))

ctk.CTkButton(app, text="📋 Copia Password", command=copia_password, font=("Helvetica", 16, "bold")).pack(pady=10)
ctk.CTkButton(app, text="💾 Salva Password", command=salva_password, font=("Helvetica", 16, "bold")).pack(pady=10)
ctk.CTkButton(app, text="🔐 Visualizza Password", command=richiedi_password_visualizzazione, font=("Helvetica", 16, "bold")).pack(pady=10)

# Footer
footer_label = ctk.CTkLabel(app, text="© 2025 SCSDC. Tutti i diritti riservati", font=("Helvetica", 12, "italic"))
footer_label.place(relx=0.5, rely=1, anchor="s")
aggiorna_colore_footer()

# Avvio
app.mainloop()