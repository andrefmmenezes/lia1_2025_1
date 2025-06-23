FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

# Instala ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg \
    &&  apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install --force-reinstall numpy==1.26.4

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
