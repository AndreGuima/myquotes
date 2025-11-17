# ============================
# 1) Build da aplicação (Vite + React)
# ============================
FROM node:20 AS build
WORKDIR /app

# Copia apenas package.json para instalar dependências
COPY package*.json ./
RUN npm install

# Copia todos os arquivos do projeto
COPY . .

# Garante que o .env.production usado no build seja o correto
COPY .env.production .env.production

# Build para produção
RUN npm run build


# ============================
# 2) Servir com Nginx
# ============================
FROM nginx:1.25-alpine

# Remove configuração default
RUN rm /etc/nginx/conf.d/default.conf

# Copia build do Vite
COPY --from=build /app/dist /usr/share/nginx/html

# Copia configuração do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
