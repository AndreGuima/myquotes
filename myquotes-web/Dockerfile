# ============================
# 1) Build da aplicação (Vite + React)
# ============================
FROM node:20 AS build
WORKDIR /app

# Copia só package.json primeiro (melhor cache)
COPY package*.json ./

# Instala dependências
RUN npm install

COPY . .

RUN npm run build

# ============================
# 2) Servir com Nginx
# ============================
FROM nginx:1.25-alpine

# Copia build do Vite para a pasta publica do nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Remove configuração default do nginx
RUN rm /etc/nginx/conf.d/default.conf

# Instala nossa configuração
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
