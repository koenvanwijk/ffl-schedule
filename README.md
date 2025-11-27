# First Lego League Tournament Scheduler

Een complete planning tool voor First Lego League toernooien die gebruik maakt van Google OR-Tools constraint programming om een optimaal wedstrijdschema te maken met **zowel matches (wedstrijden) als jury sessies**.

## ✨ Functionaliteit

### Matches (Wedstrijden)
- Plant **10-40 teams** over **4-10 tafels**
- Elk team speelt **4 wedstrijden**
- Teams spelen bij voorkeur op **verschillende tafels** voor maximale variatie
- **Unieke tegenstanders**: elk team speelt maximaal 1x tegen dezelfde tegenstander
- Wedstrijd duur: **7 minuten** (configureerbaar)
- **Tafel paren**: tafels werken in paren (beide bezet of beide leeg)

### Jury Sessies
- Plant **jury sessies** in **4-10 jury rooms**
- Elk team heeft **1 jury sessie** (configureerbaar)
- Jury sessie duur: **42 minuten** (configureerbaar)
- **Gesynchroniseerde rondes**: jury sessies starten in gecoördineerde rondes

### Planning Optimalisatie
- **Minimale buffer tijd** tussen activiteiten (standaard 30 minuten)
- **Pauze ondersteuning**: automatische pauze toevoeging in het schema
- Voorkomt overlap tussen matches en jury sessies
- Optimaliseert voor minimale tafelwisselingen
- **Tafel paren**: maximaal gebruik van tafel paren
- **Exporteert naar JSON** voor verder gebruik

### Automatische Testing
- **GitHub Actions**: automatisch schema genereren en testen bij elke commit
- **Test suite**: controleert alle constraints en optimalisaties
- Verificatie van overlaps, buffers, en jury rondes

## 📦 Installatie

### Optie 1: Met Conda (aanbevolen)
```bash
conda create -n ffl python=3.11 -y
conda activate ffl
pip install ortools
```

### Optie 2: Met pip
```bash
pip install -r requirements.txt
```

## 🚀 Gebruik

### Snelstart - Complete Scheduler (aanbevolen)

**Voor complete toernooi planning met matches EN jury sessies:**

1. Pas `config.py` aan met jouw toernooi gegevens:

```python
NUM_TEAMS = 40              # Aantal teams (10-40)
NUM_TABLES = 6              # Aantal tafels (4-10)
NUM_JURY_ROOMS = 8          # Aantal jury rooms (4-10)
NUM_TIMESLOTS = 40          # Aantal tijdsloten (verhoog indien nodig)
MATCHES_PER_TEAM = 4        # Wedstrijden per team
JURY_SESSIONS_PER_TEAM = 1  # Jury sessies per team
MATCH_DURATION = 7          # Minuten per wedstrijd
JURY_DURATION = 42          # Minuten per jury sessie
MINIMUM_BUFFER_TIME = 30    # Min. minuten tussen activiteiten

# Pauze instellingen
BREAK_ENABLED = True        # Pauze inschakelen
BREAK_START_TIME = 168      # Start tijd pauze (minuten)
BREAK_DURATION = 30         # Duur pauze (minuten)

# Tafel paren (beide tafels tegelijk gebruiken)
TABLE_PAIRS = [
    (0, 1),   # Tafel 1 en 2
    (2, 3),   # Tafel 3 en 4
    (4, 5),   # Tafel 5 en 6
]
```

2. Voer uit:

```bash
python complete_scheduler.py
```

Dit genereert een compleet JSON bestand met:
- ✅ Alle wedstrijden (matches) per team
- ✅ Alle jury sessies per team
- ✅ Optimale timing met buffer tijd
- ✅ Unieke tegenstanders (elk team speelt max 1x tegen zelfde tegenstander)
- ✅ Maximum tafel variatie (teams spelen bij voorkeur op verschillende tafels)
- ✅ Minimale tafelwisselingen

### Scripts

- **`complete_scheduler.py`** - 🎯 Complete scheduler met matches + jury sessies
- **`test_schedule.py`** - Test suite voor schema validatie
- **`config.py`** - Configuratie voor toernooi instellingen

### Schema Testen

Test een gegenereerd schema:

```bash
python test_schedule.py schedule-complete-*.json
```

Dit controleert:
- ✅ Geen overlappende matches of jury sessies
- ✅ Minimale buffer tijd tussen activiteiten
- ✅ Gesynchroniseerde jury rondes
- ✅ Correcte tafel paar gebruik
- ✅ Unieke tegenstanders (elk team max 1x tegen zelfde tegenstander)
- ✅ Maximum tafel variatie (teams spelen op verschillende tafels)
- ✅ Alle teams hebben juiste aantal matches en jury sessies

## 🤖 GitHub Actions

Het project bevat een GitHub Actions workflow die automatisch:
- Schema genereert bij elke commit
- Alle tests uitvoert
- Het schema als artifact opslaat (30 dagen)

**Handmatig starten:**
1. Ga naar de "Actions" tab in GitHub
2. Selecteer "FLL Tournament Scheduler"
3. Klik "Run workflow"

De gegenereerde schema's zijn te downloaden als artifacts na elke run.

### JSON Output genereren

De complete scheduler genereert automatisch een JSON bestand met het formaat:
- `constraintConfiguration` - Timing configuratie (wedstrijd/jury duur, buffer tijd)
- `tableList` - Alle tafels met hun table pairs
- `juryList` - Alle jury rooms
- `teamList` - Alle teams
- `tableTimeslotList` - Alle beschikbare timeslots per tafel
- `juryTimeslotList` - Alle jury sessie tijden
- `teamTableAllocationList` - **Match toewijzingen** (team → tafel → tijd)
- `teamJuryAllocationList` - **Jury toewijzingen** (team → jury room → tijd)

## 📊 Output

Het programma genereert:

1. **Complete JSON export** (`schedule-complete-*.json`)
   - Matches: welk team speelt wanneer op welke tafel
   - Jury sessies: welk team heeft wanneer welke jury sessie
   - Volledige timing informatie in minuten
   - Klaar voor import in andere systemen

2. **Console output met statistieken**:
   - Status (OPTIMAAL/HAALBAAR)
   - Oplostijd
   - Aantal matches en jury sessies
   - Tafel verdeling per team

## 💡 Voorbeeld Output

```
🏆 FLL COMPLETE TOURNAMENT SCHEDULER
======================================================================
📋 Configuratie:
   Teams: 40
   Tafels: 6
   Jury Rooms: 8
   Tijdsloten: 30
   Wedstrijden per team: 4
   Jury sessies per team: 1
   Min. buffer tijd: 30 min
======================================================================

� Capaciteit check:
   Matches: 160 nodig, 180 beschikbaar
   Jury sessies: 40 nodig, 240 beschikbaar
   ✅ Capaciteit OK

✅ Oplossing gevonden!

======================================================================
📊 STATISTIEKEN
======================================================================
Status: OPTIMAAL ✅
Oplostijd: 4.78 seconden
Conflicten: 0
Branches: 5,346

Totaal matches: 160
Totaal jury sessies: 40
Unieke tegenstanders: 78 matchups (0 herhalingen)

Tafel verdeling:
  Teams op 2 tafels: 3
  Teams op 3 tafels: 11
  Teams op 4 tafels: 26
  
Tafel paar gebruik: 96.6% correct

💾 Schema opgeslagen als: schedule-complete-2025-11-27T14-27-53.json
```

## ⚙️ Configuratie voorbeelden

### Klein toernooi (12 teams)
```python
NUM_TEAMS = 12
NUM_TABLES = 4
NUM_JURY_ROOMS = 4
NUM_TIMESLOTS = 10
MINIMUM_BUFFER_TIME = 30
```

### Middelgroot toernooi (24 teams)
```python
NUM_TEAMS = 24
NUM_TABLES = 6
NUM_JURY_ROOMS = 6
NUM_TIMESLOTS = 20
MINIMUM_BUFFER_TIME = 30
```

### Groot toernooi (40 teams)
```python
NUM_TEAMS = 40
NUM_TABLES = 6
NUM_JURY_ROOMS = 8
NUM_TIMESLOTS = 30
MINIMUM_BUFFER_TIME = 30  # Meer rust tussen activiteiten
```

## 🔧 Tips & Troubleshooting

### Geen oplossing gevonden?

Als er geen oplossing wordt gevonden, probeer:
- ✅ **Verhoog NUM_TIMESLOTS** (meest effectief) - voeg 5-10 tijdsloten toe
- ✅ Verlaag MINIMUM_BUFFER_TIME (van 30 naar 20 minuten)
- ✅ Verhoog MAX_SOLVE_TIME (van 120 naar 300 seconden)
- ✅ Voeg meer tafels of jury rooms toe
- ✅ Verlaag het aantal teams
- ✅ **Voor schema's met pauze**: de pauze wordt in de output toegevoegd, niet als constraint

### Vuistregel voor aantal tijdsloten

**Voor matches:**
Minimaal = `(aantal_teams × matches_per_team) / aantal_tafels`

**Voor jury sessies:**
Minimaal = `(aantal_teams × jury_sessions_per_team) / aantal_jury_rooms`

**Totaal aanbevolen:**
Neem het maximum van beide + **5-10 extra tijdsloten** voor flexibiliteit

**Voorbeeld:** 40 teams, 6 tafels, 8 jury rooms
- Matches: (40 × 4) / 6 = 27 tijdsloten
- Jury: (40 × 1) / 8 = 5 tijdsloten
- **Aanbevolen:** 35-40 tijdsloten

### Pauze configuratie

De pauze wordt **niet als constraint** gebruikt (te restrictief), maar wordt **in de output toegevoegd**:
- Alle activiteiten voor `BREAK_START_TIME` blijven ongewijzigd
- Alle activiteiten na `BREAK_START_TIME` krijgen `+BREAK_DURATION` minuten
- Resultaat: een natuurlijke pauze periode zonder activiteiten

### Tafel paren

Tafel paren zorgen ervoor dat tafels samen gebruikt worden:
```python
TABLE_PAIRS = [
    (0, 1),   # Tafel 1 en 2 werken samen
    (2, 3),   # Tafel 3 en 4 werken samen
]
```
De optimizer probeert beide tafels van een paar tegelijk te gebruiken (of beide leeg te laten).
- Aanbevolen: 30-35 tijdsloten

### Teams op te veel tafels?

Als teams op meer dan 2 tafels spelen:
- Verhoog NUM_TIMESLOTS (geeft meer flexibiliteit voor optimalisatie)
- De optimizer probeert dit automatisch te minimaliseren

### Timing configuratie

De timing werkt als volgt:
- Elk **match timeslot** = MATCH_DURATION (7 min)
- Elk **jury timeslot** = JURY_DURATION (42 min)
- **Buffer tijd** = MINIMUM_BUFFER_TIME (30 min) tussen alle activiteiten van een team
- Teams kunnen niet tegelijk een match EN jury sessie hebben

## 📁 Bestandsstructuur

```
ffl-schedule/
├── .github/workflows/
│   └── schedule.yml             # 🤖 GitHub Actions workflow
├── config.py                    # ⚙️ Configuratie (pas dit aan!)
├── complete_scheduler.py        # 🎯 Complete scheduler (matches + jury)
├── test_schedule.py             # ✅ Test suite voor validatie
├── requirements.txt             # 📦 Dependencies
├── schedule-complete-*.json     # 💾 Gegenereerd JSON schema
└── README.md                    # 📖 Deze documentatie
```

## 🧮 Hoe werkt het?

De scheduler gebruikt **Constraint Programming** (CP-SAT solver van Google OR-Tools):

### 1. Harde Constraints (moeten voldaan worden)
**Voor Matches:**
- Elk team speelt exact 4 wedstrijden
- Maximaal 1 team per tafel per tijdslot
- Een team kan maar op 1 tafel per tijdslot spelen

**Voor Jury Sessies:**
- Elk team heeft exact 1 jury sessie
- Maximaal 1 team per jury room per tijdslot
- Een team kan maar in 1 jury room per tijdslot zijn

**Overlap Preventie:**
- Een team kan niet tegelijk een match EN jury sessie hebben
- Minimale buffer tijd tussen alle activiteiten van een team

### 2. Zachte Constraints (optimalisatie doelen)
**Prioriteit 1 (hoogste):**
- Tafel paren: beide tafels van een paar tegelijk gebruiken (of beide leeg)

**Prioriteit 2:**
- Minimaliseer aantal verschillende tafels per team
- Bij voorkeur speelt elk team op dezelfde tafel

**Jury rondes:**
- Jury sessies starten in gesynchroniseerde rondes
- Maximaal aantal teams per ronde = aantal jury rooms

De solver zoekt automatisch naar de beste oplossing binnen de gestelde grenzen en vindt een optimale balans tussen matches en jury sessies.

## 📄 JSON Output Structuur

Het gegenereerde JSON bestand bevat:

```json
{
  "constraintConfiguration": {
    "matchDuration": 7,
    "juryDuration": 42,
    "minimumBreakDuration": 30,
    "startTime": "09:30"
  },
  "tableList": [...],           // Alle tafels
  "juryList": [...],            // Alle jury rooms  
  "teamList": [...],            // Alle teams
  "tableTimeslotList": [...],   // Match tijdsloten
  "juryTimeslotList": [...],    // Jury tijdsloten
  "teamTableAllocationList": [...],  // Match planning
  "teamJuryAllocationList": [...]    // Jury planning
}
```

Elk team krijgt:
- 4 entries in `teamTableAllocationList` (4 matches)
- 1 entry in `teamJuryAllocationList` (1 jury sessie)

Met buffer tijd ertussen gegarandeerd!

## 🤝 Contributing

Suggesties en verbeteringen zijn welkom! Maak een issue of pull request aan.

## 📜 Licentie

Free to use voor FLL toernooien. Gebaseerd op OR-Tools voorbeelden.

## 🔗 Links

- [Google OR-Tools](https://developers.google.com/optimization)
- [CP-SAT Solver](https://developers.google.com/optimization/cp/cp_solver)
- [First Lego League](https://www.firstlegoleague.org/)
