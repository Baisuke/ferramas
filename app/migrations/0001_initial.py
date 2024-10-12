# Generated by Django 5.0.6 on 2024-10-12 18:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_producto', models.CharField(max_length=50)),
                ('marca', models.CharField(max_length=50)),
                ('nombre', models.CharField(max_length=50)),
                ('precio', models.IntegerField()),
                ('fecha', models.DateField()),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.categoria')),
            ],
        ),
    ]