# Generated by Django 4.2.3 on 2023-08-07 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_auction_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='auctions',
            field=models.ManyToManyField(blank=True, related_name='watchlist', to='auctions.auction'),
        ),
    ]
