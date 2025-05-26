# Etapa base
FROM node:20-alpine AS base

WORKDIR /app

# Copia arquivos de dependência
COPY package*.json ./

# Instala dependências de produção e pm2 globalmente
RUN npm ci --omit=dev && npm install -g pm2

# Copia o restante da aplicação
COPY . .

# Expõe as portas da API e do exporter
EXPOSE 3000 9209

# Inicia API via pm2-runtime e o exporter via node simultaneamente, mantendo o container vivo
CMD ["sh", "-c", "pm2-runtime --no-daemon --instances 2 index.js & node pm2_exporter.js & wait"]
