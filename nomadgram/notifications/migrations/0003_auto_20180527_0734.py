# Generated by Django 2.0.4 on 2018-05-26 22:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_notification_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created_at']},
        ),
    ]