"""
FLL Tournament Scheduler - Configuratie
Pas deze waarden aan voor jouw specifieke toernooi
"""

# ===== TOERNOOI INSTELLINGEN =====

# Aantal teams (10-40)
NUM_TEAMS = 12

# Aantal tafels beschikbaar (4-10)
NUM_TABLES = 6

# Aantal tijdsloten (4-10)
NUM_TIMESLOTS = 8

# Aantal wedstrijden per team (standaard 4 voor FLL)
MATCHES_PER_TEAM = 4

# Minimaal aantal tijdsloten tussen wedstrijden per team
# 1 = minstens 1 tijdslot tussen elke wedstrijd
# 2 = minstens 2 tijdsloten tussen elke wedstrijd
MIN_GAP_BETWEEN_MATCHES = 1

# Maximale oplostijd in seconden
MAX_SOLVE_TIME = 60

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
