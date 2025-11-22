import os
import json
from telegram import Update, ChatMember, ChatMemberUpdated
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler, MessageHandler, filters
from flask import Flask
from threading import Thread

# Flask app for keeping the bot alive on Replit
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default config
        return {
            "total_vouches": 0,
            "admin_id": None,  # You need to set this
            "channel_id": None,  # You need to set this
            "bot_token": None   # You need to set this
        }

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

# Initialize config
config = load_config()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    config = load_config()
    await update.message.reply_text(f"The admin currently has {config['total_vouches']} vouches.")

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new messages in the vouch channel"""
    config = load_config()
    
    # Check if message is from the configured channel
    if update.channel_post.chat.id == config['channel_id']:
        # Increment voucher count
        config['total_vouches'] += 1
        save_config(config)
        
        # Send notification to admin
        if config['admin_id']:
            try:
                await context.bot.send_message(
                    chat_id=config['admin_id'],
                    text=f"New vouch received! Total vouches: {config['total_vouches']}"
                )
            except Exception as e:
                print(f"Error sending notification to admin: {e}")

def main():
    # Load configuration
    config = load_config()
    
    # Check if bot token is set
    if not config.get('bot_token'):
        print("ERROR: Please set your BOT_TOKEN in config.json")
        return
    
    # Start Flask server in a separate thread for keep-alive
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Create Telegram application
    application = Application.builder().token(config['bot_token']).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))
    
    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
