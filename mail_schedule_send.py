import yagmail
import time
import openpyxl
import argparse

# Define your email and password (replace with actual credentials)
password = "qkue nhkp trrn iznm"
yag = yagmail.SMTP('parassocteamup@gmail.com', password)

# Define email content and attachments (if any)
contents = 'Parassocteamupkn-System Schedule Mail-Health Check'
attachments = "/home/raspi4/paras/output_database/attendance.csv"

# Read email addresses from the XLSX file
def get_email_addresses(xlsx_file):
    wb = openpyxl.load_workbook(xlsx_file)
    sheet = wb.active
    email_addresses = []
    for row in sheet.iter_rows(min_row=2, values_only=True):  # Assuming the first row is the header
        email_addresses.append(row[0])
    return email_addresses

# Send email to all addresses in the list
def send_emails(email_list, subject, contents, attachments):
    for email in email_list:
        yag.send(
            to=email,
            subject=subject,
            contents=contents,
            attachments=attachments
        )
        print(f"Email sent to {email}")

# Read email addresses from the XLSX file
email_list = get_email_addresses('/home/raspi4/paras/input_database/user_input_mails_rx.xlsx')

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Parassocteamupkn-System Schedule Mail-Health Check')
parser.add_argument('delay', type=float, help='Delay in seconds between email sends (can be a floating-point number)')
args = parser.parse_args()

# Send emails at specified intervals
while True:
    send_emails(email_list, 'Parassocteamupkn-System Schedule Mail-Health Check', contents, attachments)
    print("Emails sent")
    time.sleep(args.delay)  # Sleep for the user-specified delay

