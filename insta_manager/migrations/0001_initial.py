# Generated by Django 3.0.4 on 2020-03-23 22:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Follower',
            fields=[
                ('username', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('firstName', models.CharField(max_length=30)),
                ('lastName', models.CharField(max_length=30)),
                ('picture', models.CharField(max_length=100)),
                ('activeStory', models.BooleanField()),
                ('activePosts', models.BooleanField()),
                ('lastPost', models.DateTimeField()),
                ('lastStory', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='UserInstagram',
            fields=[
                ('username', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=50)),
                ('cookies', models.TextField()),
                ('lastActive', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploadedAt', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField()),
                ('image', models.ImageField(upload_to='images')),
                ('type', models.CharField(choices=[('STORY', 'Story'), ('POST', 'Post')], default='POST', max_length=10)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='insta_manager.Follower')),
            ],
        ),
        migrations.AddField(
            model_name='follower',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='insta_manager.UserInstagram'),
        ),
    ]