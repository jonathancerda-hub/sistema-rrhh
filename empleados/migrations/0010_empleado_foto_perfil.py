# Generated manually to add foto_perfil field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empleados', '0009_empleado_jerarquia'),
    ]

    operations = [
        migrations.AddField(
            model_name='empleado',
            name='foto_perfil',
            field=models.FileField(blank=True, help_text='Foto de perfil del empleado', null=True, upload_to='fotos_perfil/'),
        ),
    ]
