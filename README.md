# praktikum_new_diplom

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
    docker-compose up --build -d
    ```

4. Выполнить миграции, загрузить статику и данные, создать суперпользователя:
    ```
    docker-compose -p exec web python manage.py migrate
    docker-compose -p exec web python manage.py loaddata ./fixtures/test_data_dump_20230109.json
    docker-compose -p exec web python manage.py collectstatic --no-input
    docker-compose -p exec web python manage.py createsuperuser
    ```

После запуска сервера начните со следующих страниц:
http://localhost/signin/
http://localhost/recipes/
http://localhost/admin/
http://localhost/api/docs/
