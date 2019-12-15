FROM node:latest

COPY . /app
WORKDIR /app

RUN npm install
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

EXPOSE 80

CMD yarn serve

