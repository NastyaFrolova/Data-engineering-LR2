FROM python:3.9-slim

WORKDIR /app

# Устанавливаем системные зависимости, включая ffmpeg для Whisper
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg curl


COPY requirements.txt .
# Здесь была попытка установить torch для одного лишь cpu, так как он тяжелый
# В итоге все же решила оставить так, auto-subtitle также ставит torch, так что можно просто оставить один auto-subtitle
RUN pip install --no-cache-dir torch && pip install --no-cache-dir auto-subtitle -r requirements.txt

COPY . .

# Создаем папку для временных файлов, которая будет смонтирована как volume
RUN mkdir -p /tmp/n8n-workflow-files

# Указываем порт, наше приложение, другие детали
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]