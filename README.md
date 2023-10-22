[![Main Foodgram workflow](https://github.com/AlexShemyakin/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/AlexShemyakin/foodgram-project-react/actions/workflows/main.yml)
# Foodgram - веб-сервис, позволяющий людям делиться своими кулинарными рецептами.

## Инструменты веб-сервиса позволяют:
- Публиковать рецепты, их редактировать и удалять;
- Подписываться на других авторов;
- Добавлять рецепты в избранное;
- Возможность скачивать список ингредиентов.


## Запуск проекта
### Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:AlexShemyakin/django-personal-portfolio.git
```

### Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/bin/activate
```

```
python -m pip install --upgrade pip
```

### Для локального запуска следует запустить docker-compose.yml:

```
sudo docker compose -f docker-compose.yml up -d
```

### Выполнить миграции и сбор статики:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

### Для запуска проекта на удаленном сервере следует скопировать docker-compose.production.yml и файл с переменным окруженим на сервер:

```
scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/dir_project/docker-compose.production.yml 
scp -i path_to_SSH/SSH_name .env username@server_ip:/home/username/dir_project/.env 
```

### Выполнить на сервере pull образов с Docker hub:

```
sudo docker compose -f docker-compose.production.yml pull
```

### Перезапустить на сервере все контейнеры в Docker Compose:

```
sudo docker compose -f docker-compose.production.yml down
sudo docker compose -f docker-compose.production.yml up -d
```

### Выполнить на сервере миграции и сбор статики:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

## Автор проекта
Шемякин Александр

## Стек технологий
Разработка:

[Django]
[Python]
[DRF]
[PostgreSQL]

Сервер:

[Nginx]
[Docker]
[Gunicorn]
