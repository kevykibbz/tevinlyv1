# Generated by Django 3.2.9 on 2022-09-21 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_alter_designmodel_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='designmodel',
            name='progress',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]