from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from pytube import YouTube
import os

# توکن ربات تلگرام
TOKEN = '7556835288:AAG7A_4me2tYgQheixdMOt5njYZO0DTWjuM'

# دستور شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک یوتیوب خود را ارسال کنید.")

# دریافت لینک یوتیوب و نمایش کیفیت‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        
        # ایجاد دکمه‌های کیفیت
        buttons = []
        for stream in streams:
            buttons.append([InlineKeyboardButton(stream.resolution, callback_data=stream.itag)])
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("لطفاً کیفیت مورد نظر را انتخاب کنید:", reply_markup=reply_markup)
        
        # ذخیره اطلاعات ویدیو در context
        context.user_data['video_url'] = url
    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")

# دانلود ویدیو با کیفیت انتخابی
async def handle_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    itag = query.data
    url = context.user_data.get('video_url')
    
    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(itag)
        file_path = stream.download(output_path='downloads')
        
        # ارسال ویدیو به کاربر
        with open(file_path, 'rb') as video_file:
            await query.message.reply_video(video=video_file, caption="ویدیو شما آماده است!")
        
        # حذف فایل موقت
        os.remove(file_path)
    except Exception as e:
        await query.message.reply_text(f"خطا در دانلود ویدیو: {e}")

def main():
    # ایجاد برنامه تلگرام
    application = Application.builder().token(TOKEN).build()
    
    # ثبت دستورات و handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_quality))
    
    # اجرای ربات
    application.run_polling()

if __name__ == "__main__":
    main()