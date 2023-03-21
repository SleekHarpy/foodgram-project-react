# Foodgram
Cервис для публикаций и обмена рецептами.

Авторизованные пользователи могут подписываться на понравившихся авторов, добавлять рецепты в избранное, в покупки, скачивать список покупок. Неавторизованным пользователям доступна регистрация, авторизация, просмотр рецептов других пользователей.


## Стек технологий
Python 3.9.7, Django 3.2.7, Django REST Framework 3.12, PostgresQL, Docker.

## Установка
Для запуска локально, создайте файл `.env` в директории `/infra/` с содержанием:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=пароль_к_базе_данных_на_ваш_выбор
DB_HOST=bd
DB_PORT=5432
SECRET_KEY=любой_секретный_ключ_на_ваш_выбор
```

### Настройка проекта
1. Запустите docker compose:
```bash
docker-compose up -d
```
2. Примените миграции:
```bash
docker-compose exec backend python manage.py migrate
```
3Создайте администратора:
```bash
docker-compose exec backend python manage.py createsuperuser
```
4Соберите статику:
```bash
docker-compose exec backend python manage.py collectstatic
```

### Автор
- [Влад Шевцов](https://github.com/SleekHarpy)