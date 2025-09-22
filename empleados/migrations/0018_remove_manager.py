# Generated migration to remove the manager field now that explicit hierarchy fields exist
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('empleados', '0017_empleado_director_empleado_gerente_empleado_jefe_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='empleado',
            name='manager',
        ),
    ]
