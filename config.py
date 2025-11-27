"""
FLL Tournament Scheduler - Configuratie
Pas deze waarden aan voor jouw specifieke toernooi
"""

# ===== TOERNOOI INSTELLINGEN =====

# Aantal tafels beschikbaar (4-10)
NUM_TABLES = 8

# Aantal jury rooms beschikbaar (4-10)
NUM_JURY_ROOMS = 7

# Aantal teams (10-40)
NUM_TEAMS = 40

# Aantal wedstrijden per team (standaard 4 voor FLL)
MATCHES_PER_TEAM = 4

# Duur van een wedstrijd in minuten
MATCH_DURATION = 7

# Duur van een jury sessie in minuten
JURY_DURATION = 42


# Minimale buffer tijd tussen activiteiten in minuten
MINIMUM_BUFFER_TIME = 21

# ===== PAUZE INSTELLINGEN =====

# Pauze tijdens het toernooi - wordt toegevoegd in de OUTPUT, niet als constraint
BREAK_ENABLED = True  # Zet op False om pauze uit te schakelen
BREAK_START_TIME = 168  # Start tijd van pauze in minuten (168 min = 2u48)
BREAK_DURATION = 35  # Duur van de pauze in minuten (5 timeslots × 7 min = 35 min)
# Alle activiteiten NA break_start_time krijgen +BREAK_DURATION minuten in de output

# Tafel paren: deze tafels spelen samen (beide bezet of beide leeg)
# Format: lijst van tuples met tafel IDs (0-indexed)
TABLE_PAIRS = [
    (0, 1),  # Tafel 1 en 2
    (2, 3),  # Tafel 3 en 4
    (4, 5),  # Tafel 5 en 6
    (6, 7),  # Tafel 7 en 8
    (8, 9),  # Tafel 9 en 10
    (10, 11),  # Tafel 11 en 12
    (12, 13)  # Tafel 13 en 14
]

# Aantal tijdsloten (auto-berekend of handmatig instellen)
NUM_TIMESLOTS = 50  # Verhoog dit als er geen oplossing gevonden wordt

# Aantal jury sessies per team (standaard 1)
JURY_SESSIONS_PER_TEAM = 1

# ===== TIMING INSTELLINGEN =====

# Start tijd van het toernooi
START_TIME = "09:30"

# Eind tijd van het toernooi (in minuten vanaf start tijd)
# Alle events moeten voor deze tijd afgelopen zijn
# None = geen eind tijd constraint (gebruik alle beschikbare tijdsloten)
END_TIME = 252  # Bijvoorbeeld: 300 voor 5 uur (300 minuten vanaf start)

# Maximale oplostijd in seconden
MAX_SOLVE_TIME = 120

# ===== VOORBEELDEN =====

# Klein toernooi:
# NUM_TEAMS = 10
# NUM_TABLES = 4
# NUM_TIMESLOTS = 6

# Middelgroot toernooi:
# NUM_TEAMS = 20
# NUM_TABLES = 8
# NUM_TIMESLOTS = 10

# Groot toernooi:
# NUM_TEAMS = 30
# NUM_TABLES = 10
# NUM_TIMESLOTS = 10
