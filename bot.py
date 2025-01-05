from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from yt_dlp import YoutubeDL
import os

# توکن ربات تلگرام
TOKEN = '7556835288:AAG7A_4me2tYgQheixdMOt5njYZO0DTWjuM'

# تابع برای دریافت اطلاعات ویدیو
def get_video_info(url):
    ydl_opts = {}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

# تابع شروع
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('سلام! لطفا لینک یوتیوب را ارسال کنید.')

# تابع دریافت لینک و نمایش کیفیت‌ها
def handle_message(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    try:
        # دریافت اطلاعات ویدیو
        info = get_video_info(url)
        formats = info.get('formats', [])
        
        # ایجاد دکمه‌های کیفیت
        keyboard = []
        for f in formats:
            if f.get('resolution') and f.get('filesize'):
                button = InlineKeyboardButton(
                    f"{f['resolution']} ({round(f['filesize'] / (1024 * 1024), 2)} MB)",
                    callback_data=f"{f['format_id']}|{url}"
                )
                keyboard.append([button])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('لطفا کیفیت مورد نظر را انتخاب کنید:', reply_markup=reply_markup)
    except Exception as e:
        update.message.reply_text(f'خطا: {e}')

# تابع دانلود ویدیو
def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    # دریافت اطلاعات از دکمه
    format_id, url = query.data.split('|')
    
    try:
        # دانلود ویدیو با کیفیت انتخاب شده
        ydl_opts = {
            'format': format_id,
            'outtmpl': '%(title)s.%(ext)s',
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        
        # ارسال ویدیو به کاربر
        with open(file_path, 'rb') as video_file:
            query.message.reply_video(video_file)
        
        # حذف فایل پس از ارسال
        os.remove(file_path)
    except Exception as e:
        query.message.reply_text(f'خطا: {e}')

# تابع اصلی
def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(CallbackQueryHandler(handle_callback))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
