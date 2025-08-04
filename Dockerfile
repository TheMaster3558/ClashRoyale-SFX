FROM python:3.13-slim

WORKDIR /bot

COPY requirements.txt .
RUN apt-get update && apt-get install -y git ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "ClashRoyale_SFX"]
