FROM python:3.10-alpine

WORKDIR /app

# Flask futtatásához nem kell külön rendszercsomag, de bash-et hozzáadjuk, ha scriptelés kellene
RUN apk add --no-cache bash

# Python-csomagok telepítése
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Környezeti változókat tartalmazó .env fájl másolása
COPY .env .env

# A teljes frontend könyvtár másolása
COPY . .

# Flask alkalmazás indítása
CMD ["python", "app.py"]