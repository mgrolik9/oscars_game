# Generated by Django 3.0.2 on 2020-07-18 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nominations', '0006_auto_20200718_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='default_avatar.JPG', upload_to=''),
        ),
    ]