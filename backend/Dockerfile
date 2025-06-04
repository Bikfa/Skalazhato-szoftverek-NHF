FROM python:3.10-alpine

WORKDIR /app

# Telepítjük a MySQL-hez szükséges build-eszközöket
RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Létrehozzuk az uploads mappát, ha nincs
RUN mkdir -p /app/uploads

COPY . .

CMD ["python", "app.py"]