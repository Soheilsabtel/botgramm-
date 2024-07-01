import logging
import os
from telegram import Update, Contact, Document
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define your token
TOKEN = '7355336086:AAEsd95L8idnREGWt39cjSSScUsuhnSqNHk'
# File to save contact IDs
ID_SAVE_FILE = 'contact_ids.txt'

# Define the start command handler
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    save_contact_id(user_id)
    update.message.reply_text('Hi! Share a contact with me, and I will tell you its ID and save it.')

# Define the contact handler
def contact_handler(update: Update, context: CallbackContext) -> None:
    contact: Contact = update.message.contact
    if contact.user_id is not None:
        contact_id = contact.user_id
        update.message.reply_text(f'The contact ID is: {contact_id}')
        save_contact_id(contact_id)
    else:
        update.message.reply_text('The contact does not have a Telegram user ID.')

# Function to save the contact ID to a file
def save_contact_id(contact_id: int) -> None:
    contact_ids = read_contact_ids()
    if contact_id not in contact_ids:
        with open(ID_SAVE_FILE, 'a') as file:
            file.write(f'{contact_id}\n')

# Function to read contact IDs from file
def read_contact_ids() -> list:
    if not os.path.exists(ID_SAVE_FILE):
        return []
    with open(ID_SAVE_FILE, 'r') as file:
        contact_ids = [line.strip() for line in file.readlines()]
    return contact_ids

# Define the file upload handler
def file_upload_handler(update: Update, context: CallbackContext) -> None:
    document: Document = update.message.document
    file_id = document.file_id
    file = context.bot.get_file(file_id)
    file_path = os.path.join("downloads", document.file_name)
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.download(file_path)
    
    update.message.reply_text(f'File {document.file_name} uploaded successfully.')
    
    send_file_to_contacts(file_path, update, context)

# Function to send the uploaded file to saved contacts
def send_file_to_contacts(file_path: str, update: Update, context: CallbackContext) -> None:
    contact_ids = read_contact_ids()
    if not contact_ids:
        update.message.reply_text('No saved contact IDs to send the file to.')
        return

    successful_sends = 0
    for contact_id in contact_ids:
        try:
            context.bot.send_document(chat_id=int(contact_id), document=open(file_path, 'rb'))
            successful_sends += 1
        except Exception as e:
            logger.error(f'Failed to send file to {contact_id}: {e}')
    
    update.message.reply_text(f'File sent to {successful_sends} contacts.')

# Define the main function to start the bot
def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))
    dispatcher.add_handler(MessageHandler(Filters.document, file_upload_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
