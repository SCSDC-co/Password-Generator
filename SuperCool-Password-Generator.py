import customtkinter as ctk
from tkinter import messagebox
import os
import random
import string
import json
from tkinter.simpledialog import askstring

# === Secure Path ===
config_dir = os.path.join(os.path.expanduser("~"), ".password_generator")
os.makedirs(config_dir, exist_ok=True)
config_file = os.path.join(config_dir, "theme_config.json")
json_password_file = os.path.join(config_dir, "passwords.json")
user_password_file = os.path.join(config_dir, "user_password.json")

# === Theme State ===
dark_theme = False
def load_theme():
    global dark_theme
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
            dark_theme = config.get("switch_active", False)
            return config.get("theme", "Light")
    return "Light"

def save_theme(theme):
    with open(config_file, "w") as f:
        json.dump({"theme": theme, "switch_active": theme == "Dark"}, f)

ctk.set_appearance_mode(load_theme())
ctk.set_default_color_theme("blue")

def change_theme():
    global dark_theme
    dark_theme = not dark_theme
    new_theme = "Dark" if dark_theme else "Light"
    ctk.set_appearance_mode(new_theme)
    save_theme(new_theme)
    update_icons()
    update_footer_color()

def update_icons():
    pass  # Removed icon update code

def update_footer_color():
    color = "#FFFFFF" if dark_theme else "#000000"
    footer_label.configure(text_color=color)

def generate_password(length, letters, numbers, symbols):
    characters = ""
    if letters: characters += string.ascii_letters
    if numbers: characters += string.digits
    if symbols: characters += string.punctuation
    if not characters: raise ValueError("Select at least one category!")
    return ''.join(random.choices(characters, k=length))

def generate():
    try:
        length = int(entry_length.get())
        if length < 4: raise ValueError("Minimum 4 characters")
        password = generate_password(
            length, check_letters.get(), check_numbers.get(), check_symbols.get()
        )
        output_var.set(password)
        strength, color = evaluate_strength(password)
        strength_label.configure(text=f"Strength: {strength}", text_color=color)
        strength_label.pack(pady=(5, 10))
    except ValueError as e:
        messagebox.showerror("Error", str(e))

def evaluate_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if any(c.islower() for c in password) and any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in string.punctuation for c in password): score += 1
    if score <= 1: return "Weak", "red"
    elif score <= 3: return "Medium", "orange"
    return "Strong", "green"

def copy_password():
    password = output_var.get()
    if password:
        app.clipboard_clear()
        app.clipboard_append(password)
        messagebox.showinfo("Copied!", "Password copied!")

def save_password():
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
        messagebox.showinfo("Saved", "Password saved to JSON file!")
    else:
        messagebox.showwarning("Empty", "Generate a password first.")

def request_password_visualization():
    if os.path.exists(user_password_file):
        show_password_window()
    else:
        set_initial_password()

def set_initial_password():
    def save_password():
        new_pw = entry.get()
        if new_pw:
            with open(user_password_file, "w") as f:
                json.dump({"password": new_pw}, f)
            messagebox.showinfo("Password set", "Password set successfully!")
            pw_window.destroy()

    pw_window = ctk.CTkToplevel(app)
    pw_window.title("Set Password")
    pw_window.geometry("350x100")
    pw_window.resizable(False, False)
    # Removed .iconbitmap(img_ico)

    frame = ctk.CTkFrame(pw_window)
    frame.pack(pady=10, padx=10)

    entry = ctk.CTkEntry(frame, show="*")
    entry.pack(side="left", padx=(0, 5))

    show_button = ctk.CTkButton(frame, text="Show", width=40,
                                 command=lambda: toggle_password(entry, show_button))
    show_button.pack(side="left")

    ctk.CTkButton(pw_window, text="OK", command=save_password).pack(pady=5)
    center_window(pw_window)  # Center the window

def show_password_window():
    pw_window = ctk.CTkToplevel(app)
    pw_window.title("Enter Password")
    pw_window.geometry("350x100")
    pw_window.resizable(False, False)
    # Removed .iconbitmap(img_ico)

    def verify():
        entered = entry.get()
        if not entered: return
        with open(user_password_file, "r") as f:
            saved_password = json.load(f)["password"]
        if entered == saved_password:
            pw_window.destroy()
            visualize_passwords()
        else:
            messagebox.showerror("Error", "Incorrect password!")

    frame = ctk.CTkFrame(pw_window)
    frame.pack(pady=10, padx=10)

    entry = ctk.CTkEntry(frame, show="*")
    entry.pack(side="left", padx=(0, 5))

    show_button = ctk.CTkButton(frame, text="Show", width=40,
                                 command=lambda: toggle_password(entry, show_button))
    show_button.pack(side="left")

    ctk.CTkButton(pw_window, text="OK", command=verify).pack(pady=5)
    center_window(pw_window)  # Center the window

def toggle_password(entry, button):
    if entry.cget("show") == "":
        entry.configure(show="*")
        button.configure(text="Show")
    else:
        entry.configure(show="")
        button.configure(text="Hide")

def visualize_passwords():
    if os.path.exists(json_password_file):
        with open(json_password_file, "r") as f:
            data = json.load(f)
        passwords = data.get("passwords", [])

        if passwords:
            pw_win = ctk.CTkToplevel(app)
            pw_win.title("Saved Passwords")
            pw_win.geometry("400x400")
            pw_win.resizable(False, False)
            # Removed .iconbitmap(img_ico)

            box = ctk.CTkFrame(pw_win, fg_color="transparent")
            box.pack(fill="both", expand=True, padx=10, pady=10)

            for password in passwords:
                frame = ctk.CTkFrame(box, fg_color="transparent")
                frame.pack(fill="x", pady=5)

                theme_color = "white" if dark_theme else "black"

                password_entry = ctk.CTkEntry(frame, state="normal", font=("Helvetica", 14))
                password_entry.insert(0, password)
                password_entry.configure(
                    state="readonly",
                    text_color=theme_color,
                    fg_color=ctk.CTk().cget("fg_color"),
                    border_width=0,
                    border_color=ctk.CTk().cget("fg_color")
                )
                password_entry.pack(side="left", fill="x", expand=True)
                password_entry.select_range(0, len(password))
            center_window(pw_win)  # Center the window
        else:
            messagebox.showinfo("No Passwords", "No passwords saved.")
    else:
        messagebox.showinfo("No Passwords", "No passwords saved.")

def center_window(window):
    window.update_idletasks()
    w = window.winfo_width()
    h = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (w // 2)
    y = (window.winfo_screenheight() // 2) - (h // 2)
    window.geometry(f"+{x}+{y}")

# === Main GUI ===
app = ctk.CTk()
app.title("Password Generator")
app.geometry("500x470")
app.resizable(False, False)

# Header
header_frame = ctk.CTkFrame(app, fg_color="transparent")
header_frame.pack(fill="x", pady=(10, 0), padx=10)

left_space = ctk.CTkLabel(header_frame, text="", width=100)
left_space.pack(side="left")

center_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
center_frame.pack(side="left", expand=True)
title = ctk.CTkLabel(center_frame, text="Password Generator", font=("Helvetica", 20, "bold"))
title.pack(anchor="center")

right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
right_frame.pack(side="right")
theme_switch = ctk.CTkSwitch(right_frame, text="", command=change_theme)
theme_switch.pack(anchor="e")
theme_switch.select() if dark_theme else theme_switch.deselect()

# Input
length_frame = ctk.CTkFrame(app, fg_color="transparent")
length_frame.pack(pady=5)
ctk.CTkLabel(length_frame, text="Length:", font=("Helvetica", 14)).pack(side="left", padx=(0, 10))
entry_length = ctk.CTkEntry(length_frame, width=60, font=("Helvetica", 14))
entry_length.insert(0, "12")
entry_length.pack(side="left")

# Checkboxes
check_letters = ctk.CTkCheckBox(app, text="Letters", font=("Helvetica", 14))
check_numbers = ctk.CTkCheckBox(app, text="Numbers", font=("Helvetica", 14))
check_symbols = ctk.CTkCheckBox(app, text="Symbols", font=("Helvetica", 14))
check_letters.select()
check_numbers.select()
check_symbols.select()
check_letters.pack(pady=3)
check_numbers.pack(pady=3)
check_symbols.pack(pady=3)

# Buttons
ctk.CTkButton(app, text="🎲 Generate Password", command=generate, font=("Helvetica", 16, "bold")).pack(pady=15)

output_var = ctk.StringVar()
ctk.CTkEntry(app, textvariable=output_var, width=300, font=("Helvetica", 14)).pack(pady=(5, 0))
strength_label = ctk.CTkLabel(app, text="", font=("Helvetica", 14, "bold"))

ctk.CTkButton(app, text="📋 Copy Password", command=copy_password, font=("Helvetica", 16, "bold")).pack(pady=10)
ctk.CTkButton(app, text="💾 Save Password", command=save_password, font=("Helvetica", 16, "bold")).pack(pady=10)
ctk.CTkButton(app, text="🔐 View Passwords", command=request_password_visualization, font=("Helvetica", 16, "bold")).pack(pady=10)

# Footer
footer_label = ctk.CTkLabel(app, text="© 2025 SCSDC. All rights reserved", font=("Helvetica", 12, "italic"))
footer_label.place(relx=0.5, rely=1, anchor="s")
update_footer_color()

# Start
app.mainloop()