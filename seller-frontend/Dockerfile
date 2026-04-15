FROM node:20-alpine

WORKDIR /app

COPY seller-frontend/package.json seller-frontend/yarn.lock* ./

RUN yarn install

COPY seller-frontend .

EXPOSE 5172

CMD ["yarn", "dev", "--host", "0.0.0.0", "--port", "5172"]