
█▀▀ █▀█ █▀█ █▀▄ █▀▀ █▀█ ▄▀█ █▀▄▀█
█▀░ █▄█ █▄█ █▄▀ █▄█ █▀▄ █▀█ █░▀░█

### Описание
Дипломный проект «Foodgram» - сервис для публикации и обмена рецептами, формирования списка покупок.

Возможности:
- Регистрация новых пользователей, изменение/обновление пароля
- Возможность подписываться на других пользователей
- Добавление/обновление/удаление рецептов
- Добавление изображений рецептов
- Возможность импортировать ингредиенты из файла
- Фильтрация рецептов по тегам
- Добавление рецептов в список покупок
- Возможность скачать список ингредиентов для рецепта, который находится в списке покупок
- Добавление рецепта в избранное

### Запуск

Клонировать репозиторий

```
git@github.com:saturnsergei/foodgram-project-react.git

cd foodgram-project-react
```
Установить docker
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh 
sudo sh ./get-docker.sh
```
Установить Docker Compose
```
sudo apt-get install docker-compose-plugin 
```
Запуск
```
docker compose up --build
```

Выполнить миграции:

```
docker compose exec backend python manage.py migrate
```

Собрать статику:

```
docker compose exec backend python manage.py collectstatic
```

### Nginx (пример)
```
server {
    server_name xxx.xxx.xx.xxx;

    location / {
        proxy_pass http://127.0.0.1:9000;
    }

}
```

## Документация:

Документация для API с примерами запросов доступна по ссылке:

```
http://127.0.0.1:8000/redoc/
```


## Загрузка ингредиентов из файла:

В директории `/backend/static/data` расположен файл для загрузки `ingredients.csv`

Необходимый порядок столбцов в csv файлах:
`name | measurement_unit `

```
python manage.py upload_ingredients <filename>
```

### Технологии
- Docker
- Docker compose
- Django
- Nginx
- Gunicorn
- PostgreSQL
- React

### Автор
[saturnsergei](https://github.com/saturnsergei)
