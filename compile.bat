@echo off
REM Tento skript slouží ke zkompilování aplikace Vyzývatel AI Asistent do jednoho .exe souboru.

REM Nastavení názvu hlavního skriptu a ikony pro snadnější úpravu.
SET SCRIPT_NAME=vyzyvatel_gui_uploader_alpha_0.1.py
SET ICON_PATH=assets/ikona.ico
SET EXE_NAME=Vyzvyvatel_AI_Asistent

echo [INFO] Instaluji potrebne zavislosti z requirements.txt...
pip install -r requirements.txt

REM Kontrola, zda instalace proběhla v pořádku.
if %errorlevel% neq 0 (
    echo [CHYBA] Instalace zavislosti selhala. Zkontrolujte pripojeni k internetu a zda mate nainstalovany Python a pip.
    pause
    exit /b %errorlevel%
)

echo.
echo [INFO] Spoustim kompilaci pomoci PyInstaller...
echo [INFO] Bude vytvoren soubor: %EXE_NAME%.exe

REM Samotný příkaz pro PyInstaller.
pyinstaller --onefile --windowed --icon="%ICON_PATH%" --name="%EXE_NAME%" "%SCRIPT_NAME%"

REM Kontrola, zda kompilace proběhla v pořádku.
if %errorlevel% neq 0 (
    echo [CHYBA] Kompilace selhala. Pro vice informaci projdete vypis chyb vyse.
    pause
    exit /b %errorlevel%
)

echo.
echo [USPECH] Kompilace dokoncena!
echo Spustitelny soubor %EXE_NAME%.exe naleznete ve slozce 'dist'.
echo.
pause
