
![](https://github.com/saturnsergei/foodgram-project-react/assets/124848565/09462f77-e3c9-4c99-aafc-ff6b7fe7fb8b)

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

```
ip: 158.160.75.183
domen: https://foodgramka.ddns.net/
email: gordon@yandex.ru
user: gordon
password: gordon
```

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
        proxy_pass http://127.0.0.1:8080;
    }

}
```

## Документация:

Документация для API с примерами запросов доступна по ссылке:

```
http://localhost/api/docs/
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
