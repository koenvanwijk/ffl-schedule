"""
Complete FLL Tournament Scheduler
Plant zowel matches (tafels) als jury sessies voor teams
"""
from ortools.sat.python import cp_model
from config import *
import json
from datetime import datetime, timedelta


def calculate_timeslot_from_minutes(minutes, duration):
    """Bereken welk tijdslot correspondeert met een bepaalde minuut"""
    return minutes // duration


def create_complete_schedule():
    """Maakt een compleet FLL schema met matches en jury sessies"""
    
    all_teams = range(NUM_TEAMS)
    all_tables = range(NUM_TABLES)
    all_jury_rooms = range(NUM_JURY_ROOMS)
    
    # Bereken hoeveel tijdsloten we nodig hebben
    # Voor matches: tijdslot duur = MATCH_DURATION
    # Voor jury: tijdslot duur = JURY_DURATION
    all_match_timeslots = range(NUM_TIMESLOTS)
    all_jury_timeslots = range(NUM_TIMESLOTS)
    
    print(f"\n🏆 FLL COMPLETE TOURNAMENT SCHEDULER")
    print(f"=" * 70)
    print(f"📋 Configuratie:")
    print(f"   Teams: {NUM_TEAMS}")
    print(f"   Tafels: {NUM_TABLES}")
    print(f"   Jury Rooms: {NUM_JURY_ROOMS}")
    print(f"   Tijdsloten: {NUM_TIMESLOTS}")
    print(f"   Wedstrijden per team: {MATCHES_PER_TEAM}")
    print(f"   Jury sessies per team: {JURY_SESSIONS_PER_TEAM}")
    print(f"   Min. buffer tijd: {MINIMUM_BUFFER_TIME} min")
    print(f"=" * 70 + "\n")

    # Capacity check
    total_matches = NUM_TEAMS * MATCHES_PER_TEAM
    max_match_capacity = NUM_TIMESLOTS * NUM_TABLES
    total_jury_sessions = NUM_TEAMS * JURY_SESSIONS_PER_TEAM
    max_jury_capacity = NUM_TIMESLOTS * NUM_JURY_ROOMS
    
    print(f"📊 Capaciteit check:")
    print(f"   Matches: {total_matches} nodig, {max_match_capacity} beschikbaar")
    print(f"   Jury sessies: {total_jury_sessions} nodig, {max_jury_capacity} beschikbaar")
    
    if total_matches > max_match_capacity:
        print(f"   ⚠️  Onvoldoende match capaciteit!")
        return None
    if total_jury_sessions > max_jury_capacity:
        print(f"   ⚠️  Onvoldoende jury capaciteit!")
        return None
    print(f"   ✅ Capaciteit OK\n")

    model = cp_model.CpModel()

    # ===== VARIABELEN =====
    
    # Matches: matches[(team, timeslot, table)]
    matches = {}
    for team in all_teams:
        for ts in all_match_timeslots:
            for table in all_tables:
                matches[(team, ts, table)] = model.new_bool_var(
                    f"match_t{team}_ts{ts}_tb{table}"
                )

    # Jury sessies: jury_sessions[(team, timeslot, jury_room)]
    jury_sessions = {}
    for team in all_teams:
        for ts in all_jury_timeslots:
            for jury_room in all_jury_rooms:
                jury_sessions[(team, ts, jury_room)] = model.new_bool_var(
                    f"jury_t{team}_ts{ts}_jr{jury_room}"
                )

    # ===== CONSTRAINTS VOOR MATCHES =====
    
    print("🔧 Toevoegen van constraints...")
    
    # 1. Elk team speelt precies MATCHES_PER_TEAM wedstrijden
    for team in all_teams:
        model.add(sum(matches[(team, ts, tb)] 
                     for ts in all_match_timeslots 
                     for tb in all_tables) == MATCHES_PER_TEAM)

    # 2. Maximaal 1 team per tafel per tijdslot
    for ts in all_match_timeslots:
        for table in all_tables:
            model.add_at_most_one(matches[(team, ts, table)] for team in all_teams)

    # 3. Een team kan maar op 1 tafel per tijdslot spelen
    for team in all_teams:
        for ts in all_match_timeslots:
            model.add_at_most_one(matches[(team, ts, table)] for table in all_tables)
    
    # 4. Twee teams mogen maximaal 1 keer tegen elkaar spelen
    # Teams spelen tegen elkaar als ze op hetzelfde tijdslot op een tafel paar spelen
    print("   └─ Unique opponents...")
    
    # Maak variabelen voor welke team paren tegen elkaar hebben gespeeld
    team_matchups = {}
    for team1 in all_teams:
        for team2 in all_teams:
            if team1 < team2:  # Voorkom duplicaten (team1, team2) == (team2, team1)
                team_matchups[(team1, team2)] = model.new_int_var(0, MATCHES_PER_TEAM, 
                    f'matchup_t{team1}_t{team2}')
    
    # Bereken hoe vaak elk team paar tegen elkaar speelt
    if 'TABLE_PAIRS' in globals() and TABLE_PAIRS:
        for team1 in all_teams:
            for team2 in all_teams:
                if team1 < team2:
                    matchup_count = []
                    # Voor elk tafel paar, check of beide teams daar tegelijk spelen
                    for table1, table2 in TABLE_PAIRS:
                        if table1 < NUM_TABLES and table2 < NUM_TABLES:
                            for ts in all_match_timeslots:
                                # Beide teams spelen op dit paar op dit tijdslot
                                both_play = model.new_bool_var(f'both_t{team1}_t{team2}_ts{ts}_pair{table1}_{table2}')
                                
                                # team1 op table1 EN team2 op table2
                                option1 = model.new_bool_var(f'opt1_t{team1}_t{team2}_ts{ts}_p{table1}_{table2}')
                                model.add_bool_and([matches[(team1, ts, table1)], 
                                                   matches[(team2, ts, table2)]]).only_enforce_if(option1)
                                model.add_bool_or([matches[(team1, ts, table1)].Not(), 
                                                  matches[(team2, ts, table2)].Not()]).only_enforce_if(option1.Not())
                                
                                # team1 op table2 EN team2 op table1
                                option2 = model.new_bool_var(f'opt2_t{team1}_t{team2}_ts{ts}_p{table1}_{table2}')
                                model.add_bool_and([matches[(team1, ts, table2)], 
                                                   matches[(team2, ts, table1)]]).only_enforce_if(option2)
                                model.add_bool_or([matches[(team1, ts, table2)].Not(), 
                                                  matches[(team2, ts, table1)].Not()]).only_enforce_if(option2.Not())
                                
                                # both_play = option1 OR option2
                                model.add_bool_or([option1, option2]).only_enforce_if(both_play)
                                model.add_bool_and([option1.Not(), option2.Not()]).only_enforce_if(both_play.Not())
                                
                                matchup_count.append(both_play)
                    
                    # Totaal aantal keer dat team1 en team2 tegen elkaar spelen
                    if matchup_count:
                        model.add(sum(matchup_count) == team_matchups[(team1, team2)])
                        # Maximaal 1 keer tegen elkaar spelen
                        model.add(team_matchups[(team1, team2)] <= 1)

    # ===== CONSTRAINTS VOOR JURY SESSIES =====
    
    # 5. Elk team heeft precies JURY_SESSIONS_PER_TEAM jury sessies
    for team in all_teams:
        model.add(sum(jury_sessions[(team, ts, jr)] 
                     for ts in all_jury_timeslots 
                     for jr in all_jury_rooms) == JURY_SESSIONS_PER_TEAM)

    # 6. Maximaal 1 team per jury room per tijdslot
    for ts in all_jury_timeslots:
        for jury_room in all_jury_rooms:
            model.add_at_most_one(jury_sessions[(team, ts, jury_room)] for team in all_teams)
    
    # 6b. BELANGRIJK: Voorkom overlappende jury sessies in dezelfde room
    # Een jury op tijdslot J beslaat tijdsloten J t/m J+5 (42 min = 6 tijdsloten van 7 min)
    jury_duration_in_slots = (JURY_DURATION + MATCH_DURATION - 1) // MATCH_DURATION
    
    for jury_room in all_jury_rooms:
        for ts1 in all_jury_timeslots:
            for ts2 in range(ts1 + 1, min(ts1 + jury_duration_in_slots, NUM_TIMESLOTS)):
                # Als er een jury sessie start op ts1, mag er geen sessie starten op ts2
                # omdat deze zou overlappen (ts1 loopt tot ts1+6, ts2 start voor die tijd)
                for team1 in all_teams:
                    for team2 in all_teams:
                        if team1 != team2:  # Verschillende teams
                            model.add(
                                jury_sessions[(team1, ts1, jury_room)] + 
                                jury_sessions[(team2, ts2, jury_room)] <= 1
                            )

    # 7. Een team kan maar in 1 jury room per tijdslot zijn
    for team in all_teams:
        for ts in all_jury_timeslots:
            model.add_at_most_one(jury_sessions[(team, ts, jr)] for jr in all_jury_rooms)
    
    # 7b. NIEUWE CONSTRAINT: Jury sessies beginnen in synchrone rondes
    # Bereken hoeveel rondes nodig zijn (40 teams / 7 rooms = 6 rondes)
    import math
    num_jury_rounds = math.ceil(NUM_TEAMS / NUM_JURY_ROOMS)
    print(f"   └─ Jury rondes: {num_jury_rounds} (max {NUM_JURY_ROOMS} teams per ronde)")
    
    # Definieer welke tijdsloten gebruikt mogen worden voor jury start (beperkt aantal)
    # Jury sessies mogen alleen starten op tijdslot 0, 7, 14, 21, etc. (elke 7 slots = 49 min)
    # Dit geeft genoeg tijd tussen rondes (49 min > 42 min jury + minimale gap)
    allowed_jury_start_slots = list(range(0, NUM_TIMESLOTS, 7))[:num_jury_rounds]
    
    # Elk team mag alleen een jury sessie starten op deze specifieke tijdsloten
    for team in all_teams:
        # Tel hoeveel jury sessies het team heeft op toegestane tijdsloten
        valid_jury_sessions = []
        for ts in allowed_jury_start_slots:
            for jr in all_jury_rooms:
                if (team, ts, jr) in jury_sessions:
                    valid_jury_sessions.append(jury_sessions[(team, ts, jr)])
        
        # Team moet precies 1 jury sessie hebben op een toegestaan tijdslot
        if valid_jury_sessions:
            model.add(sum(valid_jury_sessions) == 1)

    # ===== CONSTRAINTS VOOR OVERLAP EN BUFFER =====
    
    # 8. Voorkom overlap tussen matches en jury sessies
    # BEIDE gebruiken nu dezelfde tijdschaal: tijdslot * MATCH_DURATION
    # Match op tijdslot M: start = M*7, eind = M*7+7 (7 min)
    # Jury op tijdslot J: start = J*7, eind = J*7+42 (42 min, dus 6 tijdsloten lang)
    
    print("   └─ Overlap preventie...")
    
    # Een jury sessie op tijdslot J beslaat tijdsloten J t/m J+5 (6 tijdsloten)
    jury_duration_in_slots = (JURY_DURATION + MATCH_DURATION - 1) // MATCH_DURATION  # 6 tijdsloten
    
    for team in all_teams:
        for jury_ts in all_jury_timeslots:
            # Als team jury heeft op tijdslot jury_ts, dan beslaat dit tijdsloten jury_ts t/m jury_ts+5
            jury_start_slot = jury_ts
            jury_end_slot = jury_ts + jury_duration_in_slots - 1
            
            # Team mag geen matches hebben in deze range + buffer
            buffer_in_slots = (MINIMUM_BUFFER_TIME + MATCH_DURATION - 1) // MATCH_DURATION
            
            for match_ts in all_match_timeslots:
                # Check of match overlapt met jury + buffer
                # Match overlapt als: match_ts is tussen (jury_start_slot - buffer) en (jury_end_slot + buffer)
                if (jury_start_slot - buffer_in_slots <= match_ts <= jury_end_slot + buffer_in_slots):
                    has_jury = sum(jury_sessions[(team, jury_ts, jr)] for jr in all_jury_rooms)
                    has_match = sum(matches[(team, match_ts, tb)] for tb in all_tables)
                    model.add(has_jury + has_match <= 1)
    
    # 9. Buffer tijd tussen opeenvolgende matches
    print("   └─ Match spacing...")
    # We hebben minstens MINIMUM_BUFFER_TIME nodig TUSSEN twee matches
    # Als match 1 eindigt op tijd T, dan moet match 2 starten op T + MINIMUM_BUFFER_TIME
    # In termen van tijdsloten: als match op ts1, dan match 2 op ts2
    # waarbij (ts2 * MATCH_DURATION) >= (ts1 * MATCH_DURATION + MATCH_DURATION + MINIMUM_BUFFER_TIME)
    # ts2 >= ts1 + 1 + (MINIMUM_BUFFER_TIME / MATCH_DURATION)
    min_match_gap = 1 + ((MINIMUM_BUFFER_TIME + MATCH_DURATION - 1) // MATCH_DURATION)
    
    print(f"      Min. gap tussen matches: {min_match_gap} tijdsloten ({min_match_gap * MATCH_DURATION} min)")
    
    for team in all_teams:
        for ts in range(NUM_TIMESLOTS):
            for gap in range(1, min_match_gap):
                next_ts = ts + gap
                if next_ts < NUM_TIMESLOTS:
                    has_match_at_ts = sum(matches[(team, ts, tb)] for tb in all_tables)
                    has_match_at_next = sum(matches[(team, next_ts, tb)] for tb in all_tables)
                    model.add(has_match_at_ts + has_match_at_next <= 1)
    
    # 10. Buffer tijd tussen opeenvolgende jury sessies (als team meer dan 1 heeft)
    if JURY_SESSIONS_PER_TEAM > 1:
        print("   └─ Jury spacing...")
        # Rond naar boven
        min_jury_gap = (MINIMUM_BUFFER_TIME + JURY_DURATION - 1) // JURY_DURATION
        for team in all_teams:
            for ts in range(NUM_TIMESLOTS - min_jury_gap):
                for next_ts in range(ts + 1, min(ts + 1 + min_jury_gap, NUM_TIMESLOTS)):
                    has_jury_at_ts = sum(jury_sessions[(team, ts, jr)] for jr in all_jury_rooms)
                    has_jury_at_next = sum(jury_sessions[(team, next_ts, jr)] for jr in all_jury_rooms)
                    model.add(has_jury_at_ts + has_jury_at_next <= 1)

    # ===== OPTIMALISATIE =====
    
    # Soft constraint: tafel paren zo vaak mogelijk beide bezet of beide leeg
    if 'TABLE_PAIRS' in globals() and TABLE_PAIRS:
        print("   └─ Tafel paren optimalisatie...")
        pair_violations = []
        
        for table1, table2 in TABLE_PAIRS:
            if table1 < NUM_TABLES and table2 < NUM_TABLES:
                for ts in all_match_timeslots:
                    # Check of tafel1 en tafel2 beide bezet zijn of beide leeg
                    table1_used = model.new_bool_var(f'ts{ts}_tb{table1}_used')
                    table2_used = model.new_bool_var(f'ts{ts}_tb{table2}_used')
                    
                    # table1_used = 1 als er een team op tafel1 speelt op tijdslot ts
                    model.add(sum(matches[(team, ts, table1)] for team in all_teams) >= 1).only_enforce_if(table1_used)
                    model.add(sum(matches[(team, ts, table1)] for team in all_teams) == 0).only_enforce_if(table1_used.Not())
                    
                    # table2_used = 1 als er een team op tafel2 speelt op tijdslot ts
                    model.add(sum(matches[(team, ts, table2)] for team in all_teams) >= 1).only_enforce_if(table2_used)
                    model.add(sum(matches[(team, ts, table2)] for team in all_teams) == 0).only_enforce_if(table2_used.Not())
                    
                    # Violation: XOR van table1_used en table2_used (1 als ze verschillend zijn)
                    pair_mismatch = model.new_bool_var(f'ts{ts}_pair{table1}_{table2}_mismatch')
                    # pair_mismatch = 1 als table1_used != table2_used
                    model.add(table1_used + table2_used == 1).only_enforce_if(pair_mismatch)
                    model.add(table1_used == table2_used).only_enforce_if(pair_mismatch.Not())
                    
                    pair_violations.append(pair_mismatch)
    
    # Preferentie: teams spelen op zo VEEL mogelijk verschillende tafels
    # Dit zorgt voor maximale variatie in tegenstanders
    tables_used = {}
    for team in all_teams:
        for table in all_tables:
            tables_used[(team, table)] = model.new_bool_var(f"t{team}_uses_tb{table}")
            team_matches_on_table = [matches[(team, ts, table)] for ts in all_match_timeslots]
            model.add(sum(team_matches_on_table) >= 1).only_enforce_if(tables_used[(team, table)])
            model.add(sum(team_matches_on_table) == 0).only_enforce_if(tables_used[(team, table)].Not())

    # Gecombineerde optimalisatie doelen:
    # 1. HOOGSTE PRIORITEIT: Minimaliseer tafel paar violations (cost 1000)
    # 2. TWEEDE PRIORITEIT: MAXIMALISEER aantal verschillende tafels per team (negatieve cost = beloning)
    total_tables_used = sum(tables_used[(team, table)] for team in all_teams for table in all_tables)
    
    if 'pair_violations' in locals() and pair_violations:
        # Tafel paren zijn VEEL belangrijker (cost 1000)
        # Meer tafels per team = beloning (negatieve cost -1 per extra tafel)
        model.minimize(sum(pair_violations) * 1000 - total_tables_used)
    else:
        # Maximaliseer tafel spreiding (minimaliseer negatieve som)
        model.minimize(-total_tables_used)

    # ===== OPLOSSEN =====
    
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = MAX_SOLVE_TIME
    solver.parameters.num_search_workers = 8  # Parallel zoeken
    
    print("🔍 Bezig met zoeken naar optimale oplossing...")
    print(f"   (max {MAX_SOLVE_TIME} seconden)\n")
    
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("✅ Oplossing gevonden!\n")
        return {
            'solver': solver,
            'matches': matches,
            'jury_sessions': jury_sessions,
            'status': status,
            'tables_used': tables_used
        }
    else:
        print("❌ Geen oplossing gevonden!\n")
        return None


def build_json_output(result):
    """Bouwt de JSON output"""
    if result is None:
        return None
    
    solver = result['solver']
    matches = result['matches']
    jury_sessions = result['jury_sessions']
    
    # Hulp functie: voeg pauze toe aan tijden na BREAK_START_TIME
    def adjust_time_for_break(time_minutes):
        """Voegt BREAK_DURATION toe aan tijden die na de pauze vallen"""
        if BREAK_ENABLED and time_minutes >= BREAK_START_TIME:
            return time_minutes + BREAK_DURATION
        return time_minutes
    
    output = {
        "constraintConfiguration": {
            "constraintWeight": "1hard/0medium/0soft",
            "minimumBreakDuration": MINIMUM_BUFFER_TIME,
            "startTime": START_TIME,
            "breakStartTime": BREAK_START_TIME,
            "breakDuration": BREAK_DURATION,
            "matchDuration": MATCH_DURATION,
            "juryDuration": JURY_DURATION
        },
        "tableList": [],
        "tablePairList": [],
        "juryList": [],
        "teamList": [],
        "tableTimeslotList": [],
        "juryTimeslotList": [],
        "teamTableAllocationList": [],
        "teamJuryAllocationList": [],
        "score": "0hard/0medium/0soft" if result['status'] == cp_model.OPTIMAL else "1hard/0medium/0soft"
    }
    
    # Table pairs (2 tafels per paar)
    num_table_pairs = (NUM_TABLES + 1) // 2
    for pair_id in range(num_table_pairs):
        output["tablePairList"].append({"id": pair_id})
    
    # Tables
    for table_id in range(NUM_TABLES):
        pair_id = table_id // 2
        output["tableList"].append({
            "id": table_id,
            "tablePair": {"id": pair_id}
        })
    
    # Jury rooms
    for jury_id in range(NUM_JURY_ROOMS):
        output["juryList"].append({"id": jury_id})
    
    # Teams
    for team_id in range(NUM_TEAMS):
        output["teamList"].append({"id": team_id})
    
    # Table timeslots
    table_timeslot_id = 0
    for ts in range(NUM_TIMESLOTS):
        start_time_minutes = ts * MATCH_DURATION
        adjusted_start = adjust_time_for_break(start_time_minutes)
        adjusted_end = adjust_time_for_break(start_time_minutes + MATCH_DURATION)
        
        for table_id in range(NUM_TABLES):
            pair_id = table_id // 2
            output["tableTimeslotList"].append({
                "id": table_timeslot_id,
                "startTime": adjusted_start,
                "duration": MATCH_DURATION,
                "table": {
                    "id": table_id,
                    "tablePair": {"id": pair_id}
                },
                "endTime": adjusted_end
            })
            table_timeslot_id += 1
    
    # Jury timeslots - BELANGRIJK: deze moeten gesynchroniseerd zijn met match tijden!
    # We maken jury slots die passen in het totale tijdschema
    # Jury duurt 42 min, maar we plannen ze op dezelfde tijdschaal als matches
    jury_timeslot_id = 0
    
    # Bereken hoeveel "match tijdsloten" een jury sessie beslaat
    jury_slots_in_match_units = (JURY_DURATION + MATCH_DURATION - 1) // MATCH_DURATION  # 42/7 = 6
    
    # Maak jury timeslots die gebaseerd zijn op match timing
    for ts in range(NUM_TIMESLOTS):
        start_time_minutes = ts * MATCH_DURATION  # Zelfde tijdschaal als matches!
        adjusted_start = adjust_time_for_break(start_time_minutes)
        adjusted_end = adjust_time_for_break(start_time_minutes + JURY_DURATION)
        
        for jury_id in range(NUM_JURY_ROOMS):
            output["juryTimeslotList"].append({
                "id": jury_timeslot_id,
                "startTime": adjusted_start,
                "duration": JURY_DURATION,
                "endTime": adjusted_end,
                "jury": {"id": jury_id}
            })
            jury_timeslot_id += 1
    
    # Team table allocations (matches)
    for team in range(NUM_TEAMS):
        for ts in range(NUM_TIMESLOTS):
            for table_id in range(NUM_TABLES):
                if solver.value(matches[(team, ts, table_id)]):
                    table_timeslot_id = ts * NUM_TABLES + table_id
                    output["teamTableAllocationList"].append({
                        "team": {"id": team},
                        "timeslot": {"id": table_timeslot_id}
                    })
    
    # Team jury allocations
    for team in range(NUM_TEAMS):
        for ts in range(NUM_TIMESLOTS):
            for jury_id in range(NUM_JURY_ROOMS):
                if solver.value(jury_sessions[(team, ts, jury_id)]):
                    jury_timeslot_id = ts * NUM_JURY_ROOMS + jury_id
                    output["teamJuryAllocationList"].append({
                        "team": {"id": team},
                        "timeslot": {"id": jury_timeslot_id}
                    })
    
    return output


def save_json(output, filename=None):
    """Sla op als JSON"""
    if output is None:
        return None
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        filename = f"schedule-complete-{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Schema opgeslagen als: {filename}")
    return filename


def print_summary(output, result):
    """Print samenvatting"""
    if output is None or result is None:
        print("\n❌ GEEN OPLOSSING GEVONDEN!")
        print("\n💡 Suggesties:")
        print("   • Verhoog NUM_TIMESLOTS in config.py")
        print("   • Verlaag MIN_GAP_BETWEEN_ACTIVITIES")
        print("   • Verhoog MAX_SOLVE_TIME")
        return
    
    solver = result['solver']
    
    print("\n" + "=" * 70)
    print("📊 STATISTIEKEN")
    print("=" * 70)
    print(f"Status: {'OPTIMAAL ✅' if result['status'] == cp_model.OPTIMAL else 'HAALBAAR ⚠️'}")
    print(f"Oplostijd: {solver.wall_time:.2f} seconden")
    print(f"Conflicten: {solver.num_conflicts:,}")
    print(f"Branches: {solver.num_branches:,}")
    
    print(f"\nTotaal matches: {len(output['teamTableAllocationList'])}")
    print(f"Totaal jury sessies: {len(output['teamJuryAllocationList'])}")
    
    # Analyseer tafel gebruik per team
    team_tables = {}
    for allocation in output["teamTableAllocationList"]:
        team_id = allocation["team"]["id"]
        timeslot_info = next(ts for ts in output["tableTimeslotList"] 
                            if ts["id"] == allocation["timeslot"]["id"])
        table_id = timeslot_info["table"]["id"]
        
        if team_id not in team_tables:
            team_tables[team_id] = set()
        team_tables[team_id].add(table_id)
    
    teams_1_table = sum(1 for tables in team_tables.values() if len(tables) == 1)
    teams_2_tables = sum(1 for tables in team_tables.values() if len(tables) == 2)
    teams_more = NUM_TEAMS - teams_1_table - teams_2_tables
    
    print(f"\nTafel verdeling:")
    print(f"  Teams op 1 tafel: {teams_1_table}")
    print(f"  Teams op 2 tafels: {teams_2_tables}")
    if teams_more > 0:
        print(f"  Teams op 3+ tafels: {teams_more} ⚠️")


if __name__ == "__main__":
    result = create_complete_schedule()
    
    if result:
        output = build_json_output(result)
        print_summary(output, result)
        filename = save_json(output)
        print(f"\n✅ Compleet schema succesvol gegenereerd!")
    else:
        print("\n❌ Geen oplossing gevonden - pas config.py aan")
