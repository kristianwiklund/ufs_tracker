# UFS Maritime Notices Tracker - Snabbstartsguide

## 🚀 Snabbstart (5 minuter)

### 1. Installera Python-beroenden
```bash
pip install -r requirements.txt
```

### 2. Starta applikationen
```bash
python app.py
```

### 3. Öppna i webbläsaren
Navigera till: **http://127.0.0.1:5000**

---

## 📁 Projektstruktur

```
ufs-tracker/
├── app.py                  # Huvudapplikation (Flask-server)
├── requirements.txt        # Python-beroenden
├── start.sh               # Startskript (chmod +x start.sh)
├── init_demo.py           # Skapa demo-data
├── README.md              # Teknisk dokumentation
├── USER_GUIDE.md          # Användarguide
└── templates/
    ├── index.html         # Startsida med sökfunktion
    ├── notices.html       # Lista över notiser med checkboxar
    └── statistics.html    # Statistik och översikt
```

---

## ✨ Huvudfunktioner

### 🔍 Sökfunktion
- Sök efter sjökortnummer (t.ex. 61, 522, 9221)
- Sök efter båtsportkort (t.ex. "Bsp Stockholm N 2024")
- Automatisk skrapning från UFS-webbplatsen
- Lagrar alla hämtade notiser i SQLite-databas

### ✅ Implementeringsspårning
- Checkbox för varje notis (markera som implementerad)
- Automatisk datumstämpling när notis bockas av
- Anteckningsfält för egna kommentarer
- Visuell färgkodning (grön = genomförd)

### 📊 Statistik
- Total översikt över alla notiser
- Implementeringsgrad i procent
- Fördelning per sjökortnummer
- Fördelning per båtsportkort
- Sökhistorik

### 💾 Persistent lagring
- All data sparas i SQLite-databas (ufs_notices.db)
- Ingen datakoppling krävs efter att notiser hämtats
- Säkerhetskopiering: kopiera ufs_notices.db

---

## 🎯 Exempel på användning

### Scenario 1: Båtägare med båtsportkort
```
1. Gå till startsidan
2. Välj "Bsp Stockholm N 2024" från dropdown-menyn
3. Klicka "Sök och hämta notiser"
4. Gå igenom resultaten och bocka av när du uppdaterat dina kort
```

### Scenario 2: Professionell sjöfarare med sjökort
```
1. Gå till startsidan
2. Ange sjökortnummer "61" (Stockholms inlopp)
3. Klicka "Sök och hämta notiser"
4. Se alla ändringar för sjökortet
5. Markera som implementerad när du uppdaterat papperkortet
```

### Scenario 3: Flotta med flera sjökort
```
1. Sök efter sjökort 61, 522, 933, etc.
2. Använd filter för att se endast ej-implementerade
3. Fördela arbetet: lägg till anteckningar vem som ansvarar
4. Följ upp via statistiksidan
```

---

## 🔧 Tekniska detaljer

### Beroenden
- **Flask 3.0.0**: Web framework
- **requests 2.31.0**: HTTP-förfrågningar
- **beautifulsoup4 4.12.2**: HTML-parsing

### Databas (SQLite)
- **notices**: Alla hämtade notiser
- **implementation_status**: Implementeringsstatus per notis
- **search_history**: Sökhistorik

### Portar
- Default: 5000
- Ändra i app.py om port 5000 är upptagen

---

## ⚠️ Viktiga anmärkningar

### Begränsningar
1. **Nätverksberoende vid skrapning**: Kräver internetanslutning för att hämta nya notiser
2. **Webbplatsstruktur**: Om UFS ändrar sin webbplats kan skrapningen sluta fungera
3. **Endast lokal användning**: Applikationen körs lokalt, ingen fjärråtkomst
4. **Ingen autentisering**: Säker endast för lokal användning

### Säkerhet
- Applikationen lyssnar endast på 127.0.0.1 (localhost)
- All data lagras lokalt
- Inga API-nycklar eller känslig information exponeras

---

## 🆘 Felsökning

### Problem: ModuleNotFoundError
```bash
# Lösning: Installera beroenden igen
pip install -r requirements.txt --break-system-packages
```

### Problem: Port 5000 redan används
```python
# Ändra i app.py, sista raden:
app.run(debug=True, host='127.0.0.1', port=5001)  # Ändra till 5001
```

### Problem: Database locked
```bash
# Lösning: Stäng andra instanser av applikationen
# Eller: Ta bort ufs_notices.db och starta om
```

### Problem: Inga sökresultat
- Kontrollera internetanslutning
- Verifiera att UFS-webbplatsen är tillgänglig
- Kontrollera att sjökortnummer/båtsportkort är korrekt stavat

---

## 📝 Demo-data

För att testa applikationen med exempeldata:

```bash
python init_demo.py
```

Detta skapar tre exempel-notiser:
- T123/24: Byte av sjömärke (Sjökort 61) - Implementerad
- P456/24: Ny fyr (Sjökort 61) - Ej implementerad
- T789/24: Upphävd varning (Sjökort 933) - Ej implementerad

---

## 📖 Mer information

- **Fullständig dokumentation**: Se README.md
- **Användarguide**: Se USER_GUIDE.md
- **UFS-webbplats**: https://ufs.sjofartsverket.se

---

## 🎉 Lycka till!

Din maritima underrättelsehantering är nu mer organiserad än någonsin!

**Tips**: Sök efter dina vanligaste sjökort varje vecka för att hålla dig uppdaterad med de senaste ändringarna.

---

**Version**: 1.0  
**Skapad**: 2026-01-27  
**Plattform**: Python 3.7+, Flask, SQLite
