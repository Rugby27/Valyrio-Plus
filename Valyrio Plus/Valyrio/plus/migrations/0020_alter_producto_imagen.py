# Generated by Django 5.0.3 on 2025-03-24 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plus', '0019_alter_compra_comprobante'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(null=True, upload_to='productos'),
        ),
    ]
