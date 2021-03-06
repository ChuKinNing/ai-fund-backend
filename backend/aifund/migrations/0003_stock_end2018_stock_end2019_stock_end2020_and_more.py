# Generated by Django 4.0.3 on 2022-04-08 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aifund', '0002_socialaccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='end2018',
            field=models.FloatField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='end2019',
            field=models.FloatField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='end2020',
            field=models.FloatField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='end2021',
            field=models.FloatField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='start2018',
            field=models.FloatField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='start2019',
            field=models.FloatField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='start2020',
            field=models.FloatField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='start2021',
            field=models.FloatField(blank=True, max_length=20, null=True),
        ),
    ]
