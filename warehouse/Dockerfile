# FROM python:3.10

# WORKDIR /warehouse

# COPY . .

# RUN pip install -r requirements.txt

# RUN python manage.py makemigrations

# RUN python manage.py migrate

# CMD [ "python", "manage.py", "runserver" ]

FROM python:3.10

WORKDIR /warehouse

# Скопируйте все файлы, включая wait-for-it.sh
COPY . .

# Скопируйте wait-for-it.sh и сделайте его исполняемым
RUN chmod +x server/wait-for-it.sh

# Установите зависимости
RUN pip install -r requirements.txt

# Используйте wait-for-it.sh для ожидания базы данных и выполнения миграций
CMD ["./server/wait-for-it.sh", "database:5432", "--", "sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]


