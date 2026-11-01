import os
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# আপনার বট টোকেন
TOKEN = "9022816346:AAGRGIwL75HvOPqytVFqFRFsiyRhVHEIxXk"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 স্বাগতম!\nযেকোনো ভিডিওর লিংক পাঠান, আমি সরাসরি সর্বোচ্চ কোয়ালিটির ভিডিও পাঠাবো।")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # চেক করা হচ্ছে এটি আসলেই একটি লিংক কিনা
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("⚠️ দয়া করে শুধু সঠিক ভিডিওর লিংক পাঠান।")
        return

    await update.message.reply_text("⏳ ভিডিও ডাউনলোড হচ্ছে... একটু অপেক্ষা করুন।")

    # সর্বোচ্চ রেজোলিউশনের ভিডিও এবং অডিও ডাউনলোড করে mp4 ফরম্যাটে মার্জ করার সেটিংস
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best', 
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True
    }

    try:
        loop = asyncio.get_event_loop()
        
        # ডাউনলোড ফাংশন (আলাদা থ্রেডে চালানো হবে যাতে বট হ্যাং না করে)
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp4'):
                    filename = os.path.splitext(filename)[0] + '.mp4'
                return filename

        filepath = await loop.run_in_executor(None, download)

        # টেলিগ্রামের ৫০ MB লিমিট চেক করা
        if os.path.getsize(filepath) > 50 * 1024 * 1024:
            await update.message.reply_text("❌ দুঃখিত, ভিডিওটির সাইজ ৫০ MB এর বেশি, যা টেলিগ্রাম বটে পাঠানো সম্ভব নয়।")
            os.remove(filepath) # বড় ফাইল ডিলিট করে দেওয়া
            return

        # ভিডিও পাঠানো
        await update.message.reply_video(video=open(filepath, 'rb'), supports_streaming=True)
        
        # পাঠানো শেষে ফাইলটি ডিলিট করে দেওয়া
        os.remove(filepath)
        
    except Exception as e:
        await update.message.reply_text("❌ ডাউনলোড করা সম্ভব হয়নি। লিংকটি সঠিক কিনা অথবা সার্ভারে FFmpeg ইনস্টল আছে কিনা চেক করুন।")

def main():
    print("বট চালু হচ্ছে...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # শুধুমাত্র টেক্সট মেসেজ (লিংক) ফিল্টার করা হচ্ছে
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.run_polling()

if __name__ == "__main__":
    main()