# Generated by Django 5.0.2 on 2024-02-21 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=30, verbose_name='Phone number of client')),
                ('chat_id', models.CharField(max_length=30, verbose_name='Chat ID of client.')),
                ('name', models.CharField(max_length=100, verbose_name='Contact name')),
                ('is_open', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_change', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TelegramAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=30, verbose_name='Phone number of merchant')),
                ('merchant_id', models.CharField(max_length=100)),
                ('session_string', models.TextField(blank=True, verbose_name='Telegram account session string.')),
                ('chat_id', models.CharField(blank=True, max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_change', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(0, 'Unknown'), (1, 'Success'), (2, 'Server Not Received'), (3, 'Client Not Received')], default=0)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contact_messages', to='backend.contact')),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchant_messages', to='backend.telegramaccount')),
            ],
        ),
    ]