import pandas as pd
from collections import Counter, defaultdict


# Changable values
MIN_CLUB_SIZE = 5
EXPAND_THRESHOLD = 50

# Configuration
BASE_CAPACITY = 30
SOFT_CLUB_LIMIT = 50
EXPAND_AMOUNT = 30
MAX_CAPACITY = 60
TRIM_LIMIT = 30

# Change this to auto-assign any students that have any of these clubs as their choices
UNPOPULAR_CLUBS = { "Poetry/Spoken Word Club", "Study Skills Success Club", "Walking/Reading/Math Club" }

# Load Data
df = pd.read_csv("students.csv")
df.columns = df.columns.str.strip()
df["Full Name"] = df["First Name"].str.strip() + " " + df["Last Name"].str.strip()
choices_df = df[["Full Name", "First Choice", "Second Choice", "Third Choice"]]
all_students = set(choices_df["Full Name"].tolist())

# Count club popularity
club_demand = defaultdict(int)
for _, row in choices_df.iterrows():
    for col in ["First Choice", "Second Choice", "Third Choice"]:
        club_demand[row[col]] += 1

# Set club capacities
club_capacities = {}
for club, demand in club_demand.items():
    cap = BASE_CAPACITY
    while cap < MAX_CAPACITY and demand > EXPAND_THRESHOLD:
        cap += EXPAND_AMOUNT
    club_capacities[club] = min(cap, MAX_CAPACITY)

# Assignment Structures
club_assignments = defaultdict(list)
assigned_students = {}
club_choice_tracker = {}

# Auto-assign to unpopular clubs if listed in any of 3 choices
for _, row in choices_df.iterrows():
    student = row["Full Name"]
    if student in assigned_students:
        continue
    for choice_col, label in [("First Choice", "1st"), ("Second Choice", "2nd"), ("Third Choice", "3rd")]:
        club = row[choice_col]
        if club in UNPOPULAR_CLUBS and len(club_assignments[club]) < club_capacities[club]:
            club_assignments[club].append(student)
            assigned_students[student] = club
            club_choice_tracker[student] = label
            break


# Main Assignment Loop (3rd -> 2nd -> 1st)
choice_order = [("Third Choice", "3rd"), ("Second Choice", "2nd"), ("First Choice", "1st")]
for choice_col, label in choice_order:
    for _, row in choices_df.iterrows():
        student = row["Full Name"]
        if student in assigned_students:
            continue
        club = row[choice_col]
        if len(club_assignments[club]) < club_capacities[club]:
            club_assignments[club].append(student)
            assigned_students[student] = club
            club_choice_tracker[student] = label

# Disband Clubs with Fewer Than MIN_CLUB_SIZE
disbanded_clubs = []
to_reassign = []

for club, students in list(club_assignments.items()):
    if len(students) < MIN_CLUB_SIZE:
        disbanded_clubs.append(club)
        to_reassign.extend(students)
        for student in students:
            assigned_students.pop(student, None)
            club_choice_tracker.pop(student, None)
        del club_assignments[club]
        del club_capacities[club]

# Trim Clubs with 31–49 Students to 30
for club, students in list(club_assignments.items()):
    if TRIM_LIMIT < len(students) <= SOFT_CLUB_LIMIT:
        overflow = students[TRIM_LIMIT:]
        club_assignments[club] = students[:TRIM_LIMIT]
        club_capacities[club] = TRIM_LIMIT
        to_reassign.extend(overflow)
        for student in overflow:
            assigned_students.pop(student, None)
            club_choice_tracker.pop(student, None)

# Expand Clubs with > SOFT_CLUB_LIMIT Students
for club, students in club_assignments.items():
    if len(students) > SOFT_CLUB_LIMIT:
        club_capacities[club] = min(club_capacities[club] + EXPAND_AMOUNT, MAX_CAPACITY)

# Reassign Students Removed During Cleanup
for student in to_reassign:
    row = choices_df[choices_df["Full Name"] == student].iloc[0]
    for choice_col, label in choice_order:
        club = row[choice_col]
        if club in club_capacities and len(club_assignments[club]) < club_capacities[club]:
            club_assignments[club].append(student)
            assigned_students[student] = club
            club_choice_tracker[student] = label
            break

# Final Reassignment Attempt for Unassigned
for student in all_students:
    if student not in assigned_students:
        row = choices_df[choices_df["Full Name"] == student].iloc[0]
        for choice_col, label in choice_order:
            club = row[choice_col]
            if club in club_capacities and len(club_assignments[club]) < club_capacities[club]:
                club_assignments[club].append(student)
                assigned_students[student] = club
                club_choice_tracker[student] = label
                break

# Finalize Assignment Dictionary
final_assignments = {}
for student in all_students:
    if student in assigned_students:
        final_assignments[student] = (assigned_students[student], club_choice_tracker[student])
    else:
        final_assignments[student] = ("Unassigned", "-")

# Write TXT Report
output_lines = []
for club in sorted(club_assignments.keys()):
    students = club_assignments[club]
    output_lines.append(f'"{club}" Club: {len(students)} students (Max: {club_capacities[club]})')
    for student in sorted(students):
        choice = club_choice_tracker.get(student, "?")
        output_lines.append(f"  {student} ({choice} choice)")
    output_lines.append("")

unassigned = [s for s, (club, _) in final_assignments.items() if club == "Unassigned"]
if unassigned:
    output_lines.append("Unassigned Students:")
    for student in sorted(unassigned):
        output_lines.append(f"  {student}")
    output_lines.append("")

if disbanded_clubs:
    output_lines.append("Disbanded Clubs:")
    for club in disbanded_clubs:
        output_lines.append(f"  {club}")
    output_lines.append("")



club_choice_counts = defaultdict(lambda: {"1st": 0, "2nd": 0, "3rd": 0})
for _, row in choices_df.iterrows():
    club_choice_counts[row["First Choice"]]["1st"] += 1
    club_choice_counts[row["Second Choice"]]["2nd"] += 1
    club_choice_counts[row["Third Choice"]]["3rd"] += 1

output_lines.append("\n🎯 Club Choice Popularity Breakdown:")
for club in sorted(club_choice_counts):
    counts = club_choice_counts[club]
    output_lines.append(f'  {club}: {counts["1st"]} first, {counts["2nd"]} second, {counts["3rd"]} third')

with open("final_club_assignments.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"📊 Total students: {len(all_students)}")
print(f"✅ Assigned: {len(all_students) - len(unassigned)}")
print(f"❌ Unassigned: {len(unassigned)}")
print("📁 Output saved as 'final_club_assignments.txt'")
