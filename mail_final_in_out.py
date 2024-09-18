### This code will share the mail to single person
#import yagmail
#import time
#from datetime import datetime, timedelta
#import os
#import argparse
#
## Define your email and password
#
#password = "qkue nhkp trrn iznm"
#yag = yagmail.SMTP('parassocteamup@gmail.com', password)
#
## Define email content
#contents = 'Parassocteamupkn-System Daily Attendence Update With In-Out Timings'
#
## Define the directory for output files
#OUTPUT_DIR = "/home/raspi4/paras/output_database/Final_In_Out_daily"
#
## Function to calculate time until the specified hour and minute
#def time_until(target_hour, target_minute):
#    now = datetime.now()
#    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
#    if now > target_time:
#        target_time += timedelta(days=1)
#    time_diff = target_time - now
#    return time_diff.total_seconds()
#
#if __name__ == "__main__":
#    # Parse the command-line arguments for the hour and minute
#    parser = argparse.ArgumentParser(description="System-Paras Daily Attendence Update With In-Out Timings.")
#    parser.add_argument("target_hour", type=float, help="Hour to send email (0-23)")
#    parser.add_argument("target_minute", type=float, help="Minute to send email (0-59)")
#    args = parser.parse_args()
#
#    # Convert float arguments to integers
#    target_hour = int(args.target_hour)
#    target_minute = int(args.target_minute)
#
#    while True:
#        # Calculate seconds until the specified time
#        seconds_until_target = time_until(target_hour, target_minute)
#
#        # Delay until the specified time
#        time.sleep(seconds_until_target)
#
#        # Determine the filename based on the current date
#        current_date = datetime.now().strftime('%Y_%m_%d')
#        final_output_file = os.path.join(OUTPUT_DIR, f"Paras_Final_In_Out_{current_date}.csv") ## File name should be same as final_in_out
#
#        # Check if the file exists
#        if os.path.exists(final_output_file):
#            # Send the email
#            yag.send(
#                to='yogesharma41@gmail.com',
#                subject='Parassocteamupkn-System Daily Attendence Update With In-Out Timings',
#                contents=contents,
#                attachments=final_output_file
#            )
#            print("Email Sent")
#        else:
#            print(f"File {final_output_file} does not exist. Email not sent.")
#
#        # Sleep for 61 seconds to ensure it doesn't run multiple times within the same minute
#        time.sleep(61)


#
import yagmail
import time
from datetime import datetime, timedelta
import os
import argparse
import pandas as pd

# Define your email and password
password = "qkue nhkp trrn iznm"
yag = yagmail.SMTP('parassocteamup@gmail.com', password)

# Define email content
contents = 'Parassocteamupkn-System Daily Attendence Update With In-Out Timings'

# Define the directory for output files
OUTPUT_DIR = "/home/raspi4/paras/output_database/Final_In_Out_daily"

# Function to calculate time until the specified hour and minute
def time_until(target_hour, target_minute):
    now = datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if now > target_time:
        target_time += timedelta(days=1)
    time_diff = target_time - now
    return time_diff.total_seconds()

# Function to get email addresses from an XLSX file
def get_email_addresses(file_path):
    df = pd.read_excel(file_path)
    # Assuming email addresses are in the first column
    email_addresses = df.iloc[:, 0].tolist()
    return email_addresses

if __name__ == "__main__":
    # Parse the command-line arguments for the hour and minute
    parser = argparse.ArgumentParser(description="System-Paras Daily Attendence Update With In-Out Timings.")
    parser.add_argument("target_hour", type=float, help="Hour to send email (0-23)")
    parser.add_argument("target_minute", type=float, help="Minute to send email (0-59)")
    args = parser.parse_args()

    # Convert float arguments to integers
    target_hour = int(args.target_hour)
    target_minute = int(args.target_minute)

    # Get email addresses from the XLSX file
    email_list = get_email_addresses('/home/raspi4/paras/input_database/user_input_mails_rx.xlsx')

    while True:
        # Calculate seconds until the specified time
        seconds_until_target = time_until(target_hour, target_minute)

        # Delay until the specified time
        time.sleep(seconds_until_target)

        # Determine the filename based on the current date
        current_date = datetime.now().strftime('%Y_%m_%d')
        final_output_file = os.path.join(OUTPUT_DIR, f"Paras_Final_In_Out_{current_date}.csv")

        # Check if the file exists
        if os.path.exists(final_output_file):
            # Send the email to each address in the email list
            for email in email_list:
                try:
                    yag.send(
                        to=email,
                        subject='Parassocteamupkn-System Daily Attendence Update With In-Out Timings',
                        contents=contents,
                        attachments=final_output_file
                    )
                    print(f"Email Sent to {email}")
                except Exception as e:
                    print(f"Failed to send email to {email}: {e}")
        else:
            print(f"File {final_output_file} does not exist. Email not sent.")

        # Sleep for 61 seconds to ensure it doesn't run multiple times within the same minute
        time.sleep(61)

