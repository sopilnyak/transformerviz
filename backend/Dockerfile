FROM python:3.6.8

COPY backend /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

EXPOSE 5000

CMD python app.py

