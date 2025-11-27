#!/usr/bin/env python3
"""
Test script voor FLL Tournament Scheduler
Controleert of alle constraints in het gegenereerde schema worden nageleefd.
"""

import json
import sys
from collections import defaultdict


def load_schedule(filename):
    """Laad schedule JSON bestand"""
    with open(filename, 'r') as f:
        return json.load(f)


def test_jury_room_overlaps(data):
    """Test of jury rooms geen overlappende sessies hebben"""
    print("\n🔍 Test: Jury Room Overlaps")
    print("-" * 60)
    
    # Build timeslot -> (start, end, jury_room) mapping
    timeslot_info = {}
    for ts in data['juryTimeslotList']:
        ts_id = ts['id']
        jury_room = ts['jury']['id']
        start = ts['startTime']
        end = ts['endTime']
        timeslot_info[ts_id] = (start, end, jury_room)

    # Build jury_room -> [(start, end, team)] mapping
    jury_schedule = defaultdict(list)
    for allocation in data['teamJuryAllocationList']:
        team = allocation['team']['id']
        ts_id = allocation['timeslot']['id']
        if ts_id in timeslot_info:
            start, end, jury_room = timeslot_info[ts_id]
            jury_schedule[jury_room].append((start, end, team))

    # Check overlaps
    overlap_found = False
    total_overlaps = 0
    
    for jury_room, sessions in sorted(jury_schedule.items()):
        sessions_sorted = sorted(sessions)
        overlaps = []
        
        for i in range(len(sessions_sorted)):
            for j in range(i+1, len(sessions_sorted)):
                s1_start, s1_end, team1 = sessions_sorted[i]
                s2_start, s2_end, team2 = sessions_sorted[j]
                if s1_end > s2_start:
                    overlaps.append(f'Team {team1} ({s1_start}-{s1_end}) ↔ Team {team2} ({s2_start}-{s2_end})')
                    overlap_found = True
                    total_overlaps += 1
        
        if overlaps:
            print(f'  ❌ Jury Room {jury_room}: {len(sessions_sorted)} teams, {len(overlaps)} OVERLAPS')
            for overlap in overlaps[:2]:
                print(f'     {overlap}')
            if len(overlaps) > 2:
                print(f'     ... +{len(overlaps) - 2} meer')
        else:
            print(f'  ✅ Jury Room {jury_room}: {len(sessions_sorted)} teams')

    if not overlap_found:
        print(f'\n  ✅ PASSED: Geen jury room overlaps')
        return True
    else:
        print(f'\n  ❌ FAILED: {total_overlaps} jury room overlaps gevonden')
        return False


def test_team_constraints(data):
    """Test of teams de juiste aantal activiteiten hebben met goede buffers"""
    print("\n🔍 Test: Team Constraints")
    print("-" * 60)
    
    # Build team activities
    team_activities = {}
    for team_data in data['teamList']:
        team_id = team_data['id']
        team_activities[team_id] = []

    # Add matches
    for alloc in data['teamTableAllocationList']:
        team = alloc['team']['id']
        ts_id = alloc['timeslot']['id']
        ts_data = next(t for t in data['tableTimeslotList'] if t['id'] == ts_id)
        start = ts_data['startTime']
        end = ts_data['endTime']
        table = ts_data['table']['id']
        team_activities[team].append(('match', start, end, table))

    # Add jury sessions
    timeslot_info = {}
    for ts in data['juryTimeslotList']:
        timeslot_info[ts['id']] = (ts['startTime'], ts['endTime'], ts['jury']['id'])
    
    for alloc in data['teamJuryAllocationList']:
        team = alloc['team']['id']
        ts_id = alloc['timeslot']['id']
        if ts_id in timeslot_info:
            start, end, jury_room = timeslot_info[ts_id]
            team_activities[team].append(('jury', start, end, jury_room))

    # Check constraints
    violations = []
    buffer_violations = []
    
    for team, activities in sorted(team_activities.items()):
        activities.sort(key=lambda x: x[1])
        
        # Check activity count
        matches = [a for a in activities if a[0] == 'match']
        jury_sessions = [a for a in activities if a[0] == 'jury']
        
        if len(matches) != 4:
            violations.append(f'Team {team}: {len(matches)} matches (verwacht: 4)')
        if len(jury_sessions) != 1:
            violations.append(f'Team {team}: {len(jury_sessions)} jury sessies (verwacht: 1)')
        
        # Check buffers
        for i in range(len(activities) - 1):
            _, _, end1, _ = activities[i]
            _, start2, _, _ = activities[i + 1]
            gap = start2 - end1
            if gap < 30:
                buffer_violations.append(f'Team {team}: buffer van {gap} min tussen activiteiten')

    # Print results
    if violations:
        print(f'  ❌ Activity count violations:')
        for v in violations[:5]:
            print(f'     {v}')
        if len(violations) > 5:
            print(f'     ... +{len(violations) - 5} meer')
    else:
        print(f'  ✅ Alle teams: 4 matches + 1 jury sessie')
    
    if buffer_violations:
        print(f'  ❌ Buffer violations:')
        for v in buffer_violations[:5]:
            print(f'     {v}')
        if len(buffer_violations) > 5:
            print(f'     ... +{len(buffer_violations) - 5} meer')
    else:
        print(f'  ✅ Alle buffers: minimaal 30 minuten')
    
    passed = len(violations) == 0 and len(buffer_violations) == 0
    if passed:
        print(f'\n  ✅ PASSED: Alle team constraints OK')
    else:
        print(f'\n  ❌ FAILED: {len(violations) + len(buffer_violations)} violations')
    
    return passed


def test_table_overlaps(data):
    """Test of tafels geen overlappende matches hebben"""
    print("\n🔍 Test: Table Overlaps")
    print("-" * 60)
    
    # Build table -> [(start, end, team)] mapping
    table_schedule = defaultdict(list)
    
    for alloc in data['teamTableAllocationList']:
        team = alloc['team']['id']
        ts_id = alloc['timeslot']['id']
        ts_data = next(t for t in data['tableTimeslotList'] if t['id'] == ts_id)
        start = ts_data['startTime']
        end = ts_data['endTime']
        table = ts_data['table']['id']
        table_schedule[table].append((start, end, team))

    # Check overlaps
    overlap_found = False
    total_overlaps = 0
    
    for table, matches in sorted(table_schedule.items()):
        matches_sorted = sorted(matches)
        overlaps = []
        
        for i in range(len(matches_sorted)):
            for j in range(i+1, len(matches_sorted)):
                m1_start, m1_end, team1 = matches_sorted[i]
                m2_start, m2_end, team2 = matches_sorted[j]
                if m1_end > m2_start:
                    overlaps.append(f'Team {team1} ({m1_start}-{m1_end}) ↔ Team {team2} ({m2_start}-{m2_end})')
                    overlap_found = True
                    total_overlaps += 1
        
        if overlaps:
            print(f'  ❌ Tafel {table}: {len(matches_sorted)} matches, {len(overlaps)} OVERLAPS')
            for overlap in overlaps[:2]:
                print(f'     {overlap}')
        else:
            print(f'  ✅ Tafel {table}: {len(matches_sorted)} matches')

    if not overlap_found:
        print(f'\n  ✅ PASSED: Geen tafel overlaps')
        return True
    else:
        print(f'\n  ❌ FAILED: {total_overlaps} tafel overlaps gevonden')
        return False


def test_team_table_preference(data):
    """Test hoeveel teams op 1 of 2 tafels spelen (soft constraint)"""
    print("\n🔍 Test: Team Table Preference (soft)")
    print("-" * 60)
    
    team_tables = defaultdict(set)
    
    for alloc in data['teamTableAllocationList']:
        team = alloc['team']['id']
        ts_id = alloc['timeslot']['id']
        ts_data = next(t for t in data['tableTimeslotList'] if t['id'] == ts_id)
        table = ts_data['table']['id']
        team_tables[team].add(table)
    
    teams_1_table = sum(1 for tables in team_tables.values() if len(tables) == 1)
    teams_2_tables = sum(1 for tables in team_tables.values() if len(tables) == 2)
    teams_more = sum(1 for tables in team_tables.values() if len(tables) > 2)
    
    print(f'  Teams op 1 tafel: {teams_1_table}')
    print(f'  Teams op 2 tafels: {teams_2_tables}')
    if teams_more > 0:
        print(f'  Teams op 3+ tafels: {teams_more}')
    
    print(f'\n  ✅ INFO: Soft constraint (geen pass/fail)')
    return True


def test_jury_synchronized_rounds(data):
    """Test of jury sessies in gesynchroniseerde rondes beginnen"""
    print("\n🔍 Test: Jury Synchronized Rounds")
    print("-" * 60)
    
    # Build timeslot -> (start, end, jury_room) mapping
    timeslot_info = {}
    for ts in data['juryTimeslotList']:
        ts_id = ts['id']
        jury_room = ts['jury']['id']
        start = ts['startTime']
        end = ts['endTime']
        timeslot_info[ts_id] = (start, end, jury_room)

    # Build start_time -> [teams] mapping
    jury_start_times = defaultdict(list)
    for allocation in data['teamJuryAllocationList']:
        team = allocation['team']['id']
        ts_id = allocation['timeslot']['id']
        if ts_id in timeslot_info:
            start, end, jury_room = timeslot_info[ts_id]
            jury_start_times[start].append((team, jury_room))

    # Print jury rondes
    num_rounds = len(jury_start_times)
    print(f'  Aantal jury rondes: {num_rounds}')
    
    for start_time in sorted(jury_start_times.keys()):
        teams_in_round = jury_start_times[start_time]
        print(f'  Ronde @ {start_time} min: {len(teams_in_round)} teams')
    
    # Check: alle teams moeten in een ronde zitten
    total_teams_in_rounds = sum(len(teams) for teams in jury_start_times.values())
    num_teams = len(data['teamList'])
    
    if total_teams_in_rounds == num_teams:
        print(f'\n  ✅ PASSED: Alle {num_teams} teams in {num_rounds} gesynchroniseerde rondes')
        return True
    else:
        print(f'\n  ❌ FAILED: {total_teams_in_rounds}/{num_teams} teams in rondes')
        return False


def test_table_pairs(data):
    """Test of tafel paren (soft constraint) goed worden gebruikt"""
    print("\n🔍 Test: Table Pairs (soft)")
    print("-" * 60)
    
    # Tafel paren (0-indexed)
    TABLE_PAIRS = [(0, 1), (2, 3), (4, 5)]
    
    # Build tijdslot -> tafels in gebruik
    timeslot_tables = defaultdict(set)
    
    for alloc in data['teamTableAllocationList']:
        ts_id = alloc['timeslot']['id']
        ts_data = next(t for t in data['tableTimeslotList'] if t['id'] == ts_id)
        table = ts_data['table']['id']
        start = ts_data['startTime']
        timeslot_tables[start].add(table)
    
    # Check voor elk tijdslot de paren
    matched = 0
    mismatched = 0
    
    for start_time in sorted(timeslot_tables.keys()):
        tables = timeslot_tables[start_time]
        
        for t1, t2 in TABLE_PAIRS:
            t1_used = t1 in tables
            t2_used = t2 in tables
            
            if (t1_used and t2_used) or (not t1_used and not t2_used):
                matched += 1
            else:
                mismatched += 1
    
    total = matched + mismatched
    percentage = (matched / total * 100) if total > 0 else 0
    
    print(f'  Tafel paren: (1,2), (3,4), (5,6)')
    print(f'  Beide bezet OF beide leeg: {matched}/{total} ({percentage:.1f}%)')
    print(f'  Slechts 1 van paar bezet: {mismatched}/{total} ({100-percentage:.1f}%)')
    
    print(f'\n  ✅ INFO: Soft constraint (geen pass/fail)')
    return True


def test_unique_opponents(data):
    """Test of teams maximaal 1 keer tegen elkaar spelen"""
    print("\n🔍 Test: Unique Opponents")
    print("-" * 60)
    
    # Build tafel paren
    TABLE_PAIRS = [(0, 1), (2, 3), (4, 5)]
    
    # Voor elk tijdslot, groepeer teams per tafel paar
    timeslot_pairs = defaultdict(lambda: defaultdict(list))
    
    for alloc in data['teamTableAllocationList']:
        team = alloc['team']['id']
        ts_id = alloc['timeslot']['id']
        ts_data = next(t for t in data['tableTimeslotList'] if t['id'] == ts_id)
        table = ts_data['table']['id']
        start_time = ts_data['startTime']
        
        # Check welk tafel paar deze tafel bij hoort
        for pair_idx, (t1, t2) in enumerate(TABLE_PAIRS):
            if table in (t1, t2):
                timeslot_pairs[start_time][pair_idx].append((team, table))
                break
    
    # Count matchups
    matchups = defaultdict(int)
    
    for start_time, pairs in timeslot_pairs.items():
        for pair_idx, teams_on_pair in pairs.items():
            if len(teams_on_pair) == 2:
                (team1, table1), (team2, table2) = teams_on_pair
                team_pair = tuple(sorted([team1, team2]))
                matchups[team_pair] += 1
    
    # Check violations
    violations = [(pair, count) for pair, count in matchups.items() if count > 1]
    
    print(f'  Totaal unieke matchups: {len(matchups)}')
    
    if violations:
        print(f'  ❌ {len(violations)} team paren spelen meer dan 1x tegen elkaar:')
        for (t1, t2), count in sorted(violations, key=lambda x: -x[1])[:5]:
            print(f'     Team {t1} vs Team {t2}: {count} keer')
        if len(violations) > 5:
            print(f'     ... +{len(violations) - 5} meer')
        print(f'\n  ❌ FAILED: Teams spelen meerdere keren tegen elkaar')
        return False
    else:
        print(f'  ✅ Alle matchups zijn uniek')
        print(f'\n  ✅ PASSED: Geen team speelt meer dan 1x tegen dezelfde tegenstander')
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_schedule.py <schedule.json>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    print("=" * 60)
    print("🧪 FLL SCHEDULE TESTER")
    print("=" * 60)
    print(f"Bestand: {filename}")
    
    try:
        data = load_schedule(filename)
    except FileNotFoundError:
        print(f"\n❌ ERROR: Bestand '{filename}' niet gevonden")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\n❌ ERROR: Ongeldig JSON bestand: {e}")
        sys.exit(1)
    
    # Run all tests
    results = []
    results.append(("Table Overlaps", test_table_overlaps(data)))
    results.append(("Jury Room Overlaps", test_jury_room_overlaps(data)))
    results.append(("Team Constraints", test_team_constraints(data)))
    results.append(("Jury Synchronized Rounds", test_jury_synchronized_rounds(data)))
    results.append(("Unique Opponents", test_unique_opponents(data)))
    results.append(("Table Preference", test_team_table_preference(data)))
    results.append(("Table Pairs", test_table_pairs(data)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SAMENVATTING")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALLE TESTS GESLAAGD!")
        sys.exit(0)
    else:
        print(f"⚠️  {total - passed} van {total} tests gefaald")
        sys.exit(1)


if __name__ == "__main__":
    main()
