# Generated migration for review and design models
from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MaxValueValidator, MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_initial_cart_wishlist'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(max_value=5, min_value=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('helpful_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.CASCADE, to='api.product')),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'api_review',
                'indexes': [
                    models.Index(fields=['product']),
                    models.Index(fields=['user']),
                    models.Index(fields=['rating']),
                    models.Index(fields=['is_verified']),
                    models.Index(fields=['created_at']),
                ],
                'unique_together': {('user', 'product')},
            },
        ),
        migrations.CreateModel(
            name='ReviewReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('review', models.ForeignKey(db_column='review_id', on_delete=django.db.models.deletion.CASCADE, to='api.review')),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'api_reviewreport',
                'indexes': [
                    models.Index(fields=['review']),
                    models.Index(fields=['user']),
                    models.Index(fields=['created_at']),
                ],
                'unique_together': {('review', 'user')},
            },
        ),
        migrations.CreateModel(
            name='DesignCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=255)),
                ('name_en', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.CharField(blank=True, max_length=500, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('design_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'api_designcategory',
                'indexes': [
                    models.Index(fields=['slug']),
                    models.Index(fields=['is_active']),
                    models.Index(fields=['design_count']),
                ],
                'ordering': ['name_ar'],
            },
        ),
        migrations.CreateModel(
            name='Design',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.CharField(blank=True, max_length=500, null=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('likes', models.IntegerField(default=0)),
                ('downloads', models.IntegerField(default=0)),
                ('tags', models.JSONField(blank=True, default=list)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('generated_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, db_column='category_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.designcategory')),
                ('user', models.ForeignKey(blank=True, db_column='user_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'db_table': 'api_design',
                'indexes': [
                    models.Index(fields=['category']),
                    models.Index(fields=['user']),
                    models.Index(fields=['is_featured']),
                    models.Index(fields=['is_active']),
                    models.Index(fields=['status']),
                    models.Index(fields=['likes']),
                    models.Index(fields=['downloads']),
                    models.Index(fields=['created_at']),
                ],
                'ordering': ['-created_at'],
            },
        ),
    ]
