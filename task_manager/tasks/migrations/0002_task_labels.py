# Generated by Django 3.1.5 on 2021-01-29 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labels', '0001_initial'),
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='labels',
            field=models.ManyToManyField(to='labels.Label'),
        ),
    ]