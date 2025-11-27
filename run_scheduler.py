"""FLL Scheduler met configuratie bestand"""
from ortools.sat.python import cp_model
from config import (
    NUM_TEAMS,
    NUM_TABLES,
    NUM_TIMESLOTS,
    MATCHES_PER_TEAM,
    MIN_GAP_BETWEEN_MATCHES,
    MAX_SOLVE_TIME
)


def create_schedule():
    """Maakt een FLL wedstrijdschema op basis van config.py"""
    
    all_teams = range(NUM_TEAMS)
    all_tables = range(NUM_TABLES)
    all_timeslots = range(NUM_TIMESLOTS)
    
    print(f"\n🏆 FLL TOURNAMENT SCHEDULER")
    print(f"=" * 70)
    print(f"Teams: {NUM_TEAMS} | Tafels: {NUM_TABLES} | Tijdsloten: {NUM_TIMESLOTS}")
    print(f"Wedstrijden per team: {MATCHES_PER_TEAM}")
    print(f"Minimale gap tussen wedstrijden: {MIN_GAP_BETWEEN_MATCHES} tijdslot(en)")
    print(f"=" * 70 + "\n")

    # Controle of het mogelijk is
    max_matches_per_timeslot = NUM_TABLES
    total_timeslots_needed = (NUM_TEAMS * MATCHES_PER_TEAM) / max_matches_per_timeslot
    
    if total_timeslots_needed > NUM_TIMESLOTS:
        print(f"⚠️  WAARSCHUWING: Mogelijk onvoldoende tijdsloten!")
        print(f"   Minimaal {total_timeslots_needed:.1f} tijdsloten nodig, maar {NUM_TIMESLOTS} beschikbaar")
        print(f"   Suggestie: verhoog naar {int(total_timeslots_needed) + 2} tijdsloten\n")

    model = cp_model.CpModel()

    # Variabelen
    matches = {}
    for team in all_teams:
        for timeslot in all_timeslots:
            for table in all_tables:
                matches[(team, timeslot, table)] = model.new_bool_var(
                    f"t{team}_ts{timeslot}_tb{table}"
                )

    # 1. Elk team speelt precies MATCHES_PER_TEAM wedstrijden
    for team in all_teams:
        model.add(sum(matches[(team, ts, tb)] 
                     for ts in all_timeslots 
                     for tb in all_tables) == MATCHES_PER_TEAM)

    # 2. Maximaal 1 team per tafel per tijdslot
    for timeslot in all_timeslots:
        for table in all_tables:
            model.add_at_most_one(matches[(team, timeslot, table)] 
                                 for team in all_teams)

    # 3. Maximaal 1 wedstrijd per team per tijdslot
    for team in all_teams:
        for timeslot in all_timeslots:
            model.add_at_most_one(matches[(team, timeslot, table)] 
                                 for table in all_tables)

    # 4. Minimale gap tussen wedstrijden
    for team in all_teams:
        for ts in range(NUM_TIMESLOTS):
            for next_ts in range(ts + 1, min(ts + 1 + MIN_GAP_BETWEEN_MATCHES, NUM_TIMESLOTS)):
                model.add(sum(matches[(team, ts, tb)] for tb in all_tables) +
                         sum(matches[(team, next_ts, tb)] for tb in all_tables) <= 1)

    # 5. Optimalisatie: Teams bij voorkeur op dezelfde tafel
    tables_used = {}
    for team in all_teams:
        for table in all_tables:
            tables_used[(team, table)] = model.new_bool_var(f"t{team}_uses_tb{table}")
            team_matches_on_table = [matches[(team, ts, table)] for ts in all_timeslots]
            model.add(sum(team_matches_on_table) >= 1).only_enforce_if(
                tables_used[(team, table)])
            model.add(sum(team_matches_on_table) == 0).only_enforce_if(
                tables_used[(team, table)].Not())

    # Minimaliseer totaal aantal gebruikte tafels per team
    model.minimize(sum(tables_used[(team, table)] 
                      for team in all_teams 
                      for table in all_tables))

    # Oplossen
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = MAX_SOLVE_TIME
    
    print("🔍 Bezig met zoeken naar optimale oplossing...")
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Bouw het schema
        schedule = {}
        team_info = {}
        
        for timeslot in all_timeslots:
            schedule[timeslot] = {}
            for table in all_tables:
                for team in all_teams:
                    if solver.value(matches[(team, timeslot, table)]):
                        schedule[timeslot][table] = team
        
        for team in all_teams:
            team_matches = []
            team_tables = set()
            for ts in all_timeslots:
                for tb in all_tables:
                    if solver.value(matches[(team, ts, tb)]):
                        team_matches.append((ts, tb))
                        team_tables.add(tb)
            team_info[team] = {
                'matches': sorted(team_matches),
                'tables': sorted(team_tables)
            }
        
        return {
            'schedule': schedule,
            'team_info': team_info,
            'optimal': status == cp_model.OPTIMAL,
            'solve_time': solver.wall_time,
            'solver': solver
        }
    else:
        return None


def print_schedule(result):
    """Print het schema"""
    if result is None:
        print("\n❌ GEEN OPLOSSING GEVONDEN!")
        print("\n💡 Probeer:")
        print("   • Verhoog NUM_TIMESLOTS in config.py")
        print("   • Verlaag NUM_TEAMS")
        print("   • Verlaag MIN_GAP_BETWEEN_MATCHES")
        print("   • Verhoog NUM_TABLES")
        return
    
    schedule = result['schedule']
    team_info = result['team_info']
    
    print("\n" + "=" * 70)
    print("📅 WEDSTRIJDSCHEMA PER TIJDSLOT")
    print("=" * 70)
    
    for timeslot in sorted(schedule.keys()):
        print(f"\n⏰ Tijdslot {timeslot + 1}:")
        tables_with_teams = schedule[timeslot]
        if tables_with_teams:
            for table in sorted(tables_with_teams.keys()):
                team = tables_with_teams[table]
                print(f"   Tafel {table + 1:2d} → Team {team + 1:2d}")
        else:
            print("   (geen wedstrijden)")
    
    print("\n" + "=" * 70)
    print("👥 PLANNING PER TEAM")
    print("=" * 70)
    
    for team in sorted(team_info.keys()):
        info = team_info[team]
        print(f"\n🏁 Team {team + 1}:")
        for ts, tb in info['matches']:
            print(f"   Tijdslot {ts + 1:2d} → Tafel {tb + 1:2d}")
        num_tables = len(info['tables'])
        tables_list = [tb + 1 for tb in info['tables']]
        emoji = "✅" if num_tables <= 2 else "⚠️"
        print(f"   {emoji} Gebruikt {num_tables} tafel(s): {tables_list}")
    
    print("\n" + "=" * 70)
    print("📊 STATISTIEKEN")
    print("=" * 70)
    status_text = "OPTIMAAL ✅" if result['optimal'] else "HAALBAAR ⚠️"
    print(f"Status: {status_text}")
    print(f"Oplostijd: {result['solve_time']:.2f} seconden")
    
    # Statistieken
    avg_tables = sum(len(info['tables']) for info in team_info.values()) / len(team_info)
    print(f"Gemiddeld aantal tafels per team: {avg_tables:.2f}")
    
    teams_on_one_table = sum(1 for info in team_info.values() if len(info['tables']) == 1)
    teams_on_two_tables = sum(1 for info in team_info.values() if len(info['tables']) == 2)
    teams_on_more = len(team_info) - teams_on_one_table - teams_on_two_tables
    
    print(f"Teams op 1 tafel: {teams_on_one_table}")
    print(f"Teams op 2 tafels: {teams_on_two_tables}")
    if teams_on_more > 0:
        print(f"Teams op 3+ tafels: {teams_on_more} ⚠️")
    
    # Extra solver statistieken
    print(f"\nSolver info:")
    print(f"  Conflicten: {result['solver'].num_conflicts}")
    print(f"  Branches: {result['solver'].num_branches}")


def export_to_csv(result, filename="ffl_schedule.csv"):
    """Exporteer het schema naar een CSV bestand"""
    if result is None:
        print("Geen schema om te exporteren")
        return
    
    import csv
    
    team_info = result['team_info']
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Team', 'Tijdslot', 'Tafel', 'Wedstrijd Nr.'])
        
        for team in sorted(team_info.keys()):
            matches = team_info[team]['matches']
            for idx, (ts, tb) in enumerate(matches, 1):
                writer.writerow([team + 1, ts + 1, tb + 1, idx])
    
    print(f"\n💾 Schema geëxporteerd naar: {filename}")


if __name__ == "__main__":
    result = create_schedule()
    print_schedule(result)
    
    if result:
        export_to_csv(result)
