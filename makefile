
migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

run:
	python manage.py runserver 0.0.0.0:8000

superuser:
	export DJANGO_SUPERUSER_USERNAME="admin" &&        \
	export DJANGO_SUPERUSER_PASSWORD="admin" &&        \
 	export DJANGO_SUPERUSER_EMAIL="admin@admin.com" && \
 	python manage.py createsuperuser --noinput
