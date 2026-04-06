# Generated migration for notification and alert models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_initial_reviews_designs'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('type', models.CharField(default='info', max_length=50)),
                ('is_read', models.BooleanField(default=False)),
                ('data', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'api_notification',
                'indexes': [
                    models.Index(fields=['user']),
                    models.Index(fields=['is_read']),
                    models.Index(fields=['type']),
                    models.Index(fields=['created_at']),
                ],
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
                ('message', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('conditions', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'api_alert',
                'indexes': [
                    models.Index(fields=['user']),
                    models.Index(fields=['type']),
                    models.Index(fields=['is_active']),
                    models.Index(fields=['created_at']),
                ],
                'ordering': ['-created_at'],
            },
        ),
    ]
