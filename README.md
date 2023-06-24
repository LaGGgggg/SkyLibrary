![GitHub](https://img.shields.io/github/license/LaGGgggg/SkyLibrary?label=License)
![GitHub watchers](https://img.shields.io/github/watchers/LaGGgggg/SkyLibrary)
![GitHub last commit](https://img.shields.io/github/last-commit/LaGGgggg/SkyLibrary)
[![wakatime](https://wakatime.com/badge/user/824414bb-4135-4fbc-abbd-0d007987e855/project/c5bb279e-2962-4a25-b98b-9b09e581de4c.svg)](https://wakatime.com/badge/user/824414bb-4135-4fbc-abbd-0d007987e855/project/c5bb279e-2962-4a25-b98b-9b09e581de4c)

# Sky library

Web library on django.
You can upload and download media files (videos, books, webinars...), rate them and much more!

### Project includes:
- [x] Support for Docker compose deployment.
  - [x] Automatic creation of SSL certificates.
  - [x] Automatic renewal of SSL certificates.
  - [x] Automatic rejection of unknown domains (using nginx).
  - [x] Static and media files support.
  - [x] Automatic launch of django inside entrypoint. Executed commands:
    - collectstatic
    - migrate
    - createcachetable
    - clear_cache (custom command, removing all cache)
    - compilemessages
    - test
    - sendtestemail
    - gunicorn
- [x] Full translation into 2 languages.
- [x] Autotest system (by github actions).
- [x] Big amount of tests (113+).
- [x] Caching using redis.
- [x] Registration with confirmation by email.
- [x] User roles system (4 roles with different permissions).
- [x] Moderation system.
- [x] Configured administration system.
- [x] Configured logs system.
- [x] Django [email reports](https://docs.djangoproject.com/en/4.2/howto/error-reporting/#email-reports) support.
- [x] Error codes system.
- [x] Star rating.
- [x] [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/).

# How to start the project?

### 1. Clone this repository

```bash
git clone https://github.com/LaGGgggg/SkyLibrary.git
cd SkyLibrary
```

### 2. Create the virtualenv:

#### With [pipenv](https://pipenv.pypa.io/en/latest/):

```bash
pip install --user pipenv
pipenv shell  # create and activate
```

#### Or classic:

```bash
python -m venv .venv  # create
.venv\Scripts\activate.bat  # activate
```

### 3. Install python packages

#### With [pip](https://pypi.org/project/pip/):

```bash
pip install -r requirements.txt
```

### 4. Change directory

```bash
cd SkyLibrary
```

### 5. Create postgresql database

To create your postgresql database you need:
1. Install [this](https://www.postgresql.org/download/)
2. Open pgadmin
3. Create a new one or use the default database

### 6. Add environment variables

Create file `.env` in `SkyLibrary/app_main`, such it `SkyLibrary/app_main/.env`. Next, paste it in `.env`
(this is a configuration for development, not for production!):

```dotenv
SECRET_KEY=<your secret key>
DEBUG=True
DB_URL=postgres://<username>:<password>@localhost:5432/<database_name>
ALLOWED_HOSTS=*  # In case of 2 or more, divide with ", "
INTERNAL_IPS=127.0.0.1  # In case of 2 or more, divide with ", "
CSRF_TRUSTED_ORIGINS=http://*  # In case of 2 or more, divide with ", "
ADMINS=Name:email@email.com  # In case of 2 or more, divide with ", "

USE_CACHE=False
CACHE_LOCAL=True
CACHE_LOCATION_DB_TABLE_NAME=cache
CACHE_REDIS_LOCATIONS=

EMAIL_HOST_USER=<your email adress>
EMAIL_HOST_PASSWORD=<your email password>

LANGUAGE_CODE=en-us
```
_**Do not forget to set the DB_URL variable!**_

#### More about variables:
SECRET_KEY - standard [django secret key](https://docs.djangoproject.com/en/4.1/topics/signing/).<br>
DEBUG - standard [django debug](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-DEBUG).<br>
DB_URL - argument for [dj_database_url.config(default=)](https://github.com/jazzband/dj-database-url).<br>
ALLOWED_HOSTS - standard [django allowed hosts](https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts).<br>
INTERNAL_IPS - standard [django internal ips](https://docs.djangoproject.com/en/4.1/ref/settings/#internal-ips).<br>
CSRF_TRUSTED_ORIGINS - standard [django csrf trusted origins](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins).<br>
ADMINS - standard [django admins](https://docs.djangoproject.com/en/4.2/ref/settings/#admins).<br>

USE_CACHE - if False, set [django DummyCache](https://docs.djangoproject.com/en/4.1/topics/cache/#dummy-caching-for-development) = no caching.<br>
CACHE_LOCAL - if True, set [django DatabaseCache](https://docs.djangoproject.com/en/4.1/topics/cache/#database-caching), else [django RedisCache](https://docs.djangoproject.com/en/4.1/topics/cache/#redis).<br>
CACHE_LOCATION_DB_TABLE_NAME - standard [django DatabaseCache location](https://docs.djangoproject.com/en/4.1/topics/cache/#database-caching).<br>
CACHE_REDIS_LOCATIONS - standard [django RedisCache location](https://docs.djangoproject.com/en/4.1/topics/cache/#redis),
can be empty if you are not using Redis caching, can take more than one location, separated  by " ,"
(for example: "first_location, second_location, third_location").<br>

**Warning!** The project uses **yandex smtp** as [email host variable](https://docs.djangoproject.com/en/4.1/ref/settings/#email-host).<br>
EMAIL_HOST_USER - standard [django email host user](https://docs.djangoproject.com/en/4.1/ref/settings/#email-host-user).<br>
EMAIL_HOST_PASSWORD - standard [django email host password](https://docs.djangoproject.com/en/4.1/ref/settings/#email-host-password).<br>

LANGUAGE_CODE - standard [django language code](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-LANGUAGE_CODE).<br>

### 7. Run database migrations

```bash
python manage.py migrate
```

### 8. Run createcachetable

```bash
python manage.py createcachetable
```

### 9. Run collectstatic _(not required for development server)_ 

```bash
python manage.py collectstatic
```

### 10. Run development server

```bash
python manage.py runserver
```

# Server set-up

### 1. Install [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### 2. Install [docker](https://docs.docker.com/engine/install/)

### 3. Install [docker compose plugin](https://docs.docker.com/compose/install/linux/)

### 4. Clone this repository

```bash
git clone https://github.com/LaGGgggg/SkyLibrary.git
cd SkyLibrary
```

### 5. Add environment variables

Create file `.env` in `SkyLibrary/app_main`, such it `SkyLibrary/app_main/.env`. Next, paste it in `.env`
(this is a configuration for development, not for production!):

```dotenv
# django section
SECRET_KEY=<your secret key>
DEBUG=True
DB_URL=postgres://<username>:<password>@postgres:5432/<database_name>
ALLOWED_HOSTS=*  # In case of 2 or more, divide with ", "
INTERNAL_IPS=127.0.0.1  # In case of 2 or more, divide with ", "
CSRF_TRUSTED_ORIGINS=<your csrf trusted origins>  # In case of 2 or more, divide with ", "
ADMINS=Name:email@email.com  # In case of 2 or more, divide with ", "

USE_CACHE=False
CACHE_LOCAL=True
CACHE_LOCATION_DB_TABLE_NAME=cache
CACHE_REDIS_LOCATIONS=

EMAIL_HOST_USER=<your email adress>
EMAIL_HOST_PASSWORD=<your email password>

LANGUAGE_CODE=en-us

# docker-compose section
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<database_name>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data/pgdata
```
_**Do not forget to set the DB_URL variable!
(For use with docker-compose host must be the name of the service!)**_

#### More about variables:
SECRET_KEY - standard [django secret key](https://docs.djangoproject.com/en/4.1/topics/signing/).<br>
DEBUG - standard [django debug](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-DEBUG).<br>
DB_URL - argument for [dj_database_url.config(default=)](https://github.com/jazzband/dj-database-url).<br>
ALLOWED_HOSTS - standard [django allowed hosts](https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts).<br>
INTERNAL_IPS - standard [django internal ips](https://docs.djangoproject.com/en/4.1/ref/settings/#internal-ips).<br>
CSRF_TRUSTED_ORIGINS - standard [django csrf trusted origins](https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins).<br>
ADMINS - standard [django admins](https://docs.djangoproject.com/en/4.2/ref/settings/#admins).<br>

USE_CACHE - if False, set [django DummyCache](https://docs.djangoproject.com/en/4.1/topics/cache/#dummy-caching-for-development) = no caching.<br>
CACHE_LOCAL - if True, set [django DatabaseCache](https://docs.djangoproject.com/en/4.1/topics/cache/#database-caching), else [django RedisCache](https://docs.djangoproject.com/en/4.1/topics/cache/#redis).<br>
CACHE_LOCATION_DB_TABLE_NAME - standard [django DatabaseCache location](https://docs.djangoproject.com/en/4.1/topics/cache/#database-caching).<br>
CACHE_REDIS_LOCATIONS - standard [django RedisCache location](https://docs.djangoproject.com/en/4.1/topics/cache/#redis),
can be empty if you are not using Redis caching, can take more than one location, separated  by " ,"
(for example: "first_location, second_location, third_location").<br>

**Warning!** The project uses **yandex smtp** as [email host variable](https://docs.djangoproject.com/en/4.1/ref/settings/#email-host).<br>
EMAIL_HOST_USER - standard [django email host user](https://docs.djangoproject.com/en/4.1/ref/settings/#email-host-user).<br>
EMAIL_HOST_PASSWORD - standard [django email host password](https://docs.djangoproject.com/en/4.1/ref/settings/#email-host-password).<br>

LANGUAGE_CODE - standard [django language code](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-LANGUAGE_CODE).<br>

POSTGRES_USER - standard [POSTGRES_USER](https://hub.docker.com/_/postgres) environment variable.<br>
POSTGRES_PASSWORD - standard [POSTGRES_PASSWORD](https://hub.docker.com/_/postgres) environment variable.<br>
POSTGRES_DB - standard [POSTGRES_DB](https://hub.docker.com/_/postgres) environment variable.<br>
POSTGRES_HOST - standard [POSTGRES_HOST](https://hub.docker.com/_/postgres) environment variable.<br>
POSTGRES_PORT - standard [POSTGRES_PORT](https://hub.docker.com/_/postgres) environment variable.<br>
PGDATA - standard [PGDATA](https://hub.docker.com/_/postgres) environment variable.<br>

### 6. Configure nginx.conf

Configure it (_nginx/nginx.conf_):
```nginx configuration
ssl_certificate /etc/letsencrypt/live/<domain.site>/fullchain.pem;  # 11 line
ssl_certificate_key /etc/letsencrypt/live/<domain.site>/privkey.pem;  # 12 line
server_name www.<domain.site> <domain.site>;  # 23 line
server_name www.<domain.site> <domain.site>;  # 39 line
ssl_certificate /etc/letsencrypt/live/<domain.site>/fullchain.pem;  # 44 line
ssl_certificate_key /etc/letsencrypt/live/<domain.site>/privkey.pem;  # 45 line
```

### 7. Configure docker-compose-init.sh

Configure it (_3-5 lines in docker-compose-init.sh file_):
```bash
domains=()  # example: (domain.site www.domain.site)
email=""  # example: "example@yandex.ru"
staging=0  # 1 - staging on, 0 - off
```

### 8. Run docker-compose-init.sh

```bash
chmod +x docker-compose-init.sh
sudo ./docker-compose-init.sh
```

### 9. Check the server

```bash
docker compose logs -f
```

# User roles system

- visitor (default user role, site visitor)
- moderator (has access to the moderator page)
  - tasks
    - Moderate new inactive media (on the "moderator" page)
- administrator (has access to the administration panel (not all permissions))
  - tasks
    - Report processing (ban comment or media if necessary)
    - Managing moderator accounts (create, edit, block)
    - Managing media tags (create, edit, delete)
    - Managing report types (create, edit, delete)
  - permissions (set manual by a superuser)
    - accounts_app | user | Can add a new moderator
    - accounts_app | user | Can add user
    - accounts_app | user | Can change a moderator data
    - accounts_app | user | Can change user
    - accounts_app | user | Can change the user active field
    - media_app | comment | Can change comment
    - media_app | comment | Can change the content of the comment to "This comment was banned"
    - media_app | media | Can change media
    - media_app | media | Can change the value of the media active field
    - media_app | media tag | Can add media tags
    - media_app | media tag | Can change media tags
    - media_app | media tag | Can delete media tags
    - media_app | media tag | Can view media tags
    - media_app | report | Can delete report
    - media_app | report | Can view report
    - media_app | report type | Can add report type
    - media_app | report type | Can change report type
    - media_app | report type | Can delete report type
    - media_app | report type | Can view report type
    - staff_app | moderator task | Can delete moderator task
    - staff_app | moderator task | Can view moderator task
- superuser (django vanilla superuser)

# Project structure

- Home page
  - Navigation bar
    - User is authenticated
      - Link to the "profile" page
      - Link to the "add new media" page
      - User is moderator
        - Link to the "moderator" page
    - User is not authenticated
      - Link to the "login" page
      - Link to the "registration" page
  - "Search media" button (you can search for media by tags and/or title text. Returns links to media with star ratings and tags)
  - "Best media" compilation (by media rating. Links to media with star ratings)
  - "Recent media" compilation (by publication date. Links to media with star ratings)
- Login page
  - Navigation bar
    - Link to the "home" page
  - Login form (with support for field errors)
    - username field
    - password field
  - Link to the "password reset" page
- Password reset page
  - Navigation bar
    - Link to the "home" page
  - Password reset form (with support for field errors)
    - email field
- Register page
  - Navigation bar
    - Link to the "home" page
  - Registration form (with support for field errors. Registration created partially with [django-registration](https://django-registration.readthedocs.io/en/latest/))
    - username field
    - email field
    - password field
    - confirm password field
- View media page
  - Navigation bar
    - Link to the "home" page
    - User is authenticated
      - Link to the "profile" page
      - Link to the "add new media" page
      - User is moderator
        - Link to the "moderator" page
  - Media title
  - Media star rating
  - Media tags
  - Media description
  - Media cover (if exists)
  - Download media file button (with a download counter. The user must be authenticated)
  - Report media button (receives report media form (with support for field errors), after confirming create media report. The user must be authenticated)
  - Media author
  - Media user who added username
  - Media publication date
  - Create media comment form (with support for field errors. The user must be authenticated)
  - Media comments
    - Comment data
      - user who added username
      - publication date
      - comment content
      - comment rating
      - comment upvote and downvote buttons (the user must be authenticated)
      - reply button (receives create comment reply form (with support for field errors), after confirming create comment reply. The user must be authenticated)
      - report button (receives report comment form (with support for field errors), after confirming create comment report. The user must be authenticated)
      - pin button (adds a link to the comment (by url fragment))
  - The user is the moderator and the media is the moderator's task (in this case, the user cannot add comments, reports and comment ratings)
    - Validate media form
      - Approve/disapprove radio buttons
      - Auto new task/no auto new task radio buttons (if the value is set to "auto new task", a new moderator task is automatically created after media validation)
- Profile page
  - Navigation bar
    - Link to the "home" page
    - Link to the "add new media" page
    - Link to the "change password" page
    - Link to the "logout" page
    - User is moderator
      - Link to the "moderator" page
  - My medias (a list of media added by the user, with media statuses, star ratings, tags and links to the "change media" pages (for each active media))
  - My downloads (a list of media downloaded by the user, with media tags and star ratings (user ratings, not average across all user ratings, the user can add a new rating to the media by clicking on the star))
- Change password page
  - Navigation bar
    - Link to the "home" page
    - Link to the "profile" page
  - Change password form (with support for field errors)
    - old password field
    - new password field
    - confirm new password field
- Add new media page
  - Navigation bar
    - Link to the "home" page
    - Link to the "profile" page
  - Add new media form (with support for field errors)
    - title field
    - description field
    - author field
    - tags field (checkboxes)
    - file field
    - cover field (optional)
- Change media page
  - Navigation bar
    - Link to the "home" page
    - Link to the "profile" page
  - Change media form (with support for field errors)
    - title field
    - description field
    - author field
    - tags field (checkboxes)
    - file field
    - cover field (optional)
- Logout page
- Error pages
  - 400 (with the link to the "home" page)
  - 403 (with the link to the "home" page)
  - 404 (with the link to the "home" page)
  - 500 (with the link to the "home" page)
- Moderator page
  - Navigation bar
    - Link to the "home" page
    - Link to the "profile" page
  - Get task button or link to the moderator task

# Contacts

For any questions:<br>
TulNik0@yandex.ru

# [License](LICENSE)
