import customtkinter as ctk
from tkinter import messagebox, Canvas, Scrollbar
from tkinter.simpledialog import askstring
import os
import random
import string
import json

# --- Secure Path Configuration ---
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".password_generator")
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(CONFIG_DIR, "theme_config.json")
JSON_PASSWORD_FILE = os.path.join(CONFIG_DIR, "passwords.json")
USER_PASSWORD_FILE = os.path.join(CONFIG_DIR, "user_password.json")

# --- Theme Management ---
dark_theme = False

def load_theme():
    """Loads the theme preference from the config file."""
    global dark_theme
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            dark_theme = config.get("switch_active", False)
            return config.get("theme", "Light")
    return "Light"

def save_theme(theme):
    """Saves the theme preference to the config file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump({"theme": theme, "switch_active": theme == "Dark"}, f)

ctk.set_appearance_mode(load_theme())
ctk.set_default_color_theme("blue")

def change_theme():
    """Toggles the application theme between Light and Dark."""
    global dark_theme
    dark_theme = not dark_theme
    new_theme = "Dark" if dark_theme else "Light"
    ctk.set_appearance_mode(new_theme)
    save_theme(new_theme)
    update_footer_color()

def update_footer_color():
    """Updates the footer label color based on the current theme."""
    color = "#FFFFFF" if dark_theme else "#000000"
    footer_label.configure(text_color=color)

def generate_password(length, use_letters, use_numbers, use_symbols):
    """Generates a random password based on the specified criteria."""
    characters = ""
    if use_letters:
        characters += string.ascii_letters
    if use_numbers:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation
    if not characters:
        raise ValueError("Select at least one character category!")
    return ''.join(random.choices(characters, k=length))

def generate():
    """Handles the password generation process on button click."""
    try:
        length = int(entry_length.get())
        if length < 4:
            raise ValueError("Minimum password length is 4 characters.")
        password = generate_password(
            length, check_letters.get(), check_numbers.get(), check_symbols.get()
        )
        output_var.set(password)
        update_password_strength(password)
        strength_label.pack(pady=2)
    except ValueError as e:
        messagebox.showerror("Error", str(e))

def evaluate_strength(password):
    """Evaluates the strength of a password and returns a label and color."""
    score = 0
    if len(password) >= 8:
        score += 1
    if any(c.islower() for c in password) and any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1
    if score <= 1:
        return "Weak", "red"
    elif score <= 3:
        return "Medium", "orange"
    return "Strong", "green"

def update_password_strength(password):
    """Evaluates the password strength and updates the label."""
    if not password:
        strength_label.configure(text="")
        strength_label.pack(pady=2) 
    else:
        strength, color = evaluate_strength(password)
        strength_label.configure(text=f"Strength: {strength}", text_color=color)
        strength_label.pack(pady=2) 

def copy_password():
    """Copies the generated password to the clipboard."""
    password = output_var.get()
    if password:
        app.clipboard_clear()
        app.clipboard_append(password)
        messagebox.showinfo("Copied!", "Password copied to clipboard!")

def save_password():
    """Saves the current password with a user-defined name."""
    password_to_save = output_var.get()
    if password_to_save:
        name_window = ctk.CTkToplevel(app)
        name_window.title("Save Password")
        name_window.geometry("350x100")
        name_window.resizable(False, False)
        center_window(name_window)

        label = ctk.CTkLabel(name_window, text="Enter password name:")
        label.pack(pady=(10, 0), padx=10)

        input_frame = ctk.CTkFrame(name_window, fg_color="transparent")
        input_frame.pack(pady=5, padx=10, fill="x")

        name_entry = ctk.CTkEntry(input_frame)
        name_entry.pack(side="left", fill="x", expand=True, padx=(0, 5)) 

        def save_with_name():
            name = name_entry.get()
            if name:
                if os.path.exists(JSON_PASSWORD_FILE):
                    with open(JSON_PASSWORD_FILE, "r") as f:
                        data = json.load(f)
                else:
                    data = {"passwords": []}
                data["passwords"].append({"name": name, "password": password_to_save})
                with open(JSON_PASSWORD_FILE, "w") as f:
                    json.dump(data, f, indent=4)
                messagebox.showinfo("Saved", f"Password saved as '{name}'!")
                name_window.destroy()
            else:
                messagebox.showwarning("Warning", "Please enter a name for the password.")

        save_button = ctk.CTkButton(input_frame, text="Save", width=80, command=save_with_name)
        save_button.pack(side="right")

        evaluate_strength(password_to_save) 

    else:
        messagebox.showwarning("Empty", "No password to save.")

def request_password_visualization():
    """Requests the user's password to view saved passwords."""
    if os.path.exists(USER_PASSWORD_FILE):
        show_password_window()
    else:
        set_initial_password()

def set_initial_password():
    """Sets the initial password for accessing saved passwords."""
    def save_user_password():
        """Saves the newly set user password."""
        new_pw = entry.get()
        if new_pw:
            with open(USER_PASSWORD_FILE, "w") as f:
                json.dump({"password": new_pw}, f)
            messagebox.showinfo("Password set", "Password set successfully!")
            pw_window.destroy()

    pw_window = ctk.CTkToplevel(app)
    pw_window.title("Set Password")
    pw_window.geometry("350x100")
    pw_window.resizable(False, False)
    center_window(pw_window)

    frame = ctk.CTkFrame(pw_window)
    frame.pack(pady=10, padx=10)

    entry = ctk.CTkEntry(frame, show="*")
    entry.pack(side="left", padx=(0, 5))

    show_button = ctk.CTkButton(frame, text="Show", width=40,
                                    command=lambda: toggle_password(entry, show_button))
    show_button.pack(side="left")

    ctk.CTkButton(pw_window, text="OK", command=save_user_password).pack(pady=5)

def show_password_window():
    """Prompts the user for their password to view saved passwords."""
    pw_window = ctk.CTkToplevel(app)
    pw_window.title("Enter Password")
    pw_window.geometry("350x100")
    pw_window.resizable(False, False)
    center_window(pw_window)

    def verify():
        """Verifies the entered password against the saved user password."""
        entered = entry.get()
        if not entered:
            return
        with open(USER_PASSWORD_FILE, "r") as f:
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

def toggle_password(entry, button):
    """Toggles the visibility of the password in an entry field."""
    if entry.cget("show") == "":
        entry.configure(show="*")
        button.configure(text="Show")
    else:
        entry.configure(show="")
        button.configure(text="Hide")

def visualize_passwords():
    """Displays the saved passwords and their names in a scrollable window."""
    print("Visualizzazione password avviata") 
    if os.path.exists(JSON_PASSWORD_FILE):
        with open(JSON_PASSWORD_FILE, "r") as f:
            try:
                data = json.load(f)
                passwords_data = data.get("passwords", [])
                print(f"Dati password letti: {passwords_data}") 
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Error reading the password file.")
                return
    else:
        messagebox.showinfo("No Passwords", "No passwords saved.")
        return

    if passwords_data:
        pw_win = ctk.CTkToplevel(app)
        pw_win.title("Saved Passwords")
        pw_win.geometry("350x400") 
        pw_win.resizable(False, False)
        center_window(pw_win)

        canvas = Canvas(pw_win, bd=0, highlightthickness=0, bg=pw_win.cget("bg")) 
        scrollable_frame = ctk.CTkFrame(canvas, fg_color=pw_win.cget("bg")) 
        scrollbar = ctk.CTkScrollbar(pw_win, orientation="vertical", command=canvas.yview)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)

        def update_scrollbar(event):
            if canvas.yview() == (0.0, 1.0):
                scrollbar.pack_forget()
            else:
                scrollbar.pack(side="right", fill="y")

        scrollable_frame.bind("<Configure>", update_scrollbar)
        canvas.bind("<Enter>", lambda e: scrollable_frame.focus_set())
        canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units")) 
        canvas.bind("<Button-4>", lambda event: canvas.yview_scroll(-1, "units")) 
        canvas.bind("<Button-5>", lambda event: canvas.yview_scroll(1, "units")) 

        for item in passwords_data:
            name = item.get("name", "Unnamed")
            password = item.get("password", "No Password")
            print(f"Nome nel ciclo: {name}, Password nel ciclo: {password}")

            frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent") 
            frame.pack(fill="x", pady=5)

            theme_color = "white" if dark_theme else "black"

            name_label = ctk.CTkLabel(frame, text=f"{name}:", font=("Helvetica", 14, "bold"), text_color=theme_color)
            name_label.pack(side="left", padx=(10, 5)) 

            password_entry = ctk.CTkEntry(frame, state="normal", font=("Helvetica", 14), text_color=theme_color, fg_color=ctk.CTk().cget("fg_color"), border_width=0, border_color=ctk.CTk().cget("fg_color"))
            password_entry.insert(0, password)
            password_entry.pack(side="left", fill="x", expand=True, padx=(10, 0)) 
            password_entry.select_range(0, len(password))

        empty_label = ctk.CTkLabel(scrollable_frame, text="", height=20)
        empty_label.pack()

        pw_win.after(100, lambda: update_scrollbar(None))

    else:
        messagebox.showinfo("No Passwords", "No passwords saved.")

def center_window(window):
    """Centers a given window on the screen."""
    window.update_idletasks()
    w = window.winfo_width()
    h = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (w // 2)
    y = (window.winfo_screenheight() // 2) - (h // 2)
    window.geometry(f"+{x}+{y}")

# === Main Application GUI ===
app = ctk.CTk()
app.title("SuperCool Password Generator")
app.geometry("500x400")
app.resizable(False, False)

# Header Section
header_frame = ctk.CTkFrame(app, fg_color="transparent")
header_frame.pack(fill="x", pady=(10, 0), padx=10)

left_space = ctk.CTkLabel(header_frame, text="", width=100)
left_space.pack(side="left")

center_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
center_frame.pack(side="left", expand=True)
title = ctk.CTkLabel(center_frame, text="SC Password Generator", font=("Helvetica", 20, "bold"))
title.pack(anchor="center")

right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
right_frame.pack(side="right")
theme_switch = ctk.CTkSwitch(right_frame, text="", command=change_theme)
theme_switch.pack(anchor="e")
theme_switch.select() if dark_theme else theme_switch.deselect()

# Input Controls
length_frame = ctk.CTkFrame(app, fg_color="transparent")
length_frame.pack(pady=5)
ctk.CTkLabel(length_frame, text="Length:", font=("Helvetica", 14)).pack(side="left", padx=(0, 10))
entry_length = ctk.CTkEntry(length_frame, width=60, font=("Helvetica", 14))
entry_length.insert(0, "12")
entry_length.pack(side="left")

# Password Options Checkboxes
check_letters = ctk.CTkCheckBox(app, text="Letters", font=("Helvetica", 14))
check_numbers = ctk.CTkCheckBox(app, text="Numbers", font=("Helvetica", 14))
check_symbols = ctk.CTkCheckBox(app, text="Symbols", font=("Helvetica", 14))
check_letters.select()
check_numbers.select()
check_symbols.select()
check_letters.pack(pady=3)
check_numbers.pack(pady=3)
check_symbols.pack(pady=3)

# Action Buttons
ctk.CTkButton(app, text="🎲 Generate Password", command=generate, font=("Helvetica", 16, "bold")).pack(pady=15)

# Password Output Field
output_var = ctk.StringVar()
output_entry = ctk.CTkEntry(app, textvariable=output_var, width=300, font=("Helvetica", 14))
output_entry.pack(pady=2)
output_entry.bind("<KeyRelease>", lambda event: update_password_strength(output_var.get()))

strength_label = ctk.CTkLabel(app, text="", font=("Helvetica", 14, "bold"))
strength_label.pack(pady=2)

# Button Actions
button_row_1 = ctk.CTkFrame(app, fg_color="transparent")
button_row_1.pack(pady=2, padx=20) 

copy_button = ctk.CTkButton(button_row_1, text="📋 Copy Password", command=copy_password, font=("Helvetica", 16, "bold"))
copy_button.pack(side="left", expand=True)

save_button = ctk.CTkButton(button_row_1, text="💾 Save Password", command=save_password, font=("Helvetica", 16, "bold"))
save_button.pack(side="left", padx=10, expand=True)

view_button = ctk.CTkButton(app, text="🔐 View Passwords", command=request_password_visualization, font=("Helvetica", 16, "bold"))
view_button.pack(pady=10, padx=20)

# Footer Information
footer_label = ctk.CTkLabel(app, text="© 2025 SCSDC. All rights reserved", font=("Helvetica", 12, "italic"))
footer_label.place(relx=0.5, rely=1, anchor="s")
update_footer_color()

# Start the app
app.mainloop()