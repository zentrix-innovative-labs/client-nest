#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# The sys.path modification above ensures the script can locate the necessary modules. PYTHONPATH configuration is not required here.
# Note: Modifying sys.path in manage.py is nonstandard. Prefer adding the project root to PYTHONPATH externally for best practice.


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
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
