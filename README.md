Веб-приложение для ведения рабочего журнала "LABBOOK"
Особенности :
Веб-приложение реализовано на фреймворке Django
Авторизация пользователя
Регистрация пользователя
Управление своими записями текущим пользователем
Документация по API с Swagger
Развертывание на сервере
1. Требования
Для успешного развертывания вам понадобятся:

Удаленный сервер с установленным Docker.
Учетная запись Docker Hub.
Доступ к репозиторию на GitHub.
2. Настройка удаленного сервера
Обновление системы

sudo apt update
sudo apt upgrade
Установка docker and docker-compose

sudo apt update && sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo usermod -aG docker $USER && newgrp docker
Настройка брандмауэра

3.1. Активировать брандмауэр - check the firewall status - sudo ufw status Если брандмауэр отключен, включите его - sudo ufw enable

3.2. Откройте необходимые порты - http port: - sudo ufw allow 80/tcp

    - https port:
      - sudo ufw allow 443/tcp
 
    - ssh port:
      - sudo ufw allow 22/tcp
Клонирование репозитория: \

git clone https://github.com/gulnaramari/Diary.git /var/www/config
cd /var/www/config
Заполните значения. Вот пример:

Секретный ключ Django

SECRET_KEY=1234567890op

Подключение к базе

POSTGRES_DB=diary
POSTGRES_USER=postgres
POSTGRES_PASSWORD=SkyPro2025
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
Разрешенные хосты

ALLOWED_HOSTS=localhost,127.0.0.1,example.com
Запуск в production:
git clone https://github.com/gulnaramari/Diary.git /var/www/config \
cd /var/www/config

Важно:

Nginx будет доступен на порту 80
Автоматическая статическая и миграционная сборка
Celery workers/beat запустятся автоматически
Настройка CI/CD
1. Разветвите или клонируйте репозиторий
Разветвите этот репозиторий на свою собственную учетную запись GitHub, если вы планируете вносить свой вклад или запускать рабочие процессы, для которых требуются секретные ключи. В качестве альтернативы, клонируйте репозиторий непосредственно на свой локальный компьютер: git clone https://github.com/username/repository-name.git
cd repository-name

2. Установка данных в secrets:
а) Перейдите в свой разветвленный репозиторий на GitHub.
б) Перейдите в Settings > Secrets and variables > Actions.
в) Добавьте необходимые переменные в secrets, такие как:
DOTENV - содержимое файла .env
(заполните в соответствии с образцом .env.sample)
DOCKER_HUB_USERNAME - логин Docker Hub
DOCKER_ACCESS_TOKEN - токен Docker Hub
SSH_KEY - закрытый SSH-ключ сервера
SSH_USER - пользователь сервера
SERVER_IP - IP-адрес виртуальной машины
3. Workflow:
Автоматически запускается по запросу push/pull \
Шаги: ✅ lint→ ✅ build → 🚀 deploy\
Запустить локально
(для разработки)

Убедитесь, что вы заполнили данные в файле .env
Сборка и запуск:
docker-compose -f docker-compose.dev.yml up --build
Создать суперпользователя
docker-compose -f docker-compose.dev.yml exec web python manage.py csu\
Порты:
Django: http://localhost:8000
PostgreSQL: 5432
Redis: 6379

Аварийные Команды (Сервер)

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f

# Пересборка контейнеров
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate

# Остановка
docker-compose -f docker-compose.prod.yml down -v
