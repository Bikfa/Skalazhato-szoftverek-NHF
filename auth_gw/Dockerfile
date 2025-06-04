# dog_project/auth_gw/Dockerfile
FROM node:18-alpine

WORKDIR /app

# A függőségek telepítése
COPY package.json package-lock.json* ./
RUN npm install --production

# Forráskód bemásolása
COPY . .

# Port, amin a szolgáltatás fut
EXPOSE 4000

CMD ["node", "app.js"]
