import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import time
import threading
import os
from pathlib import Path
from http.cookiejar import MozillaCookieJar
import customtkinter
import sys

# --- ZÁVISLOSTI PRO API A WORD ---
try:
    import google.generativeai as genai
except ImportError:
    messagebox.showerror("Chybějící knihovna", "Knihovna 'google-generativeai' není nainstalována.\n\nNainstalujte ji prosím příkazem:\npip install google-generativeai")
    sys.exit(1)

try:
    import docx
except ImportError:
    messagebox.showerror("Chybějící knihovna", "Knihovna 'python-docx' není nainstalována.\nPro podporu Word souborů ji nainstalujte příkazem:\npip install python-docx")
    # Neukončíme program, jen nebude fungovat import z .docx
    pass


# --- KONSTANTY A NASTAVENÍ UKLÁDÁNÍ DAT ---
APP_NAME = "VyzvyvatelAIHelper"

if sys.platform == "win32":
    APP_DATA_DIR = Path.home() / "AppData" / "Roaming" / APP_NAME
elif sys.platform == "darwin":
    APP_DATA_DIR = Path.home() / "Library" / "Application Support" / APP_NAME
else:
    APP_DATA_DIR = Path.home() / ".config" / APP_NAME

APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
SAVED_TEXTS_DIR = APP_DATA_DIR / "saved_texts"
SAVED_TEXTS_DIR.mkdir(exist_ok=True)

API_BASE_URL = "https://be.vyzyvatel.com/api"
LOGIN_URL = f"{API_BASE_URL}/auth/login"
SESSION_VALIDATE_URL = f"{API_BASE_URL}/users/me"
SETS_URL = f"{API_BASE_URL}/sets"
COOKIES_FILE = APP_DATA_DIR / "vyzyvatel_cookies.txt"
EDITOR_DATA_FILE = APP_DATA_DIR / "editor_data.json"
GEMINI_KEY_FILE = APP_DATA_DIR / "gemini_api_key.txt"
CREDENTIALS_FILE = APP_DATA_DIR / "vyzyvatel_credentials.json"

AI_PROMPT = """
Jsi asistent, který převádí text v přirozeném jazyce na strukturovaný JSON formát pro kvízovou aplikaci.
Text obsahuje otázky, které mohou být buď výběrové (s více možnostmi) nebo číselné.
Tvým úkolem je zpracovat text a vygenerovat JSON pole objektů. Každý objekt reprezentuje jednu otázku.
Struktura JSON objektů musí být přesně následující:
1. Pro výběrové otázky (typ "pick"):
   - "type": "pick"
   - "content": "Text otázky"
   - "correctAnswer": "Text správné odpovědi"
   - "wrongAnswers": ["Text špatné odpovědi 1", "Text špatné odpovědi 2", ...]
2. Pro číselné otázky (typ "number"):
   - "type": "number"
   - "content": "Text otázky"
   - "correctAnswer": "Číselná odpověď jako string"
Pravidla:
- Správná odpověď u výběrových otázek musí být označena (např. hvězdičkou, slovem SPRÁVNĚ, atd.), abys ji poznal.
- Výstup musí být pouze a jen validní JSON pole, bez jakéhokoliv dalšího textu nebo vysvětlení.
- Pokud je v textu nadpis nebo úvod, ignoruj ho a zpracuj pouze otázky.
- Ujisti se, že `correctAnswer` pro číselné otázky je string, ne číslo.
"""

HELP_TEXT = """
Vítejte v aplikaci Vyzývatel AI Asistent!

Tato aplikace vám pomůže snadno a rychle vytvářet sady otázek pro hru Vyzývatel.

Základní postup:
---------------------------------
1. Příprava textu:
   - V záložce "Editor Otázek" napište nebo vložte text s vašimi otázkami.
   - Můžete také použít tlačítko "Načíst soubor..." pro import z .txt nebo .docx.
   - U výběrových otázek označte správnou odpověď (např. hvězdičkou *).

2. Generování s AI:
   - Klikněte na tlačítko "Generovat s Gemini (API)".
   - AI automaticky převede váš text do strukturovaného formátu JSON.
   - Při prvním použití budete požádáni o vložení vašeho Gemini API klíče.

3. Nahrání do Vyzývatele:
   - Po úspěšném vygenerování se přepněte do záložky "Nahrávač do Vyzývatele".
   - Zde uvidíte náhled vygenerovaných otázek.
   - Zadejte číselné "ID Sady", do které chcete otázky nahrát.
   - Novou sadu můžete vytvořit přímo ve hře nebo v záložce "Nahrávač".
   - Klikněte na "Nahrát otázky".

Přihlášení:
---------------------------------
- Pro nahrávání otázek musíte být přihlášeni.
- Použijte tlačítko "Přihlásit se" vpravo nahoře.
- Aplikace si může zapamatovat vaše údaje pro příští spuštění, pokud s tím budete souhlasit.
"""

# --- GUI Třídy ---
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class LoginWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Přihlášení do Vyzývatel"); self.geometry("350x250")
        self.lift(); self.attributes("-topmost", True); self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.credentials = None; self.grid_columnconfigure(0, weight=1)
        self.name_label = customtkinter.CTkLabel(self, text="Jméno:"); self.name_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.name_entry = customtkinter.CTkEntry(self, placeholder_text="Vaše jméno"); self.name_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.password_label = customtkinter.CTkLabel(self, text="Heslo:"); self.password_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.password_entry = customtkinter.CTkEntry(self, placeholder_text="Vaše heslo", show="*"); self.password_entry.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.login_button = customtkinter.CTkButton(self, text="Přihlásit se", command=self._on_ok); self.login_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
        self.name_entry.focus_set()
    def _on_ok(self, event=None):
        name = self.name_entry.get(); password = self.password_entry.get()
        if name and password: self.credentials = {"name": name, "password": password}; self.destroy()
        else: messagebox.showwarning("Chyba", "Jméno a heslo nesmí být prázdné.", parent=self)
    def _on_closing(self): self.credentials = None; self.destroy()
    def get_credentials(self): self.master.wait_window(self); return self.credentials

class CreateSetWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Vytvořit novou sadu"); self.geometry("350x200")
        self.lift(); self.attributes("-topmost", True); self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.set_data = None; self.grid_columnconfigure(0, weight=1)
        self.name_label = customtkinter.CTkLabel(self, text="Název sady:"); self.name_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.name_entry = customtkinter.CTkEntry(self, placeholder_text="Např. Léčiva a farmacie"); self.name_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.desc_label = customtkinter.CTkLabel(self, text="Popis (volitelný):"); self.desc_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.desc_entry = customtkinter.CTkEntry(self, placeholder_text="Stručný popis obsahu sady"); self.desc_entry.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.private_var = tk.BooleanVar(value=True)
        self.private_check = customtkinter.CTkCheckBox(self, text="Soukromá sada", variable=self.private_var); self.private_check.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.create_button = customtkinter.CTkButton(self, text="Vytvořit", command=self._on_ok); self.create_button.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.name_entry.focus_set()
    def _on_ok(self, event=None):
        name = self.name_entry.get(); description = self.desc_entry.get()
        if name: self.set_data = {"name": name, "description": description, "private": self.private_var.get()}; self.destroy()
        else: messagebox.showwarning("Chyba", "Název sady nesmí být prázdný.", parent=self)
    def _on_closing(self): self.set_data = None; self.destroy()
    def get_set_data(self): self.master.wait_window(self); return self.set_data

# 3.5 QuestionGeneratorApp

class QuestionGeneratorApp(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = None; self.saved_documents = {}; self.current_file_path = None
        self.user_name = None
        self.gemini_api_key = None
        self.saved_username = None
        self.saved_password = None
        self.allow_saving_credentials = None
        
        self.title("Vyzývatel AI Asistent"); self.geometry("950x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Horní lišta
        self.grid_rowconfigure(1, weight=1) # Tab view
        self.grid_rowconfigure(2, weight=0) # Tlačítka
        self.grid_rowconfigure(3, weight=0) # Status bar
        
        # --- HORNÍ LIŠTA ---
        self.top_bar_frame = customtkinter.CTkFrame(self, height=40, corner_radius=0)
        self.top_bar_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        self.top_bar_frame.grid_columnconfigure(4, weight=1) # Prázdný prostor

        self.new_file_button = customtkinter.CTkButton(self.top_bar_frame, text="Nový", width=80, command=self.new_text_file)
        self.new_file_button.grid(row=0, column=0, padx=(10, 5), pady=10)

        self.load_button = customtkinter.CTkButton(self.top_bar_frame, text="Načíst...", width=100, command=self.load_and_save_file)
        self.load_button.grid(row=0, column=1, padx=5, pady=10)

        self.save_as_button = customtkinter.CTkButton(self.top_bar_frame, text="Uložit jako...", width=110, command=self.save_current_text_prompt)
        self.save_as_button.grid(row=0, column=2, padx=5, pady=10)
        
        self.quick_save_button = customtkinter.CTkButton(self.top_bar_frame, text="Uložit (Ctrl+S)", width=120, command=self.save_text_file)
        self.quick_save_button.grid(row=0, column=3, padx=5, pady=10)
        
        self.login_button = customtkinter.CTkButton(self.top_bar_frame, text="Přihlásit se", width=140, command=self.prompt_login)
        self.login_button.grid(row=0, column=5, padx=10, pady=10)

        # --- HLAVNÍ OBSAH - ZÁLOŽKY ---
        self.tab_view = customtkinter.CTkTabview(self, corner_radius=8, command=self.update_top_bar_visibility)
        self.tab_view.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.tab_view._segmented_button.configure(font=customtkinter.CTkFont(size=14, weight="bold")) 
        self.tab_view.add("Editor Otázek")
        self.tab_view.add("Nahrávač do Vyzývatele")
        self.tab_view.add("Nápověda")

        # --- Záložka: Editor Otázek ---
        self.editor_frame = self.tab_view.tab("Editor Otázek"); self.editor_frame.grid_columnconfigure(1, weight=1); self.editor_frame.grid_rowconfigure(0, weight=1)
        self.sidebar_frame = customtkinter.CTkFrame(self.editor_frame, width=150, corner_radius=0); self.sidebar_frame.grid(row=0, column=0, sticky="nsw")
        self.sidebar_label = customtkinter.CTkLabel(self.sidebar_frame, text="Uložené texty", font=customtkinter.CTkFont(size=14, weight="bold")); self.sidebar_label.pack(padx=10, pady=10)
        self.saved_docs_frame = customtkinter.CTkScrollableFrame(self.sidebar_frame, corner_radius=0); self.saved_docs_frame.pack(fill="both", expand=True)
        self.editor_textbox = customtkinter.CTkTextbox(self.editor_frame, wrap=tk.WORD, corner_radius=0, undo=True); self.editor_textbox.grid(row=0, column=1, sticky="nsew")

        # --- Tlačítka pro generování ---
        self.ai_button_frame = customtkinter.CTkFrame(self, fg_color="transparent"); self.ai_button_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.ai_button_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.gemini_button = customtkinter.CTkButton(self.ai_button_frame, text="✨ Generovat s Gemini (API)", command=lambda: self.start_ai_generation('gemini')); self.gemini_button.grid(row=0, column=0, padx=(0,5), sticky="ew")
        self.deepseek_button = customtkinter.CTkButton(self.ai_button_frame, text="🚀 Generovat s DeepSeek (Připravuje se)", command=self.show_feature_unavailable, fg_color="grey"); self.deepseek_button.grid(row=0, column=1, padx=(5,0), sticky="ew")

        # --- Záložka: Nahrávač do Vyzývatele ---
        self.uploader_frame = self.tab_view.tab("Nahrávač do Vyzývatele"); self.uploader_frame.grid_columnconfigure(0, weight=1); self.uploader_frame.grid_rowconfigure(1, weight=1)
        self.control_frame = customtkinter.CTkFrame(self.uploader_frame, corner_radius=0); self.control_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        self.create_set_button = customtkinter.CTkButton(self.control_frame, text="Vytvořit novou sadu", command=self.prompt_create_set, state=tk.DISABLED); self.create_set_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.select_file_button = customtkinter.CTkButton(self.control_frame, text="Načíst JSON soubor", command=self.select_json_file, state=tk.DISABLED); self.select_file_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.save_file_button = customtkinter.CTkButton(self.control_frame, text="Uložit vygenerovaný JSON", command=self.save_generated_json, state=tk.DISABLED); self.save_file_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.id_label = customtkinter.CTkLabel(self.control_frame, text="ID Sady:"); self.id_label.pack(side=tk.LEFT, padx=(10, 5), pady=10)
        self.set_id_entry = customtkinter.CTkEntry(self.control_frame, width=80, state=tk.DISABLED); self.set_id_entry.pack(side=tk.LEFT, padx=0, pady=10)
        self.upload_button = customtkinter.CTkButton(self.control_frame, text="Nahrát otázky", command=self.start_upload_thread, state=tk.DISABLED, fg_color="green", hover_color="darkgreen"); self.upload_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.preview_text = customtkinter.CTkTextbox(self.uploader_frame, wrap=tk.WORD, corner_radius=0, state=tk.DISABLED); self.preview_text.grid(row=1, column=0, sticky="nsew")

        # --- Záložka: Nápověda ---
        self.help_frame = self.tab_view.tab("Nápověda")
        self.help_textbox = customtkinter.CTkTextbox(self.help_frame, wrap=tk.WORD, font=("Segoe UI", 14))
        self.help_textbox.pack(expand=True, fill="both", padx=10, pady=10)
        self.help_textbox.insert("1.0", HELP_TEXT)
        self.help_textbox.configure(state="disabled")

        # --- Stavový řádek ---
        self.status_bar = customtkinter.CTkLabel(self, text="Stav: Odhlášeno", height=24, anchor='w'); self.status_bar.grid(row=3, column=0, padx=10, pady=(5,10), sticky="ew")
        
        self.bind("<Control-s>", self.save_text_file_event)
        self.update_top_bar_visibility() # Pro správné zobrazení při startu
        self.load_credentials()
        self.load_gemini_key()
        self.load_saved_documents()
        self.after(200, self.try_auto_login)

    def prompt_for_saving_consent(self):
        title = "Souhlas s ukládáním citlivých údajů"
        message = ("Chystáte se uložit přihlašovací jméno/heslo nebo API klíč.\n\n"
                   "Tyto údaje budou uloženy v čitelném textovém formátu ve vašem počítači pro zjednodušení budoucích přihlášení.\n\n"
                   "Souhlasíte s uložením?")
        
        response = messagebox.askyesno(title, message, parent=self)
        self.allow_saving_credentials = response
        return response

    def update_top_bar_visibility(self):
        current_tab = self.tab_view.get()
        show = (current_tab == "Editor Otázek")
        
        if show:
            self.new_file_button.grid()
            self.load_button.grid()
            self.save_as_button.grid()
            self.quick_save_button.grid()
        else:
            self.new_file_button.grid_remove()
            self.load_button.grid_remove()
            self.save_as_button.grid_remove()
            self.quick_save_button.grid_remove()

    def save_text_file_event(self, event=None):
        self.save_text_file()
        return "break"

    def load_credentials(self):
        if CREDENTIALS_FILE.exists():
            try:
                with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
                    creds = json.load(f)
                    self.saved_username = creds.get("name")
                    self.saved_password = creds.get("password")
            except (json.JSONDecodeError, IOError):
                self.saved_username = None
                self.saved_password = None

    def load_gemini_key(self):
        if GEMINI_KEY_FILE.exists():
            with open(GEMINI_KEY_FILE, 'r') as f:
                self.gemini_api_key = f.read().strip()

    def prompt_and_save_gemini_key(self):
        key = simpledialog.askstring("Gemini API Klíč", "Vložte prosím váš Google AI API klíč:", parent=self)
        if key:
            self.gemini_api_key = key.strip()
            if self.allow_saving_credentials is None:
                self.prompt_for_saving_consent()
            
            if self.allow_saving_credentials:
                with open(GEMINI_KEY_FILE, 'w') as f: f.write(self.gemini_api_key)
                self.log_to_status("API klíč byl trvale uložen.")
            else:
                self.log_to_status("API klíč bude použit pouze dočasně.")
            return True
        return False
    
    def show_feature_unavailable(self):
        messagebox.showinfo("Funkce nedostupná", "Tato funkce bude přidána v budoucí verzi.", parent=self)

    def start_ai_generation(self, provider):
        if provider == 'gemini':
            text_content = self.editor_textbox.get("1.0", tk.END).strip()
            if not text_content: 
                messagebox.showwarning("Prázdný text", "Editor je prázdný.")
                return
            
            self.log_to_status(f"⏳ Spouštím generování s Gemini...")
            self.gemini_button.configure(state=tk.DISABLED)
            
            if not self.gemini_api_key:
                if not self.prompt_and_save_gemini_key():
                    self.log_to_status("Generování zrušeno, chybí API klíč.")
                    self.gemini_button.configure(state=tk.NORMAL)
                    return
            
            threading.Thread(target=self.generate_with_gemini, args=(text_content,), daemon=True).start()

    def generate_with_gemini(self, text_content):
        try:
            self.after(0, lambda: self.log_to_status("⏳ Gemini generuje odpověď..."))
            genai.configure(api_key=self.gemini_api_key)
            full_prompt = AI_PROMPT + "\n\n---\n\n" + text_content
            
            response = None
            try:
                self.after(0, lambda: self.log_to_status("🤖 Zkouším model 'gemini-1.5-flash' (limit 2 minuty)..."))
                model = genai.GenerativeModel("gemini-1.5-flash-latest")
                response = model.generate_content(full_prompt, request_options={'timeout': 120})
            except Exception as e:
                self.after(0, lambda err=e: self.log_to_status(f"⚠️ Primární model selhal ({type(err).__name__}), zkouším záložní..."))
                time.sleep(1)
                model = genai.GenerativeModel("learnlm-2.0-flash-experimental")
                response = model.generate_content(full_prompt)

            if response and hasattr(response, 'text') and response.text:
                self.after(0, lambda: self.process_ai_response(response.text))
            else:
                try:
                    candidate_text = response.candidates[0].content.parts[0].text
                    self.after(0, lambda: self.process_ai_response(candidate_text))
                except (AttributeError, IndexError):
                     raise ValueError("AI nevrátila žádný text ani v kandidátech.")

        except Exception as e:
            self.after(0, lambda: self.log_to_status(f"❌ Chyba při generování (Gemini)!"))
            self.after(0, lambda err=e: messagebox.showerror("Chyba Gemini API", f"Nastala chyba i u záložního modelu:\n\n{err}"))
        finally:
            self.after(0, lambda: self.gemini_button.configure(state=tk.NORMAL))

    def try_auto_login(self):
        if self.saved_username and self.saved_password:
            self.log_to_status("Nalezeny uložené údaje. Zkouším se přihlásit...")
            threading.Thread(target=self.perform_api_login, args=(self.saved_username, self.saved_password), daemon=True).start()
        else:
            self.log_to_status("Připraveno. Přihlaste se pro nahrávání otázek.")

    def perform_logout(self):
        self.session = None
        self.user_name = None
        self.saved_username = None
        self.saved_password = None

        if CREDENTIALS_FILE.exists(): CREDENTIALS_FILE.unlink()
        if COOKIES_FILE.exists(): COOKIES_FILE.unlink()

        self.update_login_status()
        self.create_set_button.configure(state=tk.DISABLED)
        self.select_file_button.configure(state=tk.DISABLED)
        self.set_id_entry.configure(state=tk.DISABLED)
        self.log_to_status("Úspěšně odhlášeno.")

    def perform_api_login(self, name, password):
        self.after(0, lambda: self.log_to_status(f"Přihlašuji se jako {name}..."))
        self.make_session()
        try:
            response = self.session.post(LOGIN_URL, json={"name": name, "password": password}, timeout=20)
            if response.status_code == 200:
                self.session.cookies.save(ignore_discard=True, ignore_expires=False)
                self.user_name = response.json().get('user', {}).get('name', name)
                
                self.saved_username = name
                self.saved_password = password

                if self.allow_saving_credentials is None:
                    self.prompt_for_saving_consent()

                if self.allow_saving_credentials:
                    try:
                        with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
                            json.dump({"name": name, "password": password}, f)
                    except IOError as e: print(f"Chyba při ukládání údajů: {e}")

                self.after(0, self.update_login_status)
                self.after(0, self.unlock_app)
            else:
                self.after(0, lambda: messagebox.showerror("Chyba přihlášení", f"Přihlášení selhalo: {response.json().get('message', response.text)}"))
                self.after(0, lambda: self.log_to_status("Přihlášení selhalo."))
        except requests.exceptions.RequestException as e:
            self.after(0, lambda: messagebox.showerror("Chyba sítě", f"Nepodařilo se připojit k serveru:\n{e}"))
            self.after(0, lambda: self.log_to_status("Chyba sítě."))

    def update_login_status(self):
        if self.user_name:
            self.login_button.configure(text=f"Odhlásit ({self.user_name})", command=self.perform_logout)
            self.log_to_status(f"Přihlášen jako {self.user_name}")
        else:
            self.login_button.configure(text="Přihlásit se", command=self.prompt_login)
            self.log_to_status("Odhlášeno.")
    
    def save_current_text_prompt(self):
        text_content = self.editor_textbox.get("1.0", tk.END).strip()
        if not text_content:
            messagebox.showwarning("Prázdný editor", "Není co uložit, editor je prázdný.", parent=self)
            return

        filename = simpledialog.askstring("Pojmenovat soubor", "Zadejte název pro uložení textu (bez přípony):", parent=self)
        if filename:
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '_', '-')).rstrip()
            if not safe_filename:
                messagebox.showerror("Chyba", "Zadán neplatný název souboru.", parent=self)
                return
            
            filepath = SAVED_TEXTS_DIR / f"{safe_filename}.txt"
            self._write_to_file(filepath)
            
    def load_and_save_file(self):
        filepath = filedialog.askopenfilename(
            title="Načíst textový soubor",
            filetypes=(("Všechny textové soubory", "*.txt *.docx"),("Textové soubory", "*.txt"), ("Word dokumenty", "*.docx"))
        )
        if not filepath: return
        
        content = ""
        try:
            if filepath.lower().endswith(".txt"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif filepath.lower().endswith(".docx"):
                try:
                    doc = docx.Document(filepath)
                    content = "\n".join([para.text for para in doc.paragraphs])
                except NameError:
                    messagebox.showerror("Chybějící knihovna", "Pro načtení .docx souborů je nutné nainstalovat knihovnu 'python-docx'.", parent=self)
                    return
            
            self.editor_textbox.delete("1.0", tk.END)
            self.editor_textbox.insert("1.0", content)
            self.log_to_status(f"Soubor '{os.path.basename(filepath)}' načten. Nyní ho uložte.")
            self.save_current_text_prompt()

        except Exception as e:
            messagebox.showerror("Chyba", f"Nepodařilo se otevřít soubor:\n{e}", parent=self)

    def _write_to_file(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as f: f.write(self.editor_textbox.get("1.0", tk.END))
            self.current_file_path = path; self.title(f"Vyzývatel AI Asistent - {os.path.basename(path)}")
            self.log_to_status(f"Soubor '{os.path.basename(path)}' uložen."); self.update_saved_documents_list()
        except Exception as e: messagebox.showerror("Chyba", f"Nepodařilo se uložit soubor:\n{e}")
    
    def new_text_file(self, event=None):
        if messagebox.askyesno("Nový soubor", "Opravdu chcete vytvořit nový text? Neuložené změny budou ztraceny."):
            self.editor_textbox.delete("1.0", tk.END)
            self.current_file_path = None
            self.title("Vyzývatel AI Asistent - Nový soubor")

    def open_text_file(self, path=None):
        if not path: return
        try:
            with open(path, 'r', encoding='utf-8') as f: self.editor_textbox.delete("1.0", tk.END); self.editor_textbox.insert("1.0", f.read())
            self.current_file_path = path; self.title(f"Vyzývatel AI Asistent - {os.path.basename(path)}")
        except Exception as e: messagebox.showerror("Chyba", f"Nepodařilo se otevřít soubor:\n{e}")

    def save_text_file(self):
        if self.current_file_path and Path(self.current_file_path).exists():
            self._write_to_file(self.current_file_path)
        else:
            self.save_current_text_prompt()

    def load_saved_documents(self):
        self.saved_documents = {f.name: str(f) for f in SAVED_TEXTS_DIR.glob("*.txt")}
        self.update_sidebar()

    def update_saved_documents_list(self):
        self.load_saved_documents()

    def update_sidebar(self):
        for widget in self.saved_docs_frame.winfo_children(): widget.destroy()
        sorted_docs = sorted(self.saved_documents.items())
        for name, path in sorted_docs:
            btn = customtkinter.CTkButton(self.saved_docs_frame, text=name, anchor="w", fg_color="transparent", command=lambda p=path: self.open_text_file(p))
            btn.pack(fill="x", padx=5, pady=2)

    def process_ai_response(self, response_text):
        cleaned_response = response_text.strip()
        if "```json" in cleaned_response: cleaned_response = cleaned_response.split("```json")[1]
        if "```" in cleaned_response: cleaned_response = cleaned_response.split("```")[0]
        try:
            self.questions_to_upload = json.loads(cleaned_response)
            self.log_to_status("✅ AI úspěšně vygenerovala otázky. Zkontrolujte náhled.")
            self.populate_uploader_preview(); self.tab_view.set("Nahrávač do Vyzývatele")
        except json.JSONDecodeError:
            self.log_to_status("❌ AI vrátila neplatný JSON.")
            self.preview_text.configure(state=tk.NORMAL); self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", f"Chyba: AI vrátila neplatný formát.\n\nOdpověď od AI:\n{response_text}")
            self.preview_text.configure(state=tk.DISABLED)

    def populate_uploader_preview(self):
        self.preview_text.configure(state=tk.NORMAL); self.preview_text.delete('1.0', tk.END)
        try:
            preview_str = f"Nalezeno otázek: {len(self.questions_to_upload)}\n-------------------------------------\n\n"
            for i, q in enumerate(self.questions_to_upload):
                content = q.get('content') or q.get('question', 'Neznámý obsah')
                preview_str += f"#{i+1}: {content}\n  Typ: {q.get('type', 'Neznámý typ')}\n\n"
            self.upload_button.configure(state=tk.NORMAL); self.save_file_button.configure(state=tk.NORMAL)
        except (TypeError, AttributeError):
            preview_str = "Chyba: Vygenerovaná data nejsou seznamem otázek."
            self.upload_button.configure(state=tk.DISABLED); self.save_file_button.configure(state=tk.DISABLED)
        self.preview_text.insert(tk.END, preview_str); self.preview_text.configure(state=tk.DISABLED)

    def save_generated_json(self):
        if not hasattr(self, 'questions_to_upload') or not self.questions_to_upload: messagebox.showwarning("Žádná data", "Nejsou zde žádné vygenerované otázky k uložení."); return
        path = filedialog.asksaveasfilename(defaultextension=".json", title="Uložit JSON soubor", filetypes=(("JSON soubory", "*.json"),))
        if not path: return
        try:
            with open(path, 'w', encoding='utf-8') as f: json.dump(self.questions_to_upload, f, indent=4, ensure_ascii=False)
            self.log_to_status(f"JSON soubor uložen do '{os.path.basename(path)}'")
        except Exception as e: messagebox.showerror("Chyba", f"Nepodařilo se uložit soubor:\n{e}")

    def make_session(self):
        s = requests.Session()
        s.cookies = MozillaCookieJar(str(COOKIES_FILE))
        if COOKIES_FILE.exists(): s.cookies.load(ignore_discard=True, ignore_expires=True)
        s.headers.update({"User-Agent": "VyzvyvatelAIHelper/1.0", "Accept": "application/json, text/plain, */*", "Origin": "https://vyzyvatel.com", "Referer": "https://vyzyvatel.com/"})
        self.session = s

    def prompt_login(self):
        login_dialog = LoginWindow(self)
        credentials = login_dialog.get_credentials()
        if credentials: threading.Thread(target=self.perform_api_login, args=(credentials['name'], credentials['password']), daemon=True).start()

    def prompt_create_set(self):
        create_dialog = CreateSetWindow(self)
        set_data = create_dialog.get_set_data()
        if set_data: threading.Thread(target=self.perform_create_set, args=(set_data,), daemon=True).start()

    def perform_create_set(self, set_data):
        self.after(0, lambda: self.log_to_status(f"Vytvářím sadu '{set_data['name']}'..."))
        try:
            response = self.session.post(SETS_URL, json=set_data, timeout=20)
            if response.status_code == 201:
                new_set = response.json(); new_id = new_set.get('id')
                self.after(0, lambda: self.log_to_status(f"Sada úspěšně vytvořena s ID: {new_id}"))
                self.after(0, lambda: messagebox.showinfo("Úspěch", f"Sada '{new_set.get('name')}' byla úspěšně vytvořena.\nJejí ID je: {new_id}"))
                self.after(0, lambda: (self.set_id_entry.delete(0, tk.END), self.set_id_entry.insert(0, str(new_id))))
            else:
                self.after(0, lambda: messagebox.showerror("Chyba", f"Vytvoření sady selhalo: {response.json().get('message', response.text)}"))
        except requests.exceptions.RequestException as e:
            self.after(0, lambda: messagebox.showerror("Chyba sítě", f"Nepodařilo se připojit k serveru:\n{e}"))

    def unlock_app(self):
        self.create_set_button.configure(state=tk.NORMAL); self.select_file_button.configure(state=tk.NORMAL); self.set_id_entry.configure(state=tk.NORMAL)
        self.update_login_status()

    def select_json_file(self):
        filepath = filedialog.askopenfilename(title="Načíst hotový JSON soubor", filetypes=(("JSON soubory", "*.json"),))
        if not filepath: return
        encodings_to_try = ['utf-8-sig', 'utf-8', 'windows-1250', 'iso-8859-2']
        loaded_successfully = False
        for encoding in encodings_to_try:
            try:
                with open(filepath, 'r', encoding=encoding) as f: self.questions_to_upload = json.load(f)
                loaded_successfully = True; break
            except (UnicodeDecodeError, json.JSONDecodeError): continue
        if not loaded_successfully: messagebox.showerror("Chyba souboru", "Nepodařilo se zpracovat soubor."); return
        self.log_to_status(f"JSON soubor '{os.path.basename(filepath)}' načten.")
        self.populate_uploader_preview()

    def start_upload_thread(self):
        if not hasattr(self, 'questions_to_upload') or not self.questions_to_upload: messagebox.showwarning("Chybí otázky", "Nejprve načtěte nebo vygenerujte otázky."); return
        threading.Thread(target=self.upload_questions, daemon=True).start()

    def log_to_status(self, message):
        self.status_bar.configure(text=f"Stav: {message}")

    def upload_questions(self):
        set_id_str = self.set_id_entry.get()
        if not set_id_str.isdigit() or int(set_id_str) == 0:
            self.after(0, lambda: messagebox.showwarning("Chybějící údaj", "Prosím, zadejte platné číselné ID sady."))
            return
        
        if not messagebox.askyesno("Potvrzení", f"Opravdu chcete nahrát {len(self.questions_to_upload)} otázek do sady ID: {set_id_str}?"): return
        
        self.after(0, lambda: self.upload_button.configure(state=tk.DISABLED))
        url = f"{SETS_URL}/{set_id_str}/questions"
        self.after(0, lambda: self.log_to_status(f"🚀 Zahajuji nahrávání..."))
        
        success_count = 0
        for i, q in enumerate(self.questions_to_upload):
            self.after(0, lambda i=i: self.log_to_status(f"🚀 Nahrávám otázku {i+1}/{len(self.questions_to_upload)}..."))
            
            content = q.get('content') or q.get('question', ''); fields = {}
            if q.get('type') == 'number':
                fields = {"content": content, "questionType": "number", "correctAnswer": str(q.get('correctAnswer'))}
            elif q.get('type') == 'pick':
                correct_answer = q.get('correctAnswer')
                wrong_answers_list = q.get('wrongAnswers', [])
                fields = {"content": content, "questionType": "pick", "correctAnswer": correct_answer}
                for index, wrong_answer in enumerate(wrong_answers_list):
                    fields[f'wrongAnswers[{index}]'] = wrong_answer
            
            multipart_data = MultipartEncoder(fields=fields)
            try:
                response = self.session.post(url, data=multipart_data, headers={"Content-Type": multipart_data.content_type})
                if response.status_code in [200, 201]:
                    success_count += 1
                else:
                    self.after(0, lambda i=i: self.log_to_status(f"❌ Chyba u otázky #{i+1}! Kód: {response.status_code}"))
                    time.sleep(2)
            except requests.exceptions.RequestException:
                self.after(0, lambda: self.log_to_status("❌ Chyba sítě! Nahrávání přerušeno."))
                break
            time.sleep(1)
            
        self.after(0, lambda: messagebox.showinfo("Hotovo", f"Nahrávání dokončeno.\n\nÚspěšně nahráno: {success_count}\nChyb: {len(self.questions_to_upload) - success_count}"))
        self.after(0, lambda: self.upload_button.configure(state=tk.NORMAL))
        self.after(0, lambda: self.log_to_status(f"Přihlášen jako {self.user_name}"))
if __name__ == "__main__":
    app = QuestionGeneratorApp()
    app.mainloop()