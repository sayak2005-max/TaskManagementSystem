Developer notes

1. Run migrations and create groups

   python manage.py migrate
   python manage.py create_groups

2. Create superuser (if needed)

   python manage.py createsuperuser

3. Run tests

   python manage.py test

4. Start dev server

   python manage.py runserver

Notes
- Group creation is provided as a data migration `tasks/migrations/0001_create_groups.py` and also available as the management command `python manage.py create_groups` for manual use.
- Teachers are not granted global delete permissions; only task creators or admin users may delete tasks.
- If you change permissions, re-run `python manage.py create_groups` to sync groups.
