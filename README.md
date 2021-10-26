# Социальная сеть Yatube
Python 3.9, Django 3.0.5
### Описание
Данная социальная сеть предоставляет возможность авторам вести свой блог, комментировать посты других авторов, подписываться на обновления других авторов.
### Как развернуть
Форкните этот репозиторий, склонируйте к себе на машину. В коммандной строке, находясь в корневой директории проекта, выполните следующие комманды:
```
. venv/Scripts/activate
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```
После выполнения этих комманд проект будет доступен по адресу localhost:8000
