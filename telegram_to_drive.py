import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from collections import defaultdict

# Telegram bot token
TELEGRAM_BOT_TOKEN = '7236268797:AAFTbsMIk85wBoF6po1L4eFw66dwcro5aOw'

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = '/home/raspi4/paras/tools/parastelegram1-04dc0dbcb182.json'  # Ensure this path is correct

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# Folder ID where the files will be uploaded
FOLDER_ID = '1yCa74Y7sD7nzm6ciMoX3fcqLiJ2edCY-1Dk1gfPU7xFT3R6O7eZ1m8T4oBSxYGYd2lhLWvQV'  # Replace with your correct Google Drive folder ID

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store file paths temporarily and user states
user_files = defaultdict(str)
user_states = defaultdict(str)
password = "Parassocteamup"  # Replace with your password

async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_states[user.id] = "awaiting_password"
    await update.message.reply_text('Please enter the password to proceed.')

async def verify_password(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    text = update.message.text.strip()
    if user_states.get(user.id) == "awaiting_password":
        if text == password:
            user_states[user.id] = "verified"
            await update.message.reply_text('Password verified. Now you can send an image.')
        else:
            await update.message.reply_text('Incorrect password. Please try again.')
    else:
        await handle_message(update, context)

def upload_to_drive(file_path: str, file_name: str):
    file_metadata = {
        'name': file_name,
        'parents': [FOLDER_ID]  # Specify the folder ID here
    }
    media = MediaFileUpload(file_path, mimetype='image/jpeg')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, parents').execute()
    return file.get('id'), file.get('parents')[0]

async def handle_photo(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    if user_states.get(user.id) == "verified":
        photo_file = await update.message.photo[-1].get_file()
        file_name = f"{user.id}_{photo_file.file_id}.jpg"
        file_path = os.path.join('/tmp', file_name)
        await photo_file.download_to_drive(file_path)
        
        # Store file path temporarily
        user_files[user.id] = file_path

        await update.message.reply_text('Image received. Now send me the name to save the image.')
    else:
        await update.message.reply_text('Please enter the password first by using /start.')

async def handle_message(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    text = update.message.text.strip()
    
    if user_states.get(user.id) == "verified":
        if user.id in user_files:
            file_path = user_files[user.id]
            if text:
                # Upload to Google Drive with the provided name
                drive_file_id, folder_id = upload_to_drive(file_path, text + '.jpg')
                await update.message.reply_text(f"Image uploaded with name '{text}'")
                # Remove the downloaded file
                os.remove(file_path)
                del user_files[user.id]
            else:
                await update.message.reply_text('Please provide a name for the image.')
        else:
            await update.message.reply_text('No image received. Please send an image first.')
    else:
        await update.message.reply_text('Please enter the password first by using /start.')

def main():
    # Initialize the Application with your bot token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verify_password))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
