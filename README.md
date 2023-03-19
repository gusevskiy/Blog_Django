Блог на Django
Функциональность

    Регистрация и авторизация пользователей
    Просмотр профайлов пользователей
    Создание записей и комментариев к ним
    Добавление изображений к записям
    Оформление подписки на избранных авторов
    Просмотр записей и комментариев всех авторов, избранных авторов или групп
    Кастомные страницы 404 и 500
    Все функции покрыты тестами

Если вы хотите запустить проект локально

    Создайте директорию, например blog
    Склонируйте репозитарий в директорию blog

    git clone git@github.com:gusevskiy/hw05_final.git

    создайте виртуальное окружение

    python -m venv venv

    запустите виртуальное окружение

    для windows: source venv/script/activate

    установите требуемые приложения:

    pip install -r requirements.txt

    примените миграции Django:

    python manage.py migrate

    запустите сервер Django:

    python manage.py runserver
