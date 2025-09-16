#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Intenta usar 'settings_local' por defecto.
    # En Render, la variable DJANGO_SETTINGS_MODULE se establecerá a 'settings_production'.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings_local')
    
    print(f"--- Usando settings: {os.environ.get('DJANGO_SETTINGS_MODULE')} ---")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
