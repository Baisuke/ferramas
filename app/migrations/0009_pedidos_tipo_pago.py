# Generated by Django 5.0.6 on 2024-10-20 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_remove_pedidos_tipo_pago'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedidos',
            name='tipo_pago',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
