# Generated by Django 5.1.2 on 2024-11-25 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plus', '0013_compra_cancelada'),
    ]

    operations = [
        migrations.AddField(
            model_name='inversioncoleccion',
            name='confirmada',
            field=models.BooleanField(default=0),
        ),
    ]
