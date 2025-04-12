FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .


RUN npm run build

FROM node:18-alpine

WORKDIR /app

RUN npm install -g pm2
RUN npm install -g serve


COPY --from=build /app/dist ./dist


COPY ecosystem.config.js .


EXPOSE 3000


CMD ["pm2", "start", "ecosystem.config.js"]
