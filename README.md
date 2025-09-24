# GUI-pro-nahr-v-n-ot-zek-do-Vyz-vatele-AI-asistent-
Nástroj pro rychlou a efektivní tvorbu otázek do hry Vyzývatel pomocí umělé inteligence Gemini od Google. Aplikace umožňuje převod textových poznámek na strukturovaný JSON formát a jejich následné nahrání přímo do vaší sady otázek.

![Obrázek uživatelského rozhraní aplikace]
Klíčové funkce

    Textový editor: Pohodlné psaní a úprava textu s otázkami.

    Správa souborů: Možnost ukládat a načítat rozpracované texty z lokálních souborů.

    Import z Wordu: Podpora načítání textů přímo z .docx dokumentů.

    AI Generování: Převod textu na strukturovaný JSON formát pomocí Gemini API.

    Náhled a úpravy: Zobrazení vygenerovaných otázek před nahráním.

    Přímé nahrání: Nahrání hotových otázek do konkrétní sady ve hře Vyzývatel.

    Bezpečnost: Aplikace si vyžádá váš souhlas před uložením přihlašovacích údajů nebo API klíče na disk.

    Tmavý režim: Moderní a přehledné uživatelské rozhraní.

Instalace a nastavení

Pro spuštění projektu z Python skriptu je nutné mít nainstalovaný Python 3.9+ a všechny potřebné závislosti.

    Klonujte repozitář:

    git clone https://[URL_VASEHO_REPOZITARE]
    cd Vyzvyvatel_AI_Asistent

    Nainstalujte závislosti:
    Všechny potřebné knihovny jsou definovány v souboru requirements.txt. Nainstalujte je pomocí jediného příkazu:

    pip install -r requirements.txt

    Spuštění aplikace:

    python gui_uploader_V4.3.5.py

Jak aplikaci používat

    Příprava textu:

        V záložce "Editor Otázek" napište nebo vložte text s otázkami.

        Pro výběrové otázky označte správnou odpověď (např. hvězdičkou * na začátku řádku).

        Pro nahrání existujícího textu použijte tlačítko Načíst... v horní liště.

    Generování otázek:

        Klikněte na tlačítko ✨ Generovat s Gemini (API).

        Při prvním použití budete vyzváni k zadání vašeho Google AI (Gemini) API klíče. Můžete ho získat zde.

        AI zpracuje text a automaticky vás přesune do záložky "Nahrávač do Vyzývatele".

    Nahrání do hry:

        V záložce "Nahrávač" zkontrolujte náhled vygenerovaných otázek.

        Přihlaste se do svého účtu ve Vyzývateli pomocí tlačítka vpravo nahoře.

        Zadejte ID sady, do které chcete otázky nahrát.

        Klikněte na tlačítko Nahrát otázky.

Kompilace do .exe (pro Windows)

Pokud chcete z aplikace vytvořit samostatný spustitelný soubor, který nevyžaduje instalaci Pythonu, můžete použít přiložený skript.

    Nainstalujte PyInstaller:

    pip install pyinstaller

    Spusťte kompilaci:
    Jednoduše spusťte soubor build.bat. Skript se postará o instalaci závislostí a vytvoření .exe souboru.

    Výsledek:
    Po dokončení procesu naleznete finální soubor Vyzvyvatel_AI_Asistent.exe ve složce dist.
