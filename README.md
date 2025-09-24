# Popis je prozatímní AI generovaný polosmysl 
## Aplikace sama je také z 90 procent AI generovaná, ale i když s mnoha bugy zhruba funkční. 

# Poděkování:
Velice děkuji discord uživateli @akrej (id 221668967780057088) za vyřešení přihlašování přes API. 

#Uploader otázek do hry Vyzyvatel s AI Asistentem pro formátování otázek k do .json 
Nástroj pro rychlou a efektivní tvorbu otázek do hry Vyzyvatel pomocí umělé inteligence Gemini od Google. Aplikace umožňuje převod otázek napsaných v běžné řeči na strukturovaný JSON formát a jejich následné nahrání přímo do vaší sady otázek.

![image](https://github.com/user-attachments/assets/a13de119-8b3e-4ae0-979d-06042cbc0aa7)

---

## Klíčové funkce

- **Textový editor:** Pohodlné psaní a úprava textu s otázkami.
- **Správa souborů:** Možnost ukládat a načítat rozpracované texty z lokálních souborů.
- **Import z Wordu:** Podpora načítání textů přímo z `.docx` dokumentů.
- **AI Generování:** Převod textu na strukturovaný JSON formát pomocí Gemini API.
- **Náhled a úpravy:** Zobrazení vygenerovaných otázek před nahráním.
- **Přímé nahrání:** Nahrání hotových otázek do konkrétní sady ve hře Vyzyvatel.
- **Možnost uložení přihlášení (na vlastní nebezpečí):** Aplikace vám nabídne možnost uložení přihlašovacích údajů nebo API klíče na disk v textovém formátu.
- **Tmavý režim:** Moderní a přehledné uživatelské rozhraní. (pokus)

---

## Instalace a nastavení

Pro spuštění projektu z Python skriptu je nutné mít nainstalovaný Python 3.9+ a všechny potřebné závislosti.

### 1. Naklonujte repozitář:
    git clone https://[URL_VASEHO_REPOZITARE]
    cd Vyzvyvatel_AI_Asistent

### 2. Nainstalujte závislosti:
Všechny potřebné knihovny jsou definovány v souboru `requirements.txt`. Nainstalujte je pomocí jediného příkazu:
    pip install -r requirements.txt

### 3. Spuštění aplikace:
    python vyzyvatel_gui_uploader_alpha_0.1

---

## Jak aplikaci používat

### Příprava textu
- V záložce **Editor Otázek** napište nebo vložte text s otázkami.  
- Pro výběrové otázky označte správnou odpověď (např. hvězdičkou `*` na začátku nebo na konci řádku), ale jakýkoliv formát označení by měl být přijatelný. Otázky ani nemusí být pod sebou. Stačí, že správné odpovědi a jednotlivé otázky budou nějakým zhruba konzistentním způsobem označeny.  
- Pro nahrání existujícího textu použijte tlačítko **Načíst...** v horní liště.  

### Generování otázek
- Klikněte na tlačítko ✨ **Generovat s Gemini (API)**.  
- Při prvním použití budete vyzváni k zadání vašeho Google AI (Gemini) API klíče. Můžete ho získat zde.  
- AI zpracuje text a automaticky vás přesune do záložky **Nahrávač do Vyzyvatele**.  

### Nahrání do hry
- V záložce **Nahrávač** zkontrolujte náhled vygenerovaných otázek (zobrazí se jen otázky, ne odpovědi).  
- Přihlaste se do svého účtu ve Vyzyvateli pomocí tlačítka vpravo nahoře.  
- Zadejte **ID sady**, do které chcete otázky nahrát, nebo vytvořte sadu novou.
    - ID zýskáte na strankách hry v URl například u **https://www.vyzyvatel.com/dashboard/sets/138** je ID 138   
- Klikněte na tlačítko **Nahrát otázky**.  

---

## Kompilace do .exe (pro Windows)

Pokud chcete z aplikace vytvořit samostatný spustitelný soubor, který nevyžaduje instalaci Pythonu, můžete použít přiložený skript.

### 1. Nainstalujte PyInstaller
    pip install pyinstaller

### 2. Spusťte kompilaci
Jednoduše spusťte soubor `build.bat`. Skript se postará o instalaci závislostí a vytvoření `.exe` souboru.

### 3. Výsledek
Po dokončení procesu naleznete finální soubor **Vyzvyvatel_AI_Asistent.exe** ve složce **dist**.
