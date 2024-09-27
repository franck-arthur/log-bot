import os
import json
import logging
import requests
import telegram
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Telegram bot token and chat ID
token = os.getenv('TOKEN')
chat_id = os.getenv('CHAT_ID')

# Webhook URL for sending data
webhook_url = os.getenv('WEBHOOK_URL')  # Ensure this is set in your .env file
webapp_url = os.getenv('WEBAPP_URL')  # Ensure this is set in your .env file

# Initialize the bot
bot = telegram.Bot(token=token)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message and display the WebApp button."""
    await update.message.reply_text(
        "Welcome to the BOT Service! Click on the 'Service Client' button below to submit your data.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Service client",
                web_app=WebAppInfo(url=webapp_url),
            )
        ),
    )

# Function to send data to the webhook
def send_to_webhook(payload: dict) -> None:
    """Send the formatted data to a webhook URL."""
    try:
        headers = {'Content-Type': 'application/json'}
        
        # Log the data being sent
        logger.info(f"Sending the following data to the webhook: {json.dumps(payload, indent=2)}")

        response = requests.post(webhook_url, headers=headers, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            logger.info("Data successfully sent to the webhook.")
        else:
            logger.error(f"Failed to send data to webhook. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        logger.error(f"An error occurred while sending data to the webhook: {e}")

# Function to create the formatted payload
def format_payload(update: Update, web_app_data: dict) -> dict:
    """Create a new payload format using the Update object and WebApp data."""
    # Extract user and chat information from the Update object
    user_info = update.effective_user
    chat_info = update.effective_chat
    message = update.effective_message

    # Creating the new formatted payload
    formatted_payload = {
        "update_id": update.update_id,
        "message": {
            "message_id": message.message_id,
            "from": {
                "id": user_info.id,
                "is_bot": user_info.is_bot,
                "first_name": user_info.first_name,
                "last_name": user_info.last_name,
                "username": user_info.username,
                "language_code": user_info.language_code
            },
            "chat": {
                "id": chat_info.id,
                "first_name": chat_info.first_name,
                "last_name": chat_info.last_name,
                "username": chat_info.username,
                "type": chat_info.type
            },
            "date": message.date.isoformat(),  # Converting date to ISO format
            "text": message.text,
            "attachment": {
                "type": "OtherOrNone"  # Assuming attachment type is 'OtherOrNone'
            },
            "web_app_data": web_app_data  # Include WebApp data in the payload
        }
    }

    return formatted_payload

# Function to handle incoming WebApp data
async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the incoming WebApp data and send it to the webhook."""
    try:
        # Extract the raw WebApp data from the incoming message
        raw_web_app_data = json.loads(update.effective_message.web_app_data.data)

        # Log the received WebApp data
        logger.info(f"Received WebApp data: {json.dumps(raw_web_app_data, indent=2)}")

        # Format the payload using both WebApp data and Update object information
        formatted_payload = format_payload(update, raw_web_app_data)

        # Send the formatted payload to the webhook
        send_to_webhook(formatted_payload)

        # Construct a response message to show in Telegram
        response_message = (
            f"Data received and sent to the webhook:\n\n"
            f"<b>Update ID:</b> {formatted_payload['update_id']}\n"
            f"<b>Message ID:</b> {formatted_payload['message']['message_id']}\n"
            f"<b>From:</b> {formatted_payload['message']['from']['first_name']} "
            f"{formatted_payload['message']['from']['last_name']} (@{formatted_payload['message']['from']['username']})\n"
            f"<b>Text:</b> {formatted_payload['message']['text']}\n"
            f"<b>Attachment Type:</b> {formatted_payload['message']['attachment']['type']}\n"
            f"<b>WebApp Data:</b> {json.dumps(formatted_payload['message']['web_app_data'], indent=2)}\n"
        )

        # Send the confirmation message to the Telegram chat
        await update.message.reply_html(
            text=response_message,
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception as e:
        logger.error(f"Error handling WebApp data: {e}")
        await update.message.reply_text("An error occurred while processing your data. Please try again later.")

if __name__ == '__main__':
    app = Application.builder().token(token).build()

    # Add handlers for start command and WebApp data
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    # Run the bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)
