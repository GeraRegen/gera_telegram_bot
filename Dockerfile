FROM python:3.9
WORKDIR /app
COPY requirements.txt .  ← Сначала копируем ТОЛЬКО requirements
RUN pip install -r requirements.txt
COPY . .                ← Затем остальные файлы
CMD ["python", "Gera_Bot.py"]
