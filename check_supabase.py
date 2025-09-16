import os
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings_local')

try:
    import django
    django.setup()
    from django.conf import settings
    from django.db import connection

    db = settings.DATABASES.get('default', {})
    engine = db.get('ENGINE')
    host = db.get('HOST')
    name = db.get('NAME')

    print('Database engine:', engine)
    print('Database host:', host)
    print('Database name:', name)

    try:
        with connection.cursor() as c:
            c.execute('SELECT 1;')
            r = c.fetchone()
            print('SELECT 1 ->', r)
    except Exception as e:
        print('ERROR executing query:')
        traceback.print_exc()

except Exception as e:
    print('ERROR setting up Django:')
    traceback.print_exc()
