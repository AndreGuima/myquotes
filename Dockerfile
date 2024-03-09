# Stage 1: Build the application
FROM node:latest as build

WORKDIR /usr/app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build --prod

# Stage 2: Serve the application
FROM node:latest

WORKDIR /usr/app

COPY --from=build /usr/app/dist .

COPY server.js .

RUN npm install express

EXPOSE 80

CMD ["node", "server.js"]
