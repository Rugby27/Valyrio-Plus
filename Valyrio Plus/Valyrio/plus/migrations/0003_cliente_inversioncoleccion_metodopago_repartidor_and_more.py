# Generated by Django 5.1.2 on 2024-11-09 07:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plus', '0002_producto'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50)),
                ('telefono', models.CharField(max_length=8)),
                ('cedula', models.CharField(max_length=25)),
                ('correo', models.EmailField(max_length=25)),
                ('contraseña', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='InversionColeccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_inversion', models.FloatField()),
                ('fecha_inversion', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='MetodoPago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_metodo_pago', models.CharField(choices=[('efectivo', 'Efectivo'), ('deposito', 'Depósito'), ('transferencia', 'Transferencia')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Repartidor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50)),
                ('telefono', models.CharField(max_length=8)),
                ('cedula', models.CharField(max_length=25)),
                ('matricula', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Trabajador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50)),
                ('telefono', models.CharField(max_length=8)),
                ('cedula', models.CharField(max_length=25)),
                ('fecha_nacimiento', models.DateField()),
            ],
        ),
        migrations.AlterField(
            model_name='producto',
            name='cantidad',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='producto',
            name='descripcion',
            field=models.CharField(default='Sin descripción', max_length=100),
        ),
        migrations.AlterField(
            model_name='producto',
            name='imagen',
            field=models.URLField(default='https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Imagen_no_disponible.svg/768px-Imagen_no_disponible.svg.png', verbose_name='Imagen del producto'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='nombre',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='producto',
            name='precio',
            field=models.FloatField(),
        ),
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comprobante', models.CharField(max_length=100)),
                ('total', models.FloatField()),
                ('fecha_compra', models.DateField()),
                ('tipo_compra', models.BooleanField()),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.cliente')),
                ('metodo_pago', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.metodopago')),
                ('trabajador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.trabajador')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.compra')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.producto')),
            ],
        ),
        migrations.CreateModel(
            name='Devolucion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=100)),
                ('imagen', models.URLField(default='https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Imagen_no_disponible.svg/768px-Imagen_no_disponible.svg.png', verbose_name='Imagen de la devolución')),
                ('fecha_devolucion', models.DateField()),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.cliente')),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.compra')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleInversion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.producto')),
                ('inversion_coleccion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.inversioncoleccion')),
            ],
        ),
        migrations.CreateModel(
            name='Regalias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('monto_total', models.FloatField()),
                ('fecha_regalia', models.DateField()),
                ('beneficiado', models.CharField(max_length=50)),
                ('justificacion', models.CharField(max_length=50)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.producto')),
            ],
        ),
        migrations.CreateModel(
            name='Envio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.CharField(max_length=150)),
                ('peso', models.FloatField()),
                ('telefono', models.CharField(max_length=8)),
                ('tarifa_envio', models.FloatField()),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.compra')),
                ('repartidor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plus.repartidor')),
            ],
        ),
    ]
