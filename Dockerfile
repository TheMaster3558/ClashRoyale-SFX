FROM python:3.12-slim

WORKDIR /bot

COPY requirements.txt .
RUN sudo apt update && sudo apt install snapd && \
    sudo snap install ngrok && \
    sudo snap install ffmpeg && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "ClashRoyale_SFX"]
