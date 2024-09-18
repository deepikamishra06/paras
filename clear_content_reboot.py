import os
import csv
from datetime import datetime, timedelta
import shutil
import time
import argparse

CSV_FILE = "/home/raspi4/paras/output_database/attendance.csv"
BACKUP_DIR = "/home/raspi4/paras/output_database/detailed_entry_sheets_daily"

# Function to create CSV sheet and log entries
def create_csv_sheet():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Entry Time", "Similarity"])

# Function to backup CSV sheet with date and time stamp
def backup_csv_sheet():
    current_time = datetime.now()
    backup_filename = f"Paras_System_August_daily_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    shutil.copy(CSV_FILE, backup_path)

# Function to clear the contents of the CSV sheet
def clear_csv_sheet():
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Entry Time", "Similarity"])

# Main function
def main(backup_hour, backup_minute):
    create_csv_sheet()
    last_backup_time = None  # Track when the last backup was done

    while True:
        # Get the current time
        current_time = datetime.now()

        # Check if it's time for the backup
        if (current_time.hour == backup_hour and current_time.minute == backup_minute):
            # Only proceed if last_backup_time is not set or is a different day
            if last_backup_time is None or last_backup_time.date() != current_time.date():
                backup_csv_sheet()
                clear_csv_sheet()
                last_backup_time = current_time  # Update the last backup time

                # Sleep to avoid multiple backups in the same minute
                time.sleep(60)

        # Wait for a minute before checking again
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup and clear CSV file at a specified time.")
    parser.add_argument("backup_hour", type=float, help="Hour for backup (0-23)")
    parser.add_argument("backup_minute", type=float, help="Minute for backup (0-59)")
    args = parser.parse_args()

    # Convert float arguments to integers
    backup_hour = int(args.backup_hour)
    backup_minute = int(args.backup_minute)

    main(backup_hour, backup_minute)

