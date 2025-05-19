# Etapa de build (opcional se não usar TypeScript ou build tools)
FROM node:20-alpine AS base

# Define diretório de trabalho
WORKDIR /app

# Copia apenas os arquivos necessários para instalar as dependências
COPY package*.json ./

# Instala apenas as dependências de produção
RUN npm ci --omit=dev

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta que o Fastify vai escutar (por padrão, 3000)
EXPOSE 3000

# Comando para iniciar a aplicação
CMD ["node", "index.js"]