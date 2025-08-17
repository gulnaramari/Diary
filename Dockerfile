FROM python:3.11

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости системы
COPY requirements.txt ./



# Устанавливаем зависимости Python

RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt

# Копируем исходный код приложения в контейнер
COPY . .

