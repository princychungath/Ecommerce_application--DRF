# Generated by Django 4.2.2 on 2023-08-18 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_api', '0002_alter_order_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='total',
        ),
    ]
