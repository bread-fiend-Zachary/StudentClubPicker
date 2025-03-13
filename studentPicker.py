import pandas as pd
import csv
import os
from collections import defaultdict

# max size for all clubs
default_max_size = 30

# CHANGE THIS!!!
# Whatever clubs that have more space or less space, etc
# change values here
custom_club_sizes = {

}

file_path = "students.csv"
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()

students = df[['First Name', 'Last Name', 'Grade', 'First Choice', 'Second Choice', 'Third Choice']].copy()
students = students.dropna(subset=['First Name', 'Last Name'])  # Ensure valid student names

club_assignments = defaultdict(list)
unassigned_students = []

for _, student in students.iterrows():
    club = student['First Choice']
    if pd.notna(club):
        club_capacity = custom_club_sizes.get(club, default_max_size)
        if len(club_assignments[club]) < club_capacity:
            club_assignments[club].append(f"{student['First Name']} {student['Last Name']}, {student['Grade']}")
        else:
            unassigned_students.append(student)

final_club_assignments = defaultdict(list)
overflow_students = []

for club, members in club_assignments.items():
    club_capacity = custom_club_sizes.get(club, default_max_size)
    if len(members) > club_capacity:
        final_club_assignments[club] = members[:club_capacity]
        overflow_students.extend(members[club_capacity:])
    else:
        final_club_assignments[club] = members

unassigned_after_capping = []
for student in unassigned_students:
    first_name, last_name, grade = student['First Name'], student['Last Name'], student['Grade']
    assigned = False

    for choice in ['Second Choice', 'Third Choice']:
        club = student[choice]
        if pd.notna(club):
            club_capacity = custom_club_sizes.get(club, default_max_size)
            if len(final_club_assignments[club]) < club_capacity:
                final_club_assignments[club].append(f"{first_name} {last_name}, {grade}")
                assigned = True
                break

    if not assigned:
        unassigned_after_capping.append(f"{first_name} {last_name}, {grade}")


dirname = os.path.dirname(os.path.abspath(__file__))
csvfilename = os.path.join(dirname, 'club_assignments.csv')
with open(csvfilename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    total_students = len(students)
    total_assigned = sum(len(members) for members in final_club_assignments.values())
    total_unassigned = len(unassigned_after_capping)
    writer.writerow(["Total Students", total_students])
    writer.writerow(["Total Assigned", total_assigned])
    writer.writerow(["Total Unassigned", total_unassigned])
    writer.writerow([])

    for club, members in final_club_assignments.items():
        writer.writerow([f"{club} ({len(members)} students):"])
        for member in members:
            writer.writerow([f"{member}"])
        writer.writerow([])

    writer.writerow(["Unassigned Students:"])
    for student in unassigned_after_capping:
        writer.writerow([f"{student}"])

print(f"Club assignments saved to: {csvfilename}")