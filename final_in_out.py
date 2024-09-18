import os
import csv
from datetime import datetime
import time
import argparse

# Define the path for the output directory
FINAL_OUTPUT_DIR = "/home/raspi4/paras/output_database/Final_In_Out_daily"
OUTPUT_DIR = "/home/raspi4/paras/output_database/"

def process_attendance():
    # Dictionary to hold the first in-time and last out-time for each person
    attendance_data = {}

    # Read the output sheet
    csv_file = os.path.join(OUTPUT_DIR, "attendance.csv")
    
    # Check if the file exists
    if not os.path.exists(csv_file):
        print(f"Attendance CSV file not found: {csv_file}")
        return

    with open(csv_file, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header

        for row in csv_reader:
            # Skip rows that do not have exactly 3 elements
            if len(row) != 3:
                print(f"Skipping incomplete row: {row}")
                continue

            name, entry_time, similarity = row

            # Convert the entry time to datetime object
            try:
                # Extract the current year
                current_year = datetime.now().year
                
                # Convert the time format to include the current year
                entry_time = datetime.strptime(f"{entry_time}_{current_year}", "%d_%m_%H_%M_%S_%Y")
            except ValueError as e:
                print(f"Error parsing date/time for row {row}: {e}")
                continue

            # Store the entry time for the name
            if name not in attendance_data:
                attendance_data[name] = {'first_in': entry_time, 'last_out': entry_time}  # Initialize first and last in/out
            else:
                if entry_time < attendance_data[name]['first_in']:
                    attendance_data[name]['first_in'] = entry_time
                if entry_time > attendance_data[name]['last_out']:
                    attendance_data[name]['last_out'] = entry_time

    # Determine the filename based on the current date
    current_date = datetime.now().strftime('%Y_%m_%d')
    final_output_file = os.path.join(FINAL_OUTPUT_DIR, f"Paras_Final_In_Out_{current_date}.csv") #File name should be same in mail_final_in_out.py

    # Write to the final output sheet
    with open(final_output_file, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Name", "First In-Date", "First In-Time", "Last Out-Date", "Last Out-Time"])

        for name, times in attendance_data.items():
            first_in_date = times['first_in'].strftime("%d-%m-%Y")
            first_in_time = times['first_in'].strftime("%H:%M:%S")
            last_out_date = times['last_out'].strftime("%d-%m-%Y")
            last_out_time = times['last_out'].strftime("%H:%M:%S")
            csv_writer.writerow([name, first_in_date, first_in_time, last_out_date, last_out_time])

    print(f"Processed attendance and saved to {final_output_file}")

if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description='Process attendance at a specific hour and minute.')
    parser.add_argument('hour', type=float, help='Hour to trigger the attendance processing (0-23)')
    parser.add_argument('minute', type=float, help='Minute to trigger the attendance processing (0-59)')
    args = parser.parse_args()

    # Convert float arguments to integers
    target_hour = int(args.hour)
    target_minute = int(args.minute)

    print(f"Waiting to process attendance at {target_hour}:{target_minute}")

    while True:
        current_time = datetime.now()

        # Check if the current time matches the specified hour and minute
        if current_time.hour == target_hour and current_time.minute == target_minute:
            process_attendance()
            # Sleep for 61 seconds to ensure it doesn't run multiple times within the same minute
            time.sleep(61)
        else:
            # Sleep for 60 seconds before checking again
            time.sleep(60)

