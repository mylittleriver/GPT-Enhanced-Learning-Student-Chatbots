FROM python:3.9-slim

WORKDIR /app

RUN pip install streamlit

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["streamlit","run","app.py","--server.port","8080"]
