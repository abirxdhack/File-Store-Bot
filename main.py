import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import threading
import requests

# Replace with your bot's token
API_TOKEN = 'Your Bot Token Goes Here'
bot = telebot.TeleBot(API_TOKEN)

# Dictionary to store file data with unique identifiers
file_storage = {}
# Dictionary to store user settings
user_settings = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    command_parts = message.text.split()
    if len(command_parts) > 1:
        # Handle file retrieval if a file ID is passed
        file_id = command_parts[1]
        if file_id in file_storage:
            file_info = file_storage[file_id]
            file_type = file_info['type']
            if file_type == 'document':
                bot.send_document(message.chat.id, file_info['file_id'])
            elif file_type == 'photo':
                bot.send_photo(message.chat.id, file_info['file_id'])
            elif file_type == 'video':
                bot.send_video(message.chat.id, file_info['file_id'])
            elif file_type == 'audio':
                bot.send_audio(message.chat.id, file_info['file_id'])
            elif file_type == 'text':
                bot.send_message(message.chat.id, f"📄 Text Content:\n\n{file_info['content']}")
            return

    # Default welcome message with channel join prompt
    user_name = message.from_user.first_name or "User"
    welcome_text = (
        f"⚡ <b>Hello {user_name}</b>\n\n"
        "⚡️ Pʟs Jᴏɪɴ Oᴜʀ Mᴀɪɴ Cʜᴀɴɴᴇʟ\nAɴᴅ EɴJᴏʏ Oᴜʀ Lᴏᴏᴛs.."
    )
    
    # Buttons for joining channels
    join_markup = InlineKeyboardMarkup(row_width=1)
    join_markup.add(
        InlineKeyboardButton("Join Main Channel", url="https://t.me/ModVipRM"),
        InlineKeyboardButton("Join Developer Channel", url="https://t.me/ModviprmBackup"),
        InlineKeyboardButton("Check Membership", callback_data="check_membership")
    )
    
    # Send welcome message with join buttons
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="HTML",
        reply_markup=join_markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check_membership(call):
    user_id = call.message.chat.id
    channels = ["@abir_x_official", "@abir_x_official_developer"]
    
    try:
        for channel in channels:
            member_status = bot.get_chat_member(channel, user_id).status
            if member_status not in ["member", "administrator", "creator"]:
                bot.send_message(
                    call.message.chat.id,
                    "❌ You need to join all channels to access the bot's features."
                )
                return
        
        # Show the main menu if the user is a member of both channels
        main_menu(call.message.chat.id)
    
    except Exception as e:
        bot.send_message(
            call.message.chat.id,
            "❌ Unable to verify membership. Please ensure the channels are public and accessible."
        )
        print(f"Error: {e}")

def main_menu(chat_id):
    # Main menu after joining channels
    menu = InlineKeyboardMarkup(row_width=2)
    menu.add(
        InlineKeyboardButton("Aᴅᴅ Fɪʟᴇ [Sɪɴɢʟᴇ]", callback_data="add_file"),
        InlineKeyboardButton("Lɪɴᴋ Sʜᴏʀᴛᴇɴᴇʀ", callback_data="link_shortener"),
        InlineKeyboardButton("Mᴜʟᴛɪᴘʟᴇ [Fɪʟᴇs]", callback_data="multiple_files"),
        InlineKeyboardButton("⚡ Eᴅɪᴛ [Sᴇᴛᴛɪɴɢs]", callback_data="edit_settings"),
        InlineKeyboardButton("Aʙᴏᴜᴛ Mᴇ", callback_data="about_me"),
        InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close")
    )
    bot.send_message(
        chat_id,
        "✅ You have joined all channels. Welcome to the main menu!",
        reply_markup=menu
    )


# Handler for the "Mᴜʟᴛɪᴘʟᴇ [Fɪʟᴇs]" button
@bot.callback_query_handler(func=lambda call: call.data == "multiple_files")
def multiple_files_handler(call):
    user_files = []
    file_storage[call.message.chat.id] = user_files
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("Aᴅᴅ Mᴏʀᴇ", callback_data="add_more"),
               InlineKeyboardButton("Cᴀɴᴄᴇʟ Tᴏ Aᴅᴅ", callback_data="back_to_main"))
    bot.send_message(
        call.message.chat.id,
        "🔥 Sᴇɴᴅ Mᴇssᴀɢᴇ Oʀ Fɪʟᴇs \nTʜᴀᴛ Yᴏᴜ Wᴀɴᴛ Tᴏ Aᴅᴅ...\n\nTᴏ Cᴀɴᴄᴇʟ: /cancel",
        reply_markup=markup
    )

# Helper function for generating shareable links
def generate_shareable_link(bot_username, unique_id):
    return f"https://t.me/{bot_username}?start={unique_id}"


# Process multiple file uploads
@bot.message_handler(
    func=lambda message: isinstance(file_storage.get(message.chat.id), list),
    content_types=['document', 'photo', 'video', 'audio', 'text']
)
def handle_multiple_file_upload(message):
    user_files = file_storage.get(message.chat.id, [])
    unique_id = str(uuid.uuid4())

    # Store file data globally by unique ID
    if message.document:
        file_data = {'type': 'document', 'file_id': message.document.file_id}
    elif message.photo:
        file_data = {'type': 'photo', 'file_id': message.photo[-1].file_id}
    elif message.video:
        file_data = {'type': 'video', 'file_id': message.video.file_id}
    elif message.audio:
        file_data = {'type': 'audio', 'file_id': message.audio.file_id}
    elif message.text:
        file_data = {'type': 'text', 'content': message.text}
    else:
        return

    # Save the file data globally
    file_storage[unique_id] = file_data
    user_files.append(unique_id)

    # Update user-specific file list
    file_storage[message.chat.id] = user_files

    if len(user_files) < 3:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Aᴅᴅ Mᴏʀᴇ", callback_data="add_more"),
            InlineKeyboardButton("Cᴀɴᴄᴇʟ Tᴏ Aᴅᴅ", callback_data="back_to_main")
        )
        bot.send_message(
            message.chat.id,
            f"✅ Fɪʟᴇ Uᴘʟᴏᴀᴅᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ...\n\nYᴏᴜ ʜᴀᴠᴇ Uᴘʟᴏᴀᴅᴇᴅ {len(user_files)} ғɪʟᴇs.",
            reply_markup=markup
        )
    else:
        bot_username = bot.get_me().username
        shareable_links = [
            generate_shareable_link(bot_username, file_id)
            for file_id in user_files
        ]

        links_text = "\n\n".join(shareable_links)
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Sʜᴀʀᴇ Lɪɴᴋs", callback_data="share_links"),
            InlineKeyboardButton("Rᴇᴛᴜʀɴ Bᴀᴄᴋ Tᴏ Mᴀɪɴ Mᴇɴᴜ", callback_data="back_to_main")
        )
        bot.send_message(
            message.chat.id,
            f"✅ Fɪʟᴇs Uᴘʟᴏᴀᴅᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ...\n\n⚡️ Sʜᴀʀᴇᴀʙʟᴇ Lɪɴᴋs:\n\n{links_text}",
            reply_markup=markup
        )
        # Clear user-specific list
        file_storage[message.chat.id] = []

@bot.callback_query_handler(func=lambda call: call.data == "add_more")
def add_more_files(call):
    bot.send_message(
        call.message.chat.id,
        "🔥 Sᴇɴᴅ Mᴏʀᴇ Mᴇssᴀɢᴇs Oʀ Fɪʟᴇs...\n\nTᴏ Cᴀɴᴄᴇʟ: /cancel"
    )


# Handler for the "Cᴀɴᴄᴇʟ Tᴏ Aᴅᴅ" button
@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main(call):
    send_welcome(call.message)

# Handle user cancellation with /cancel command
@bot.message_handler(commands=['cancel'])
def cancel_add_file(message):
    if isinstance(file_storage.get(message.chat.id), list):
        # Clear the file storage for the user
        file_storage[message.chat.id] = []
        bot.send_message(
            message.chat.id,
            "❌ Yᴏᴜ Hᴀᴠᴇ Cᴀɴᴄᴇʟʟᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ\nTᴏ Aᴅᴅ Fɪʟᴇs..."
        )
        send_welcome(message)


# Handler for the "Lɪɴᴋ Sʜᴏʀᴛᴇɴᴇʀ" button
@bot.callback_query_handler(func=lambda call: call.data == "link_shortener")
def link_shortener_handler(call):
    link_shortener_text = "🔥 Eɴᴛᴇʀ Yᴏᴜʀ Lɪɴᴋ..."
    link_shortener_markup = InlineKeyboardMarkup(row_width=1)
    link_shortener_markup.add(
        InlineKeyboardButton("Sʜᴏʀᴛᴇɴ Lɪɴᴋ", callback_data="generate_short_link"),
        InlineKeyboardButton("Rᴇᴛᴜʀɴ Bᴀᴄᴋ", callback_data="back_to_main")
    )
    bot.send_message(
        call.message.chat.id,
        link_shortener_text,
        reply_markup=link_shortener_markup
    )

# Handler for the "Generate Short Link" button
@bot.callback_query_handler(func=lambda call: call.data == "generate_short_link")
def generate_short_link(call):
    bot.send_message(
        call.message.chat.id,
        "🔥 Eɴᴛᴇʀ Yᴏᴜʀ Lɪɴᴋ..."
    )
    bot.register_next_step_handler(call.message, process_short_link)

def process_short_link(message):
    url = message.text.strip()
    try:
        response = requests.get(f'https://tinyurl.com/api-create.php?url={url}')
        short_link = response.text
        markup = InlineKeyboardMarkup(row_width=1)
        shorten_link_button = InlineKeyboardButton("Sʜᴏʀᴛᴇɴ Lɪɴᴋ", url=short_link)
        markup.add(shorten_link_button)
        bot.send_message(
            message.chat.id,
            "✅ Hᴇʀᴇ ɪs Yᴏᴜʀ Sʜᴏʀᴛᴇɴᴇᴅ Lɪɴᴋ:",
            reply_markup=markup
        )
    except:
        bot.send_message(
            message.chat.id,
            "❌ Iɴᴠᴀʟɪᴅ Uʀʟ..."
        )

# Handler for the "⚡ Edit [Settings]" button
@bot.callback_query_handler(func=lambda call: call.data == "edit_settings")
def edit_settings(call):
    user_id = call.message.chat.id
    if user_id not in user_settings:
        user_settings[user_id] = {"auto_delete": False, "protect_content": False}

    settings_text = "⚙️ <b>Eᴅɪᴛ Sᴇᴛᴛɪɴɢs</b>"
    settings_markup = InlineKeyboardMarkup(row_width=1)

    auto_delete_button_text = "Auto Delete: On 🔥" if user_settings[user_id]["auto_delete"] else "Auto Delete: Off"
    settings_markup.add(InlineKeyboardButton(auto_delete_button_text, callback_data="toggle_auto_delete"))

    protect_content_button_text = "Protect Content: On 🔒" if user_settings[user_id]["protect_content"] else "Protect Content: Off"
    settings_markup.add(InlineKeyboardButton(protect_content_button_text, callback_data="toggle_protect_content"))

    settings_markup.add(InlineKeyboardButton("Return Back To Page", callback_data="back_to_main"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=settings_text,
        parse_mode="HTML",
        reply_markup=settings_markup
    )

# Handler for toggling auto delete
@bot.callback_query_handler(func=lambda call: call.data == "toggle_auto_delete")
def toggle_auto_delete(call):
    user_id = call.message.chat.id
    user_settings[user_id]["auto_delete"] = not user_settings[user_id]["auto_delete"]
    edit_settings(call)

# Handler for toggling protect content
@bot.callback_query_handler(func=lambda call: call.data == "toggle_protect_content")
def toggle_protect_content(call):
    user_id = call.message.chat.id
    user_settings[user_id]["protect_content"] = not user_settings[user_id]["protect_content"]
    edit_settings(call)

# Handler for the "Add File [Single]" button
@bot.callback_query_handler(func=lambda call: call.data == "add_file")
def add_file_prompt(call):
    bot.send_message(
        call.message.chat.id,
        "🔥 Sᴇɴᴅ Mᴇssᴀɢᴇ Oʀ Fɪʟᴇ \nTʜᴀᴛ Yᴏᴜ Wᴀɴᴛ Tᴏ Aᴅᴅ...\n\nTᴏ Cᴀɴᴄᴇʟ: /cancel"
    )
    file_storage[call.message.chat.id] = "awaiting_file"

# Handle file upload
@bot.message_handler(func=lambda message: file_storage.get(message.chat.id) == "awaiting_file", content_types=['document', 'photo', 'video', 'audio', 'text'])
def handle_file_upload(message):
    unique_id = str(uuid.uuid4())
    
    if message.document:
        file_storage[unique_id] = {'type': 'document', 'file_id': message.document.file_id}
    elif message.photo:
        file_storage[unique_id] = {'type': 'photo', 'file_id': message.photo[-1].file_id}
    elif message.video:
        file_storage[unique_id] = {'type': 'video', 'file_id': message.video.file_id}
    elif message.audio:
        file_storage[unique_id] = {'type': 'audio', 'file_id': message.audio.file_id}
    elif message.text:
        file_storage[unique_id] = {'type': 'text', 'content': message.text}
    
    file_storage[message.chat.id] = None
    file_link = f"https://t.me/{bot.get_me().username}?start={unique_id}"
    bot.send_message(
        message.chat.id,
        f"✅ Uᴘʟᴏᴀᴅᴇᴅ SᴜᴄᴄᴇssFᴜʟʟʏ...\n\n⚡️ Lɪɴᴋ:\n{file_link}"
    )

    if user_settings.get(message.chat.id, {}).get("auto_delete", False):
        def delete_file():
            del file_storage[unique_id]
            bot.send_message(message.chat.id, f"❌ Fɪʟᴇ [{unique_id}] Hᴀs Bᴇᴇɴ Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ Dᴇʟᴇᴛᴇᴅ")
        timer = threading.Timer(1800, delete_file)  # 30 minutes
        timer.start()

# Handler for the "Aʙᴏᴜᴛ Mᴇ" button
@bot.callback_query_handler(func=lambda call: call.data == "about_me")
def about_me(call):
    about_text = (
        "╔════════════⦿\n"
        "├⋗ Cʀᴇᴀᴛᴏʀ:  ⏤͟͞〲ᗩᗷiᖇ 𓊈乂ᗪ𓊉\n"
        "├⋗ Lᴀɴɢᴜᴀɢᴇ: Pʏᴛʜᴏɴ\n"
        "├⋗ Bᴏᴛ Usᴇʀɴᴀᴍᴇ: @Kalyani_Priya_Darshan_Bot\n"
        "├⋗ Mᴀɪɴ Cʜᴀɴɴᴇʟ: @ModVipRM\n"
        "├⋗ Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ: @ModVipRM_Discussion\n"
        "╚═════════════════⦿"
    )
    close_markup = InlineKeyboardMarkup(row_width=1)
    close_markup.add(InlineKeyboardButton("Cʟᴏsᴇ", callback_data="close"))
    bot.send_message(call.message.chat.id, about_text, reply_markup=close_markup)

# Handler for the "Close" button
@bot.callback_query_handler(func=lambda call: call.data == "close")
def close(call):
    send_welcome(call.message)

# Start polling to keep the bot running
bot.polling()
