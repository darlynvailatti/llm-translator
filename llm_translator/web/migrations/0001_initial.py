# Generated by Django 5.1.6 on 2025-03-03 21:19

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AccountAPIKey',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(default=uuid.uuid4, max_length=128)),
                ('is_active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.account')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TranslationEndpoint',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(max_length=128, unique=True)),
                ('name', models.CharField(max_length=256)),
                ('is_active', models.BooleanField(default=True)),
                ('definition', models.JSONField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.account')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TranslationEvent',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('SUCCESS', 'SUCCESS'), ('SUCCESS', 'FAILURE')], max_length=128)),
                ('context', models.JSONField()),
                ('endpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.translationendpoint')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TranslationSpec',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=256)),
                ('definition', models.JSONField()),
                ('version', models.CharField(max_length=128)),
                ('endpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.translationendpoint')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
