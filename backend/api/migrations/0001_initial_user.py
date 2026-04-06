# Generated migration for user models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('avatar', models.CharField(blank=True, max_length=255, null=True)),
                ('preferences', models.JSONField(blank=True, default=dict)),
                ('settings', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='auth.user')),
            ],
            options={
                'db_table': 'api_userprofile',
                'indexes': [
                    models.Index(fields=['user']),
                    models.Index(fields=['created_at']),
                ],
            },
        ),
    ]
