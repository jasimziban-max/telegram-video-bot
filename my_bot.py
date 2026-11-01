import os
import asyncio
import yt_dlp
import http.server
import socketserver
import threading
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
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("⚠️ দয়া করে শুধু সঠিক ভিডিওর লিংক পাঠান।")
        return

    await update.message.reply_text("⏳ ভিডিও ডাউনলোড হচ্ছে... একটু অপেক্ষা করুন।")

    # Render Environment Variable থেকে কুকিজ নেওয়া হচ্ছে
    cookies_content = os.environ.get("YTDLP_COOKIES")
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'nocheckcertificate': True
    }

    # যদি Environment Variable-এ কুকিজ থাকে, তবে সেটি যোগ করা হচ্ছে
    if cookies_content:
        ydl_opts['http_headers'] = {'Cookie': cookies_content}

    try:
        loop = asyncio.get_event_loop()
        
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith('.mp4'):
                    filename = os.path.splitext(filename)[0] + '.mp4'
                return filename

        filepath = await loop.run_in_executor(None, download)

        # টেলিগ্রামের ৫০ MB লিমিট চেক
        if os.path.getsize(filepath) > 50 * 1024 * 1024:
            await update.message.reply_text("❌ দুঃখিত, ভিডিওটির সাইজ ৫০ MB এর বেশি।")
            os.remove(filepath)
            return

        await update.message.reply_video(video=open(filepath, 'rb'), supports_streaming=True)
        os.remove(filepath)
        
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text(f"❌ ডাউনলোড করা সম্ভব হয়নি। এরর: {str(e)[:100]}")

def main():
    # ১. Render-এর পোর্ট স্ক্যান টাইমআউট এড়াতে ডামি ওয়েব সার্ভার
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("0.0.0.0", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print(f"ডামি ওয়েব সার্ভার পোর্ট {port}-এ চালু হয়েছে।")

    # ২. টেলিগ্রাম বট চালু করা
    print("বট চালু হচ্ছে...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.run_polling()

if __name__ == "__main__":
    main()