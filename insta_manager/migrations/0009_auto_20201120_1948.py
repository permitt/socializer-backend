# Generated by Django 3.0.4 on 2020-11-20 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insta_manager', '0008_userinstagram_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinstagram',
            name='picture',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
