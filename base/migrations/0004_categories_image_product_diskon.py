# Generated by Django 4.2.1 on 2023-06-03 07:00

import base.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='categories',
            name='image',
            field=models.ImageField(null=True, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='product',
            name='diskon',
            field=models.IntegerField(null=True, validators=[base.models.maxValueDiskon]),
        ),
    ]