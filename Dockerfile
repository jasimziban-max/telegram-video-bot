FROM python:3.10-slim

# FFmpeg, Node.js এবং Deno ইনস্টল করা (YouTube এর জন্য)
RUN apt-get update && apt-get install -y ffmpeg nodejs curl unzip && \
    curl -fsSL https://deno.land/install.sh | sh -s -- -y

# Deno এর PATH সেট করা
ENV PATH="/root/.deno/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render এর জন্য পোর্ট এক্সপোজ করা
EXPOSE 10000

CMD ["python", "my_bot.py"]