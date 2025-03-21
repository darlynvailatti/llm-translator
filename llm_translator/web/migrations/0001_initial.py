# Generated by Django 5.1.6 on 2025-03-19 04:47

import django.db.models.deletion
import uuid
import web.constants
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
                ('key', models.CharField(default=uuid.uuid4, max_length=128, unique=True)),
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
                ('status', models.CharField(choices=[(web.constants.TranslationEventStatus['SUCCESS'], web.constants.TranslationEventStatus['SUCCESS']), (web.constants.TranslationEventStatus['SUCCESS'], web.constants.TranslationEventStatus['FAILURE'])], max_length=128)),
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
                ('is_active', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=256)),
                ('definition', models.JSONField()),
                ('version', models.CharField(max_length=128)),
                ('endpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.translationendpoint')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TranslationArtifact',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('implementation', models.BinaryField()),
                ('implementation_type', models.CharField(choices=[(web.constants.TranslationArtifcatImplType['PYTHON'], web.constants.TranslationArtifcatImplType['PYTHON'])], default=web.constants.TranslationArtifcatImplType['PYTHON'], max_length=128)),
                ('spec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.translationspec')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SpecTestCase',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=256)),
                ('definition', models.JSONField()),
                ('executed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[(web.constants.TranslationTestCaseStatus['SUCCESS'], web.constants.TranslationTestCaseStatus['SUCCESS']), (web.constants.TranslationTestCaseStatus['FAILURE'], web.constants.TranslationEventStatus['FAILURE']), (web.constants.TranslationTestCaseStatus['NOT_EXECUTED'], web.constants.TranslationTestCaseStatus['NOT_EXECUTED'])], default=web.constants.TranslationTestCaseStatus['NOT_EXECUTED'], max_length=128)),
                ('spec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.translationspec')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
