# Generated by Django 3.2.9 on 2022-09-21 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_reviewmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewmodel',
            name='name',
            field=models.CharField(blank=True, default=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='reviewmodel',
            name='profile_pic',
            field=models.CharField(blank=True, default=False, max_length=100, null=True),
        ),
    ]
