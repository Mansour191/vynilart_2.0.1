# Generated migration for blog and conversation models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_initial_analytics'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=255)),
                ('name_en', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'api_blogcategory',
                'indexes': [
                    models.Index(fields=['slug']),
                    models.Index(fields=['created_at']),
                ],
                'ordering': ['name_ar'],
            },
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_ar', models.CharField(max_length=255)),
                ('title_en', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('content_ar', models.TextField()),
                ('content_en', models.TextField()),
                ('summary_ar', models.TextField(blank=True, null=True)),
                ('summary_en', models.TextField(blank=True, null=True)),
                ('featured_image', models.CharField(blank=True, max_length=500, null=True)),
                ('tags', models.JSONField(blank=True, default=list)),
                ('views', models.IntegerField(default=0)),
                ('is_published', models.BooleanField(default=False)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(blank=True, db_column='author_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
                ('category', models.ForeignKey(blank=True, db_column='category_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.blogcategory')),
            ],
            options={
                'db_table': 'api_blogpost',
                'indexes': [
                    models.Index(fields=['slug']),
                    models.Index(fields=['category']),
                    models.Index(fields=['author']),
                    models.Index(fields=['is_published']),
                    models.Index(fields=['published_at']),
                    models.Index(fields=['created_at']),
                    models.Index(fields=['views']),
                ],
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ConversationHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=20)),
                ('message', models.TextField()),
                ('source', models.CharField(default='user', max_length=50)),
                ('confidence', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'api_conversationhistory',
                'indexes': [
                    models.Index(fields=['session_id']),
                    models.Index(fields=['role']),
                    models.Index(fields=['source']),
                    models.Index(fields=['created_at']),
                ],
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='DashboardSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('widgets', models.JSONField(blank=True, default=dict)),
                ('layout', models.JSONField(blank=True, default=dict)),
                ('preferences', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_settings', to='auth.user')),
            ],
            options={
                'db_table': 'api_dashboardsettings',
                'indexes': [
                    models.Index(fields=['user']),
                    models.Index(fields=['created_at']),
                ],
            },
        ),
        migrations.CreateModel(
            name='WishlistSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_add', models.BooleanField(default=True)),
                ('max_items', models.IntegerField(default=100)),
                ('email_reminders', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_settings_new', to='auth.user')),
            ],
            options={
                'db_table': 'api_wishlistsettings',
                'indexes': [
                    models.Index(fields=['user']),
                    models.Index(fields=['created_at']),
                ],
            },
        ),
    ]
