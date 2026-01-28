
# Licens:

MIT - Läs: Skyll dig själv om du går på grund på grund av att du litar på det här fulhacket...


# Dokumentation som Claude har genererat, ej kontrollerad över huvud taget:

## UFS Maritime Notices Tracker

En standalone Python-webbapplikation för att skrapa, lagra och spåra implementering av underrättelser för sjöfarande från Sjöfartsverkets UFS-databas.

## Funktioner

- 🔍 **Sökning**: Sök efter notiser baserat på sjökortnummer eller båtsportkort
- 💾 **Persistent lagring**: All data sparas i en SQLite-databas
- ✅ **Implementeringsspårning**: Markera varje notis som implementerad med checkboxar
- 📝 **Anteckningar**: Lägg till egna anteckningar för varje notis
- 📊 **Statistik**: Se översikt över totalt antal notiser och implementeringsgrad
- 🔗 **Direktlänkar**: Klicka dig vidare till originalnotisen på UFS-webbplatsen

## Installation

### Förutsättningar
- Python 3.7 eller senare
- pip (Python package manager)

### Steg för steg

1. **Installera Python-beroenden**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Kör applikationen**:
   ```bash
   python app.py
   ```
   
   Eller använd startup-scriptet:
   ```bash
   ./start.sh
   ```
   
   För att aktivera debug-utskrifter:
   ```bash
   python app.py --debug
   # eller
   ./start.sh --debug
   ```

3. **Öppna webbläsaren**:
   Gå till `http://127.0.0.1:5000`

## Användning

### 1. Söka efter notiser

1. Öppna startsidan
2. Välj sjökort från dropplistan
3. Klicka på "Sök och hämta notiser"
4. Applikationen skrapar UFS-webbplatsen och sparar resultaten i databasen

**OBS**: Applikationen hämtar automatiskt alla tillgängliga sjökort och båtsportkort från 
UFS-webbplatsen vid varje sökning. Du behöver inte ange ID-nummer manuellt.

**OBS**: Applikationen hämtar endast notiser från tabellen "Notiser för gällande sjökort". 
Notiser från andra tabeller (som "Tillkännagivanden och notiser utan anknytning till gällande sjökort") 
ignoreras automatiskt.

### 2. Hantera notiser

1. Gå till "Visa notiser"-sidan
2. Filtrera efter nedladdad data per sjökortnummer eller båtsportkort
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
   - Fördelning per kort och genomförande per kort

## Detaljer

Se promptfilen för detaljer.
