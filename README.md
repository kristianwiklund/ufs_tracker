# UFS Maritime Notices Tracker

En standalone Python-webbapplikation för att skrapa, lagra och spåra implementering av underrättelser för sjöfarande från Sjöfartsverkets UFS-databas.

## Funktioner

- 🖥️ **Desktop-läge**: Fristående desktopapplikation med pywebview (ingen webbläsare behövs)
- 🌐 **Webb-läge**: Traditionell webbapplikation som öppnas i webbläsare
- 🔍 **Sökning**: Sök efter notiser baserat på sjökortnummer eller båtsportkort
- 💾 **Persistent lagring**: All data sparas i en SQLite-databas
- ✅ **Implementeringsspårning**: Markera varje notis som implementerad per sjökort
- 📝 **Anteckningar**: Lägg till egna anteckningar för varje notis
- 📊 **Statistik**: Se översikt och framsteg per sjökort/båtsportkort
- 🔗 **Direktlänkar**: Klicka dig vidare till originalnotisen på UFS-webbplatsen
- 🏗️ **Byggsystem**: Skapa fristående körbara filer för Windows, Linux och Mac

## Installation och körning

### Alternativ 1: Desktop-applikation (Rekommenderas)

Kör som fristående desktopapplikation (ingen webbläsare behövs):

```bash
pip install -r requirements.txt
python desktop_app.py
```

Applikationen öppnas i ett eget fönster med pywebview.

### Alternativ 2: Webb-läge (Traditionell)

Kör som webbserver och öppna i webbläsare:

```bash
pip install -r requirements.txt
python app.py
```

Gå sedan till `http://127.0.0.1:5000` i din webbläsare.

### Alternativ 3: Använd startup-scriptet

```bash
./start.sh
```

För debug-läge:
```bash
python app.py --debug
# eller
python desktop_app.py  # (desktop-läge har inte --debug än)
```

## Förutsättningar
- Python 3.8 eller senare
- pip (Python package manager)

## Bygg standalone-applikation

Du kan bygga applikationen som fristående körbara filer för Windows, Linux, eller Mac.

### Windows

Bygger både Desktop-version och Konsol-version:

```batch
build-windows.bat
```

Detta skapar:
- `UFS-Tracker.exe` - Desktop-applikation (rekommenderas, öppnas i eget fönster)
- `UFS-Tracker-Console.exe` - Konsol-version (öppnas i webbläsare)

Båda finns i `dist/UFS-Tracker-Portable/` och kan köras utan Python-installation.

**Kör Desktop-versionen**:
```batch
cd dist\UFS-Tracker-Portable
start.bat
```

**Kör Konsol-versionen**:
```batch
cd dist\UFS-Tracker-Portable
start-console.bat
```

### Linux/Mac
```bash
./build-linux.sh
```

Se [BUILD.md](BUILD.md) för detaljerade instruktioner, inklusive:
- Android APK-bygge
- GitHub Actions automatiska byggen
- Distribution och kodsignering

## Användning

### 1. Söka efter notiser

1. Öppna startsidan
2. Ange antingen:
   - **Sjökortnummer** (t.ex. 61, 522, 9221)
   - **Båtsportkort** - Ange kartnamnet (t.ex. "Bsp Stockholm N 2024")
3. Klicka på "Sök och hämta notiser"
4. Applikationen skrapar UFS-webbplatsen och sparar resultaten i databasen

**OBS**: Applikationen hämtar automatiskt alla tillgängliga sjökort och båtsportkort från 
UFS-webbplatsen vid varje sökning. Du behöver inte ange ID-nummer manuellt.

**OBS**: Applikationen hämtar endast notiser från tabellen "Notiser för gällande sjökort". 
Notiser från andra tabeller (som "Tillkännagivanden och notiser utan anknytning till gällande sjökort") 
ignoreras automatiskt.

**OBS**: Applikationen använder nu samma sökning som UFS-webbplatsen:
- URL-parametrar används istället för POST-formulär
- För båtsportkort används `SearchFormModel.SmallCraftChart` med kart-ID
- För sjökort används `SearchFormModel.Chart`
- Kart-ID:n hämtas automatiskt från söksidan varje gång
- Exempel: `https://ufs.sjofartsverket.se/Notice/Search/?SearchFormModel.SmallCraftChart=5231`

### 2. Hantera notiser

1. Gå till "Visa notiser"-sidan
2. Filtrera efter sjökortnummer eller båtsportkort
3. För varje notis kan du:
   - ✅ Bocka i "Implementerad" när ändringen är genomförd
   - 📝 Lägga till anteckningar
   - 🔗 Klicka på "Visa detaljer" för att se originalnotisen

### 3. Visa statistik

1. Gå till "Statistik"-sidan
2. Se översikt över:
   - Totalt antal notiser
   - Antal implementerade notiser
   - Genomförandegrad i procent
   - Fördelning per sjökortnummer
   - Fördelning per båtsportkort
   - Senaste sökningarna

## Databasstruktur

Applikationen använder SQLite med följande tabeller:

### `notices`
- **id**: Unikt ID
- **notice_number**: Faktiskt notisnummer från UFS (används för att bygga länkar)
- **title**: Rubrik på notisen
- **affected_charts**: Lista över berörda sjökort/båtsportkort
- **sjokort_nummer**: Sökt sjökortnummer
- **batsportkort**: Sökt båtsportkort
- **published_date**: Publiceringsdatum
- **area**: Geografiskt område
- **content**: Fullständig text
- **url**: Länk till originalnotisen (genereras automatiskt från notice_number)
- **scraped_date**: När notisen hämtades

### `implementation_status`
- **id**: Unikt ID
- **notice_id**: Referens till notis
- **implemented**: Boolean (0/1)
- **implemented_date**: Datum när notisen implementerades
- **notes**: Användaranteckningar

### `search_history`
- **id**: Unikt ID
- **search_term**: Sökterm (sjökortnummer eller båtsportkort)
- **search_type**: Typ av sökning
- **search_date**: Söktidpunkt
- **results_count**: Antal resultat

## Filstruktur

```
.
├── app.py                 # Huvudapplikation (Flask-server)
├── requirements.txt       # Python-beroenden
├── ufs_notices.db        # SQLite-databas (skapas automatiskt)
├── templates/
│   ├── index.html        # Startsida med sökfunktion
│   ├── notices.html      # Lista över notiser
│   └── statistics.html   # Statistiksida
└── README.md             # Denna fil
```

## Teknisk information

### Backend
- **Flask**: Python web framework
- **SQLite**: Relationsdatabas för persistent lagring
- **Requests**: HTTP-förfrågningar till UFS-webbplatsen
- **BeautifulSoup4**: HTML-parsing och skrapning

### Frontend
- Ren HTML, CSS och JavaScript (ingen externa beroenden)
- Responsiv design som fungerar på desktop och mobila enheter
- Moderna CSS-gradienter och animationer

## Felsökning

### Applikationen startar inte
- Kontrollera att alla beroenden är installerade: `pip install -r requirements.txt --break-system-packages`
- Kontrollera att port 5000 är ledig

### Inga resultat vid sökning
- Kontrollera din internetanslutning
- Verifiera att UFS-webbplatsen är tillgänglig: https://ufs.sjofartsverket.se
- Kontrollera att sjökortnumret eller båtsporkort är korrekt stavat

### Felmeddelande "Failed to access website: 500"
Detta kan intyda att det finns ett problem med UFS-webbplatsen eller att kartnamnet inte kunde mappas korrekt. 
Kör med `--debug` flaggan för att se vilka parametrar som skickas och vad som returneras.

### Felmeddelande "Could not find results table"
Detta kan intyda att sökningen inte returnerade några resultat eller att sidan har ändrad struktur. 
Kör med `--debug` flaggan för att spara HTML-filen och inspektera den.

### Debug-läge
För att få detaljerad information om vad som händer under skrapning:
```bash
python app.py --debug
```
Detta kommer skriva ut:
- Alla HTTP-förfrågningar och svar
- Tabellstruktur och cellinnehåll
- Extraherad information från varje rad
- Databasoperationer

I debug-läge sparas också felaktiga HTTP-svar till `/tmp/ufs_error_XXX.html` och `/tmp/ufs_no_table.html` för inspektion.

### Databasen är tom
- Databasen skapas automatiskt första gången applikationen körs
- Kör en sökning för att börja samla in data

## Säkerhetsöverväganden

- Applikationen körs endast lokalt (127.0.0.1)
- Ingen autentisering krävs (endast för lokal användning)
- Data lagras lokalt i SQLite-databasen
- Inga API-nycklar eller känslig information exponeras

## Begränsningar

- Applikationen kan endast skrapa publika data från UFS-webbplatsen
- Beroende av att UFS-webbplatsens struktur förblir oförändrad
- Ingen realtidsuppdatering - måste söka manuellt för att få nya notiser
- Network-åtkomst är inte aktiverad i denna miljö, så webbskrapning kommer inte att fungera fullt ut

## Framtida förbättringar

Möjliga tillägg:
- 🔔 Automatiska notifikationer vid nya underrättelser
- 📧 E-postpåminnelser för icke-implementerade notiser
- 📤 Export till Excel eller PDF
- 🗓️ Kalenderfunktion för planerad implementering
- 👥 Flervändarsupport med behörigheter
- 🔄 Schemalagd automatisk uppdatering

## Licens

Denna applikation är skapad för privat och professionell användning. Data från Sjöfartsverkets UFS-databas är offentlig information.

## Support

För frågor eller problem, kontrollera först:
1. Att alla beroenden är korrekt installerade
2. Att UFS-webbplatsen är tillgänglig
3. Python-version (3.7+)

## Författare

Skapad för att underlätta hantering och spårning av sjökortsändringar från Sjöfartsverkets UFS-databas.
