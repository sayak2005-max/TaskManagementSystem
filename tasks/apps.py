from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    # NOTE: We intentionally do not perform DB operations in ready().
    # Group and permission setup is provided as a management command
    # (see tasks/management/commands/create_groups.py) to avoid
    # accessing the database during app initialization which raises
    # runtime warnings and can interfere with migrations.
