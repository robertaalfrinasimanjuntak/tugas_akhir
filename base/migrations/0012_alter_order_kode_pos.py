# Generated by Django 4.2.1 on 2023-06-07 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_remove_payment_user_remove_order_alamat_pengiriman_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='kode_pos',
            field=models.IntegerField(max_length=20, null=True),
        ),
    ]