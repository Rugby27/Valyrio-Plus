# Generated by Django 5.1.2 on 2024-11-27 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plus', '0018_remove_devolucion_compra_devolucion_detalle_compra'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compra',
            name='comprobante',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
