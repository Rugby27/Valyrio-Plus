# Generated by Django 5.1.2 on 2024-11-24 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plus', '0012_alter_compra_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='compra',
            name='Cancelada',
            field=models.BooleanField(default=0),
        ),
    ]
