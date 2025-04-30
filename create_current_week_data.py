import csv
import random
import pandas as pd
from datetime import datetime, timedelta

# Get current date
current_date = datetime.now()

# Calculate dates for the current week (Monday to Sunday)
# First, find the most recent Monday
days_since_monday = current_date.weekday()
start_date = current_date - timedelta(days=days_since_monday)

# Generate dates for the whole week
dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

# Meal times
meal_times = {
    'Breakfast': ['07:{:02d}:00'.format(i) for i in range(30, 60)],
    'Lunch': ['12:{:02d}:00'.format(i) for i in range(30, 60)],
    'Dinner': ['19:{:02d}:00'.format(i) for i in range(30, 60)]
}

# Create attendance records for 10 students per meal per day
attendance_records = []
next_id = 136  # Continue from our existing data

for date in dates:
    for meal_type in ['Breakfast', 'Lunch', 'Dinner']:
        for student_id in range(1, 11):  # 10 students
            time = random.choice(meal_times[meal_type])
            leftover_weight = round(random.uniform(0.1, 0.5), 2)
            
            attendance_records.append([
                next_id,
                student_id,
                date,
                time,
                meal_type,
                leftover_weight
            ])
            next_id += 1

# Read existing attendance data
existing_attendance = []
with open('data/attendance.csv', 'r') as f:
    reader = csv.reader(f)
    # Skip header
    header = next(reader)
    for row in reader:
        existing_attendance.append(row)

# Add new records to existing data
with open('data/attendance.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    # Write existing records
    for row in existing_attendance:
        writer.writerow(row)
    # Write new records
    for record in attendance_records:
        writer.writerow(record)

# Now update meal preparation records for the current week
meal_prep_records = []
next_id = 88  # Continue from existing data

for date in dates:
    for meal_type, prefix in [('Breakfast', 'Break'), ('Lunch', 'Lunch'), ('Dinner', 'Dinner')]:
        # Get day abbreviation
        day_of_week = datetime.strptime(date, '%Y-%m-%d').strftime('%a')[:3]
        meal_name = f"{day_of_week}_{prefix}_1"
        
        # Generate randomized data
        quantity_prepared = round(random.uniform(15.0, 35.0), 1)
        expected_students = random.randint(8, 12)  # Around 10 students
        leftover_weight = round(random.uniform(1.0, 5.0), 1)
        
        meal_prep_records.append([
            next_id,
            meal_name,
            date,
            quantity_prepared,
            expected_students,
            leftover_weight
        ])
        next_id += 1

# Read existing meal preparation data
existing_meal_prep = []
with open('data/meal_preparation.csv', 'r') as f:
    reader = csv.reader(f)
    # Skip header
    header = next(reader)
    for row in reader:
        existing_meal_prep.append(row)

# Add new records to existing data
with open('data/meal_preparation.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    # Write existing records
    for row in existing_meal_prep:
        writer.writerow(row)
    # Write new records
    for record in meal_prep_records:
        writer.writerow(record)

print(f"Added {len(attendance_records)} new attendance records")
print(f"Added {len(meal_prep_records)} new meal preparation records")