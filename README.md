# foodgram    <img src="https://github.com/basicshade/foodgram-project-react/actions/workflows/foodgram_backend_workflow.yml/badge.svg" />

### Описание:
Учебный проект по созданию REST API на Django REST Framework. Сервис предназначен для хранения и просмотра кулинарных рецептов, разделенных на группы с помощью тегов. Предусмотрен механизм фильтрации по избранным рецептам и механизм подписок на других пользователей. Фронтэнд написан на React. Админ панель настроена для удобства работы со всеми моделями базы данных. В пользовательскую модель включена дополнительная роль администратора. Аутентификация на основе DRF authtoken. Эндпоинты для создания пользователя и аутентификации частично обслуживаются djoser. В приложении реализована логика создания списка покупок по рецептам, добавленным в корзину. Список покупок формуруется в pdf с помощью библиотеки reportlab и отправляется пользователю по запросу.

* Главная страница: http://basicshade.ddns.net/
* Админка: http://basicshade.ddns.net/admin/
* API: http://basicshade.ddns.net/api/
* Документация API: http://basicshade.ddns.net/api/docs/

### Используемые технологии
<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" /> <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green" /> <img src="https://img.shields.io/badge/django%20rest-ff1709?style=for-the-badge&logo=django&logoColor=white" /> <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" />

   ```
   Python 3.7
   Django 3.2.3
   Django REST framework 3.12.4
   Djoser 2.1.0
   Reportlab 3.6.12
   Docker 4.6.1
   ```

### Запуск проекта ⚙️
1. В терминале клонировать репозиторий и перейти в папку infra:
    ```
    git clone git@github.com:basicShade/foodgram-project-react.git
    cd infra/
    ```
2. В папке infra создать .env файл по шаблону 🔒
    ```
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=...
    POSTGRES_USER=...
    POSTGRES_PASSWORD=...
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY=...
    ```

3. Запустить docker-compose:
    ```
    docker-compose -p foodgram up --build -d
    ```

4. Выполнить миграции, загрузить статику и данные, создать суперпользователя:
    ```
    docker-compose -p foodgram exec backend python manage.py migrate
    docker-compose -p foodgram exec backend python manage.py loaddata ./fixtures/test_data_dump_20230109.json
    docker-compose -p foodgram exec backend python manage.py collectstatic --no-input
    docker-compose -p foodgram exec backend python manage.py createsuperuser

    Optional:
    docker cp ../data/images/ <container_name>:/app/backend_media/recipes/
    ```

   Страницы, доступные после запуска:
    ```
    Главная страница: http://localhost/
    Админка: http://localhost/admin/
    API: http://localhost/api/
    Документация API: http://localhost/api/docs/
    ```

### Планы по доработке:
    ```
    добавить https
    скрыть api
    доработать интерфейс (выпадающие списки, чекбоксы)
    добавить ссылки на похожие рецепты в youtube
    восстановление пароля по email
    ```
