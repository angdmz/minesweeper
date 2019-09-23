DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '172.17.0.1',
        'PORT': '5432',
        'USER': 'minesweeper',
        'PASSWORD': 'secret123',
        'NAME': 'minesweeper',
    }
}

SECRET_KEY = 'someKey'