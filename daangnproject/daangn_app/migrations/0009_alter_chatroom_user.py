# Generated by Django 4.2.5 on 2023-09-26 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daangn_app', '0008_chatroom_user_post_like_userinfo_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatroom',
            name='user',
            field=models.ManyToManyField(to='daangn_app.userinfo'),
        ),
    ]
