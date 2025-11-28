import os
import tempfile
import asyncio
#import auto_subtitle
import subprocess

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse

# Получаем параметры модели из окружения, на всякий случай добавлены параметры по умолчанию
# В этот раз pydantic не использовался
model_type = os.getenv("WHISPER_MODEL", "base")
device_type = os.getenv("WHISPER_DEVICE", "cpu")

app = FastAPI(title="Transcription Service with auto_subtitle")

# Генерирует английские субтитры
def transcribe_video_sync(video_path: str) -> str:
    print(f"Start Transcription processing: {video_path}")

    # Временная директорию, которую потом удаляем
    with tempfile.TemporaryDirectory() as tmp_dir:
        srt_file = None

        try:
            # Команда для вызова
            cmd = [
                "auto_subtitle",
                video_path,
                "--output_dir", tmp_dir,
                "--srt_only", "true", # Выводить только субтитры
                "--model", model_type, # Модель whisper, ранее указали или взяли по умолчанию
                #"--device", device_type, # При GPU, проверка была на CPU
                "--task", "transcribe", # Субтитры без перевода
                "--verbose", "true", # Подробный вывод, полезно для отладки
            ]

            subprocess.run(cmd, check=True)

            # Ищем .srt, созданный auto_subtitle
            srt_file = None
            for fname in os.listdir(tmp_dir):
                if fname.endswith(".srt"): # Ищем любой srt
                    srt_file = os.path.join(tmp_dir, fname)
                    break

            if not srt_file: # Проверка на случай отсутствия файла
                raise FileNotFoundError("SRT file not found in output directory")

            # Читаем содержимое
            with open(srt_file, "r", encoding="utf-8") as f:
                srt_content = f.read()

            print("Transcription process success.")
            return srt_content

        except subprocess.CalledProcessError as e:
            # Отлавливаем ошибки
            print("Auto-subtitle error:", e.stderr)
            raise e
        #finally:
        # Удаляем временный файл
         #   if os.path.exists(srt_file):
           #     os.remove(srt_file)


# Берем файл и возвращаем английские субтитры
@app.post("/transcribe/")
async def transcribe_video(video: UploadFile = File(...)):
    # Проверка типа перед стартом
    if not video.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Not video.")

    input_video_path = None

    try:
        # Сохраняем входной файл, временно
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as tmp_input: # Удаляем после закрытия
            content = await video.read()
            tmp_input.write(content)
            tmp_input.flush()
            # Путь файла для дальнешей передачи
            input_video_path = tmp_input.name

            # Запускаем траскрипцию в отдельном потоке
            loop = asyncio.get_event_loop()
            srt_content = await loop.run_in_executor(
                None, transcribe_video_sync, input_video_path
            )

        # Возвращаем текст субтитров
        #return PlainTextResponse(content=srt_content, media_type="text/plain; charset=utf-8")
        # Разбиение показалось удобнее и приятнее глазу
        return PlainTextResponse(
            content=srt_content,
            media_type="text/plain; charset=utf-8"
        )

    except Exception as e:
        # Выводим ошибку в консоль Docker-контейнера
        print(f"Error Transcription: {e}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


# health проверка на доступность, можно проверить по ссылке в браузере
@app.get("/health")
def health_check():
    return {"status": "ok"}