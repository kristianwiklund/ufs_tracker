# UFS Maritime Notices Tracker - Användarguide

## Innehållsförteckning
1. [Komma igång](#komma-igång)
2. [Sökfunktionen](#sökfunktionen)
3. [Hantera notiser](#hantera-notiser)
4. [Statistik och rapporter](#statistik-och-rapporter)
5. [Tips och tricks](#tips-och-tricks)

---

## Komma igång

### Installation och start

1. **Installera beroenden**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Starta applikationen**:
   ```bash
   python app.py
   ```
   
   Eller använd startskriptet:
   ```bash
   ./start.sh
   ```

3. **Öppna webbläsaren**:
   Navigera till `http://127.0.0.1:5000`

### Första gången

När du startar applikationen första gången kommer en tom SQLite-databas att skapas automatiskt. Du kan antingen:
- Börja söka efter notiser direkt
- Köra demo-skriptet för att få exempeldata: `python init_demo.py`

---

## Sökfunktionen

### Sida: Hem (/)

På startsidan kan du söka efter underrättelser från Sjöfartsverkets UFS-databas.

#### Sökalternativ

**1. Sjökortnummer**
- Ange ett sjökortnummer (t.ex. 61, 522, 9221)
- Sök efter notiser som berör det specifika sjökortet
- Exempel:
  - `61` - Stockholms inlopp
  - `933` - Göteborg
  - `522` - Vänern

**2. Båtsportkort**
- Välj från dropdown-menyn
- Tillgängliga båtsportkort inkluderar:
  - Bsp Stockholm N 2024
  - BSP Västkusten N 2025
  - Bsp Ostkusten 2025
  - m.fl.

#### Så här söker du

1. Fyll i **antingen** sjökortnummer **eller** båtsportkort
2. Klicka på "Sök och hämta notiser"
3. Applikationen kommer att:
   - Skrapa UFS-webbplatsen
   - Hämta alla relevanta notiser
   - Spara dem i databasen
   - Omdirigera dig till notislistan

#### Vad händer vid sökning?

- **Duplicering**: Om en notis redan finns i databasen kommer den inte att dupliceras
- **Laddar**: En laddningsanimation visas under skrapningen
- **Resultat**: Ett meddelande visar hur många notiser som hittades och sparades

---

## Hantera notiser

### Sida: Visa notiser (/notices)

På denna sida visas alla hämtade notiser med möjlighet att spåra implementering.

#### Filteralternativ

Överst på sidan kan du filtrera notiser:
- **Sjökortnummer**: Visa endast notiser för ett specifikt sjökort
- **Båtsportkort**: Visa endast notiser för ett specifikt båtsportkort
- **Visa implementerade**: Bocka ur för att endast se icke-implementerade notiser

#### Notiskort

Varje notis visas i ett kort med följande information:

**Huvudinformation**
- **Notisnummer**: Unikt ID från UFS (t.ex. T123/24)
- **Rubrik**: Titel på underrättelsen
- **Sjökortnummer**: Vilket sjökort som berörs
- **Båtsportkort**: Vilket båtsportkort som berörs (om relevant)
- **Publicerad**: När notisen publicerades
- **Hämtad**: När notisen skrapades till databasen

**Innehåll**
- Fullständig text från notisen visas i en grå box
- Scrollbar visas om texten är längre än utrymmet

**Åtgärder**

1. **Implementerad-checkbox**:
   - Bocka i när du har genomfört ändringen på ditt sjökort
   - Status sparas automatiskt
   - Kortet blir grönt när det är implementerat
   - Datum för implementering registreras automatiskt

2. **Anteckningar**:
   - Lägg till egna anteckningar (t.ex. "Inritat på papperskort", "Kontrollera GPS-koordinater")
   - Sparas automatiskt när du klickar utanför fältet

3. **Visa detaljer**:
   - Klicka för att öppna originalnotisen på UFS-webbplatsen
   - Öppnas i ny flik

#### Färgkodning

- **Vit bakgrund**: Ej implementerad notis
- **Grön bakgrund**: Implementerad notis med grön ✓-märkning

---

## Statistik och rapporter

### Sida: Statistik (/statistics)

Denna sida ger en översikt över dina notiser och implementeringsstatus.

#### Statistikkort

Fyra stora kort visar:
1. **Totalt antal notiser**: Alla notiser i databasen
2. **Implementerade**: Antal genomförda notiser
3. **Återstår**: Antal väntande notiser
4. **Genomförandegrad**: Procent av implementerade notiser

#### Implementeringsgrad

- Visuell förloppsindikator (grön stapel)
- Visar procentuell färdigställning
- Uppdateras i realtid baserat på dina checkboxar

#### Notiser per sjökortnummer

Tabell som visar:
- Vilka sjökortnummer du har notiser för
- Antal notiser per sjökortnummer
- Sorterat efter antal (flest först)

#### Notiser per båtsportkort

Tabell som visar:
- Vilka båtsportkort du har notiser för
- Antal notiser per båtsportkort
- Sorterat efter antal

#### Senaste sökningarna

Historik över dina senaste 10 sökningar:
- **Sökterm**: Vad du sökte efter
- **Typ**: sjokort eller batsportkort
- **Datum**: När sökningen gjordes
- **Antal resultat**: Hur många notiser som hittades

---

## Tips och tricks

### Effektiv användning

**1. Regelbunden uppdatering**
- Sök efter dina vanligaste sjökort/båtsportkort regelbundet
- Rekommendation: En gång i veckan eller vid varje seglatssäsong

**2. Prioritering**
- Filtrera bort implementerade notiser för att se vad som återstår
- Använd anteckningsfältet för att markera prioritet

**3. Systematiskt arbetssätt**
- Bocka av notiser direkt när du uppdaterat ditt sjökort
- Lägg till anteckningar om vad du gjorde

**4. Grupperade uppdateringar**
- Sök efter flera sjökort
- Filtrera och gå igenom dem systematiskt
- Bocka av när du är klar

### Vanliga användningsfall

**För båtägare**:
1. Sök efter ditt vanligaste båtsportkort
2. Bocka av ändringar när du uppdaterat dina plotter/kartor
3. Skriv anteckningar om viktiga ändringar

**För professionella sjöfarare**:
1. Sök efter alla relevanta sjökort för ditt verksamhetsområde
2. Håll koll på implementeringsgraden
3. Använd statistiksidan för att rapportera till överordnade

**För marinor och båtklubbar**:
1. Håll en central databas för alla lokala sjökort
2. Dela ansvaret för att uppdatera olika områden
3. Använd anteckningar för att dokumentera vem som gjorde vad

### Databashantering

**Säkerhetskopiering**:
```bash
cp ufs_notices.db ufs_notices_backup_$(date +%Y%m%d).db
```

**Återställa från backup**:
```bash
cp ufs_notices_backup_20240115.db ufs_notices.db
```

**Rensa gammal data** (om databas blir för stor):
```sql
DELETE FROM notices WHERE scraped_date < '2023-01-01';
```

### Felsökning

**Problem: Inga resultat vid sökning**
- Lösning: Kontrollera internetanslutning
- Lösning: Verifiera att sjökortnummer/båtsportkort är korrekt

**Problem: Applikationen startar inte**
- Lösning: Kontrollera att port 5000 är ledig
- Lösning: Installera om beroenden: `pip install -r requirements.txt`

**Problem: Checkboxar sparas inte**
- Lösning: Kontrollera att du har skrivbehörighet till databasen
- Lösning: Starta om applikationen

### Keyboard shortcuts

Även om det inte finns inbyggda genvägar kan du använda webbläsarens funktioner:
- `Ctrl+F` - Sök på sidan
- `Ctrl+R` - Uppdatera sidan
- `Ctrl+T` - Ny flik (för att öppna UFS-länkar)

---

## Support och feedback

### Vanliga frågor

**F: Kan jag använda applikationen offline?**
S: Ja, efter att notiser har hämtats kan du se och hantera dem offline. Du behöver bara internet för att skrapa nya notiser.

**F: Sparas mina anteckningar lokalt?**
S: Ja, all data sparas i SQLite-databasen på din dator.

**F: Kan flera användare dela samma databas?**
S: Inte i nuvarande version. Varje installation har sin egen databas.

**F: Hur ofta uppdateras UFS-databasen?**
S: Sjöfartsverket uppdaterar löpande. Kör nya sökningar regelbundet för att få senaste ändringarna.

**F: Vad händer om UFS ändrar sin webbplats?**
S: Skrapningen kan sluta fungera. Kontakta utvecklaren för uppdatering av skrapningskoden.

---

## Avancerad användning

### API-endpoints

Om du vill bygga egna integrations kan du använda:

```
GET  /                    - Startsida
POST /search              - Sök och hämta notiser
GET  /notices             - Lista notiser (med filter)
POST /update_status/<id>  - Uppdatera implementeringsstatus
GET  /statistics          - Statistik och historik
```

### Databasschema

Se README.md för fullständigt databasschema och fältdefinitioner.

---

**Version**: 1.0  
**Senast uppdaterad**: 2026-01-27
