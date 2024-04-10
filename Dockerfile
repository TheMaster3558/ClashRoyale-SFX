FROM python:3.12-slim

WORKDIR /bot

COPY requirements.txt .
RUN apt-get update && apt-get install -y ffmpeg
RUN wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip && \
    unzip ngrok-stable-linux-amd64.zip && \
    mv ngrok /usr/local/bin/ && \
    rm ngrok-stable-linux-amd64.zip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "ClashRoyale_SFX"]
