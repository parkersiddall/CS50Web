# Generated by Django 3.0.1 on 2020-07-09 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_auto_20200708_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='creator',
            field=models.CharField(default='user', max_length=50),
        ),
    ]
