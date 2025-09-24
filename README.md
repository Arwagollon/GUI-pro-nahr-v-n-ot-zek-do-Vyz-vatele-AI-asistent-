##Popis je prozatimní AI generovaný poslosmyl. Aplikace sama je také z 90 procent AI generovaná, ale ikdyž s mnoha bugy zhruba funkční. 

Poděkování:

Velice děkji discord uživateli @akrej (id 221668967780057088) za vyřešení přihlašování přes API. 

Vyzývatel + AI Asistent pro formátování otázek do .json 
Nástroj pro rychlou a efektivní tvorbu otázek do hry Vyzývatel pomocí umělé inteligence Gemini od Google. Aplikace umožňuje převod textových poznámek na strukturovaný JSON formát a jejich následné nahrání přímo do vaší sady otázek.

<img width="945" height="778" alt="image" src="https://github.com/user-attachments/assets/a13de119-8b3e-4ae0-979d-06042cbc0aa7" />



Funkce 

    Textový editor: Pohodlné psaní a úprava textu s otázkami.

    Správa souborů: Možnost ukládat a načítat rozpracované texty z lokálních souborů.

     Podpora Wordu: Podpora načítání textů přímo z .docx dokumentů.

    AI formátování: Převod textu na strukturovaný JSON formát pomocí Gemini API.

    Náhled a validace: Kontrola správnosti formátu a Zobrazení vygenerovaných otázek před nahráním.

    Nahrání otázek ze souboru: Nahrání hotových otázek do konkrétní sady ve hře Vyzývatel.

    Tmavý režim: Neúspěšný pokus o Moderní a přehledné uživatelské rozhraní

Instalace a nastavení

Pro spuštění projektu z Python skriptu je nutné mít nainstalovaný Python 3.9+ a všechny potřebné závislosti.

    Klonujte repozitář:

    git clone https://[URL_VASEHO_REPOZITARE]
    cd Vyzvyvatel_AI_Asistent

    Nainstalujte závislosti:
    Všechny potřebné knihovny jsou definovány v souboru requirements.txt. Nainstalujte je pomocí jediného příkazu:

    pip install -r requirements.txt

    Spuštění aplikace:

    python vyzyvatel_gui_uploader_alpha_0.1

Jak aplikaci používat

    Příprava textu:

        V záložce "Editor Otázek" napište nebo vložte text s otázkami.

        Pro výběrové otázky označte správnou odpověď (např. hvězdičkou * na začátku nebo na konciřádku), ale jakýkoliv formát označení by měl být přijatelný. Otázky ani nemusí být pod sebou. Stačí že budou nějakým konzistentním způsobm označeny.

        Pro nahrání existujícího textu použijte tlačítko Načíst... v horní liště.

    Generování otázek:

        Klikněte na tlačítko ✨ Generovat s Gemini (API).

        Při prvním použití budete vyzváni k zadání vašeho Google AI (Gemini) API klíče. Můžete ho získat zde.

        AI zpracuje text a automaticky vás přesune do záložky "Nahrávač do Vyzývatele".

    Nahrání do hry:

        V záložce "Nahrávač" zkontrolujte náhled vygenerovaných otázek.(zobrazi se jen otázky ne odpovědi)

        Přihlaste se do svého účtu ve Vyzývateli pomocí tlačítka vpravo nahoře.

        Zadejte ID sady, do které chcete otázky nahrát. nebo vytvořete sadu novou. 

        Klikněte na tlačítko Nahrát otázky.

Kompilace do .exe (pro Windows)

Pokud chcete z aplikace vytvořit samostatný spustitelný soubor, který nevyžaduje instalaci Pythonu, můžete použít přiložený skript.

    Nainstalujte PyInstaller:

    pip install pyinstaller

    Spusťte kompilaci:
    Jednoduše spusťte soubor build.bat. Skript se postará o instalaci závislostí a vytvoření .exe souboru.

    Výsledek:

    Po dokončení procesu naleznete finální soubor Vyzvyvatel_AI_Asistent.exe ve složce dist.


