# Underrättelser för Sjöfarande (UFS) - Allvarlighetsgrader och Typer

**Version**: 1.0  
**Datum**: 2026-01-29  
**Språk**: Svenska (Swedish)  
**Källa**: Baserat på UKHO Admiralty och Sjöfartsverkets standarder

---

## 📋 Översikt

UFS Tracker klassificerar underrättelser i **tre huvudkategorier** baserat på deras varaktighet och karaktär. Varje typ har olika hanteringskrav och visuell markering.

---

## 🟢 Permanenta Underrättelser (Permanent Corrections)

### Definition

**Permanenta underrättelser** är ändringar som ska införas permanent på sjökortet och gäller tills vidare eller tills ett nytt sjökort ges ut.

### Visuell Markering

**Badge**: 🟢 (Grön cirkel)  
**Tillämpad markering på papperskort**: Magenta bläck (0.18-0.25mm penna)  
**Raderbara**: NEJ - Permanent markering

### Kriterier

Permanenta underrättelser utfärdas för:

✅ **Fysiska förändringar som är permanenta**:
- Ny fyr eller sjömärke installerat
- Djupgående ändrat (muddring, uppgrundning)
- Hamnanläggningar byggda/rivna
- Broar konstruerade
- Kablar eller ledningar lagda
- Vrak som har stabiliserats

✅ **Administrativa förändringar**:
- Ändrade sjötrafikbestämmelser
- Nya farledsystem
- Ändrade trafikseparationsscheman
- Uppdaterade ljuskaraktärer (permanent ändring)

✅ **Kartografiska korrigeringar**:
- Korrigerade djupkurvor
- Namnändringar (officiella)
- Positionskorrigeringar (kartfel)

### Hantering

**Tillämpning**:
1. Märk ändringen på sjökortet med **magenta bläck**
2. Skriv underrättelsens nummer i nedre vänstra hörnet av kortet
3. Anteckna i korrigeringsloggen (NP133A-stil)
4. Markera som "Implementerad" i UFS Tracker

**Borttagning**:
- Tas ALDRIG bort (förutom vid nytt sjökort)
- Räknas mot 6-korrigeringsgränsen
- Förblir tills sjökortet byts ut

**Prioritet**: Normal (om inte specifikt markerad som brådskande)

---

## 🔴 Tillfälliga Underrättelser (Temporary - T)

### Definition

**Tillfälliga underrättelser** (märkta med "T") är ändringar som endast gäller under en **begränsad tidsperiod**. De ska tas bort när giltighetstiden löper ut.

### Visuell Markering

**Badge**: 🔴 T (Röd cirkel med "T")  
**Tillämpad markering på papperskort**: PENNA/BLYERTS (raderbart!)  
**Raderbara**: JA - MÅSTE raderas efter utgång

**Om utgången**:  
**Badge**: 🔴 T (Utgången) (Genomstruken, grå)

### Kriterier

Tillfälliga underrättelser utfärdas för:

✅ **Tidsbegränsade arbeten**:
- Muddring pågår (temporärt hinder)
- Konstruktionsarbete till sjöss
- Kabel- eller rörläggning
- Sprängningsarbeten
- Bärgningsoperationer

✅ **Tillfälliga navigeringshinder**:
- Temporära bojar placerade
- Vrak som ska bärgas inom kort
- Tillfälliga ankringsförbud
- Övningsområden (begränsad tid)
- Skjutövningar (specifika datum)

✅ **Tillfälliga ljusändringar**:
- Fyr släckt för underhåll
- Tillfälligt ljus installerat
- Ljuskaraktär ändrad temporärt

✅ **Väderberoende förändringar**:
- Is-NOTAM (säsongsberoende)
- Översvämningsvarningar
- Extremt lågt vatten

### Giltighetstid

Underrättelsen innehåller vanligen:
- **Startdatum**: "Från och med 2024-06-15"
- **Slutdatum**: "Till och med 2024-09-30"
- **Eller**: "Tills vidare" (men fortfarande tillfällig)

**Exempel från UFS**:
> "Gäller till 2024-12-31"  
> "Valid until further notice"  
> "Under perioden 1 juni - 31 augusti"

### Hantering

**Tillämpning**:
1. Märk ändringen med **BLYERTS** (inte bläck!)
2. Notera utgångsdatum tydligt
3. Arkivera underrättelsen separat (T&P-mapp)
4. Sätt påminnelse för utgångsdatum
5. Markera i UFS Tracker med notis om utgångsdatum

**Borttagning**:
1. När utgångsdatum passerat: **RADERA** markeringen
2. Ta bort från T&P-arkiv
3. Markera som "Utgången" i UFS Tracker
4. Räknas INTE mot 6-korrigeringsgränsen (efter borttagning)

**Viktigt**: Glöm inte att radera! Gamla T-notices kan orsaka navigationsfel.

**Prioritet**: HÖG - Kan påverka omedelbar navigering

---

## 🟡 Preliminära Underrättelser (Preliminary - P)

### Definition

**Preliminära underrättelser** (märkta med "P") är **snabba varningar** baserade på ofullständig information. De ersätts senare av en permanent underrättelse när fullständig undersökning är klar.

### Visuell Markering

**Badge**: 🟡 P (Gul cirkel med "P")  
**Tillämpad markering på papperskort**: PENNA/BLYERTS (raderbart!)  
**Raderbara**: JA - Raderas när permanent version kommer

### Kriterier

Preliminära underrättelser utfärdas för:

✅ **Ej verifierad information**:
- Rapporterat grundområde (ej undersökt)
- Misstänkt vrak
- Rapporterad obstruction
- Potentiellt navigeringshinder

✅ **Ofullständiga mätningar**:
- Snabb djupmätning (ej officiell undersökning)
- Preliminär position (GPS-notering från fartyg)
- Uppskattad höjd/djup

✅ **Brådskande säkerhetsvarningar**:
- Nyupptäckt fara som kräver omedelbar varning
- Allvarlig fara där fullständig undersökning tar tid
- Snabb varning innan fullständiga detaljer finns

### Livscykel

```
1. Preliminary Notice (P) utfärdas
   ↓
2. Undersökning utförs
   ↓
3. Permanent Notice ersätter P-notice
   ↓
4. P-markeringen raderas, permanent markering appliceras
```

**Exempel**:
- **P-Notice 18370P**: "Reported shoal area, depth unknown"
- **Ersätts av Notice 18400**: "Shoal confirmed, depth 3.2m at position..."

### Hantering

**Tillämpning**:
1. Märk med **BLYERTS** (raderbart)
2. Märk tydligt "P" bredvid
3. Arkivera i T&P-mapp
4. **Bevaka** för ersättande permanent notice
5. Markera i UFS Tracker som preliminär

**Ersättning**:
1. När permanent notice kommer: **RADERA** P-markeringen
2. Applicera permanent markering i magenta
3. Notera i loggen att P ersattes av permanent
4. Ta bort P från T&P-arkiv
5. Uppdatera i UFS Tracker (länka till ersättande notice)

**Prioritet**: MYCKET HÖG - Säkerhetsvarningar som kräver omedelbar uppmärksamhet

---

## 📊 Sammanfattning av Skillnader

| Aspekt | 🟢 Permanent | 🔴 Tillfällig (T) | 🟡 Preliminär (P) |
|--------|--------------|-------------------|-------------------|
| **Varaktighet** | Tills vidare | Begränsad tid | Tillfällig (ersätts) |
| **Markering** | Magenta bläck | Blyerts | Blyerts |
| **Raderbar** | NEJ | JA (vid utgång) | JA (vid ersättning) |
| **Arkivering** | Permanent | T&P-mapp | T&P-mapp |
| **Räknas mot 6-gräns** | JA | NEJ (efter radering) | NEJ (efter radering) |
| **Utgångsdatum** | Inget | Ja, specifikt | När ersättning kommer |
| **Prioritet** | Normal | Hög | Mycket hög |
| **Exempel** | Ny fyr | Muddring pågår | Rapporterat vrak |

---

## 🎯 Varför Är Detta Viktigt?

### Säkerhet

**Fel hantering kan leda till**:
- Navigeringshinder som inte är markerade
- Gamla varningar som förvirrar (ej raderade T-notices)
- Förbisedda säkerhetsrisker (ej implementerade P-notices)

### Korrekt Sjökort

**Rätt hantering ger**:
- ✅ Aktuellt sjökort
- ✅ Korrekt information
- ✅ Säker navigering
- ✅ Inspektion-redo dokumentation

### Lagkrav

För **kommersiella fartyg**:
- Krav på uppdaterade sjökort
- PSC-inspektioner kontrollerar korrigeringsloggen
- Måste kunna visa att alla notices är hanterade
- T&P-notices måste vara korrekt arkiverade

---

## 🔍 Hur Identifierar Man Typen?

### I UFS-Databasen

**Nummerformat**:
- `18369` = Permanent (inget suffix)
- `18370T` = Tillfällig (T-suffix)
- `18371P` = Preliminär (P-suffix)

### I UFS Tracker

**Visuella indikatorer**:
- 🟢 = Permanent
- 🔴 T = Tillfällig
- 🟡 P = Preliminär
- 🔴 T (Utgången) = Utgången tillfällig (ska raderas)

### I Notice-Titel

**Nyckelord för Tillfällig (T)**:
- "Temporary"
- "Under period"
- "Tills vidare"
- "Gäller till [datum]"
- "During construction"
- "Works in progress"

**Nyckelord för Preliminär (P)**:
- "Preliminary"
- "Reported"
- "Unconfirmed"
- "Position approximate"
- "Depth uncertain"
- "Subject to confirmation"

---

## 📝 Praktiska Exempel

### Exempel 1: Permanent Notice

**Notice 18500**  
**Titel**: "Stockholm. Ny ledlinje etablerad"  
**Typ**: 🟢 Permanent  
**Handling**:
1. Markera ny ledlinje med magenta bläck
2. Skriv "18500" i nedre vänstra hörnet
3. Anteckna i korrigeringsloggen
4. Markera som implementerad i UFS Tracker
5. **Radera ALDRIG**

---

### Exempel 2: Tillfällig Notice

**Notice 18501T**  
**Titel**: "Muddring i Karlskrona hamn. Gäller till 2024-09-30"  
**Typ**: 🔴 T (Tillfällig)  
**Handling**:
1. Markera muddringområde med BLYERTS
2. Skriv "18501T" och "Utgår 2024-09-30"
3. Arkivera notice i T&P-mapp
4. Markera i UFS Tracker med utgångsdatum
5. **2024-10-01**: RADERA markeringen
6. Ta bort från T&P-arkiv

---

### Exempel 3: Preliminär Notice

**Notice 18502P**  
**Titel**: "Rapporterat grundområde öster om Sandhamn. Position approximativ"  
**Typ**: 🟡 P (Preliminär)  
**Handling**:
1. Markera område med BLYERTS
2. Skriv "18502P" och "PRELIMINARY"
3. Arkivera i T&P-mapp
4. Markera i UFS Tracker som preliminär
5. **Bevaka** UFS för ersättande notice
6. När **Notice 18550** kommer (permanent):
   - RADERA "18502P" markeringen
   - Markera med magenta enligt 18550
   - Länka i UFS Tracker: "18502P ersatt av 18550"

---

## ⚠️ Vanliga Misstag

### ❌ Fel 1: Markera T-notice i Magenta
**Problem**: Kan inte raderas senare  
**Rätt**: Använd ALLTID blyerts för T och P

### ❌ Fel 2: Glömma Radera Utgångna T-Notices
**Problem**: Gamla varningar förvirrar, fel information  
**Rätt**: Sätt påminnelser, kontrollera regelbundet

### ❌ Fel 3: Inte Bevaka P-Notices
**Problem**: Missar permanent ersättning  
**Rätt**: Bevaka UFS för uppföljning

### ❌ Fel 4: Räkna T/P mot 6-Gränsen
**Problem**: Byter sjökort i onödan  
**Rätt**: Endast permanenta räknas (efter T/P raderats)

---

## 🛠️ Användning i UFS Tracker

### Automatisk Identifiering

UFS Tracker identifierar automatiskt notice-typ från nummer:
- Suffix "T" → Tillfällig
- Suffix "P" → Preliminär
- Inget suffix → Permanent

### Utgångsspårning

För tillfälliga notices:
- Tracker försöker extrahera utgångsdatum från titel/innehåll
- Visar varning när utgångsdatum närmar sig
- Markerar som "Utgången" efter datum

### Ersättningslänkar

För preliminära notices:
- Tracker kan länka till ersättande permanent notice
- Visar historik: "P18502 → 18550"
- Hjälper hålla reda på uppdateringar

---

## 📚 Referenser

### Internationella Standarder
- **UKHO NP294**: "Admiralty Guide to the Practical Use of Charts"
- **UKHO NP133A**: "Chart Correction Log and Folio Index"
- **IALA**: Recommendations on Marine Signal Stations
- **IMO**: International Maritime Organization Guidelines

### Svenska Källor
- **Sjöfartsverket**: https://ufs.sjofartsverket.se
- **Trafikföreskrifter för sjöfart**: SJÖFS regulations
- **Svenska Krysssarklubben**: Båtsportkort guidelines

---

## 📞 Support

Om du är osäker på:
- Notice-typ
- Hur en notice ska hanteras
- Utgångsdatum tolkning
- Ersättningsnotices

**Kontakta**:
- Sjöfartsverket: https://www.sjofartsverket.se
- UFS Tracker GitHub: https://github.com/kristianwiklund/ufs_tracker/issues

---

**Viktigt**: Detta är en guide för **hobby- och fritidsbruk**. För **kommersiell sjöfart** måste fullständiga SOLAS- och STCW-krav följas, inkl. officiell certifiering och inspektion av korrigeringsrutiner.

**Senast uppdaterad**: 2026-01-29  
**Version**: 1.0  
**Språk**: Svenska
