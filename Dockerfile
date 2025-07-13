FROM python:3.11-slim

WORKDIR /app

COPY app.py .
COPY index.html ./templates/index.html

RUN pip install flask paramiko

EXPOSE 5000

CMD ["python", "app.py"]
