# Generated by Django 4.2.5 on 2023-09-25 07:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('daangn_app', '0004_post_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='product_image',
        ),
        migrations.CreateModel(
            name='PostImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='image_upload_path')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image', to='daangn_app.post')),
            ],
            options={
                'db_table': 'post_image',
            },
        ),
    ]
