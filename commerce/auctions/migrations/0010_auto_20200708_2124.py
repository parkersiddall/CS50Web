# Generated by Django 3.0.1 on 2020-07-08 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20200708_2037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='starting_bid',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
    ]