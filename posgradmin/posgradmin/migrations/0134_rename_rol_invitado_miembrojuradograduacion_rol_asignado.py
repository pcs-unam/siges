# Generated by Django 3.2.15 on 2023-05-02 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posgradmin', '0133_alter_convocatoriacurso_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='miembrojuradograduacion',
            old_name='rol_invitado',
            new_name='rol_asignado',
        ),
    ]