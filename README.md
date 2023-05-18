![GitHub](https://img.shields.io/github/license/LaGGgggg/SkyLibrary?label=License)
![GitHub watchers](https://img.shields.io/github/watchers/LaGGgggg/SkyLibrary)
![GitHub last commit](https://img.shields.io/github/last-commit/LaGGgggg/SkyLibrary)
[![wakatime](https://wakatime.com/badge/user/824414bb-4135-4fbc-abbd-0d007987e855/project/c5bb279e-2962-4a25-b98b-9b09e581de4c.svg)](https://wakatime.com/badge/user/824414bb-4135-4fbc-abbd-0d007987e855/project/c5bb279e-2962-4a25-b98b-9b09e581de4c)

# Sky library

Web library on django.
You can upload and download media files (videos, books, webinars...), add to bookmarks, rate and more!

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
.venv\Scripts\activate.bat   # activate
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

Configure it (_9, 25 and 28 lines in nginx/nginx.conf_):
```nginx configuration
server_name www.<domain.site> <domain.site>;
server_name www.<domain.site> <domain.site>;
if ($host != "www.<domain.site>" or $host != "<domain.site>") {
    return 403;
}
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

# Current project structure _(in progress)_

- Home page
  - Navigation bar
    - User is authenticated
      - "Profile" link
      - "Add new media" link
    - User is not authenticated
      - "Login" link
      - "Sign-up" link
  - Best media
    - Media title (link to the media page)
    - Media stars rating
  - Recent media
    - Media title (link to the media page)
    - Media stars rating
- Profile page
  - Navigation bar
    - "Home page" link
    - "Add new media" link
    - "Change password" link
    - "Logout" link
- Add new media page
  - Navigation bar
    - "Profile" link
    - "Home page" link
  - Add new media form
    - Fields
      - Title
      - Description
      - Author
      - Tags (checkboxes)
      - File (file input)
      - Cover (optional)
- View media page
  - Navigation bar
    - "Home page" link
    - "Profile" link
    - "Add new media" link
  - Media content
    - Title
    - Cover (if exists)
    - Rating
    - Description
    - Download button (become green if download)
    - Author
    - Added by
    - Publication date

# Contacts

For any questions:<br>
TulNik0@yandex.ru

# [License](LICENSE)
