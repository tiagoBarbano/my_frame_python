# Etapa base
FROM node:20-slim AS base

# Diretório de trabalho
WORKDIR /app

# Copia arquivos de dependência
COPY package*.json ./

# Instala dependências de produção e o PM2 globalmente
RUN npm ci --omit=dev && npm install -g pm2

# Copia o restante da aplicação
COPY . .

# Expõe a porta do Fastify (por padrão 3000)
EXPOSE 3000

# Inicia com PM2 (modo fork)
CMD ["pm2-runtime", "--no-daemon", "--instances", "2", "index.js"]

