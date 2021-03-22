# Generated by Django 3.0.4 on 2021-03-18 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insta_manager', '0009_auto_20201120_1948'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='post',
            name='unique post',
        ),
        migrations.AddConstraint(
            model_name='post',
            constraint=models.UniqueConstraint(fields=('owner', 'url'), name='unique post'),
        ),
    ]
