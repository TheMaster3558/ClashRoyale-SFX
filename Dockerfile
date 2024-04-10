FROM python:3.12-slim

WORKDIR /bot

COPY requirements.txt .
RUN apt update && apt install -y snapd
RUN snap install ngrok
RUN snap install ffmpeg
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

CMD ["python", "-m", "ClashRoyale_SFX"]
