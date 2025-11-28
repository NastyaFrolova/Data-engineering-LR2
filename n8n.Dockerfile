FROM n8nio/n8n:latest

# Переключаемся на root, чтобы установить пакеты
USER root

# Обновляем список пакетов и устанавливаем ffmpeg, --no-cache уменьшает размер образа
RUN apk update && apk add --no-cache ffmpeg

# Возвращаемся на пользователя для безопасности
USER node