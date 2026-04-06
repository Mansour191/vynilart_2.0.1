# Generated migration for product and catalog models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=255)),
                ('name_en', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('icon', models.CharField(blank=True, max_length=100, null=True)),
                ('waste_percent', models.DecimalField(decimal_places=2, default=10.0, max_digits=5)),
                ('is_active', models.BooleanField(default=True)),
                ('image', models.CharField(blank=True, max_length=500, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, db_column='parent_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='api.category')),
            ],
            options={
                'db_table': 'api_category',
                'indexes': [
                    models.Index(fields=['slug']),
                    models.Index(fields=['parent']),
                    models.Index(fields=['is_active']),
                ],
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['name_ar'],
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=255)),
                ('name_en', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('price_per_m2', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('is_premium', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('image', models.CharField(blank=True, max_length=500, null=True)),
                ('properties', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'api_material',
                'indexes': [
                    models.Index(fields=['is_active']),
                    models.Index(fields=['is_premium']),
                ],
                'ordering': ['name_ar'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=255)),
                ('name_en', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('description_ar', models.TextField(blank=True, null=True)),
                ('description_en', models.TextField(blank=True, null=True)),
                ('base_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('on_sale', models.BooleanField(default=False)),
                ('discount_percent', models.IntegerField(default=0)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_new', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('stock', models.IntegerField(default=0)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('dimensions', models.CharField(blank=True, max_length=100, null=True)),
                ('tags', models.JSONField(blank=True, default=list)),
                ('seo_title', models.CharField(blank=True, max_length=255, null=True)),
                ('seo_description', models.TextField(blank=True, null=True)),
                ('sync_status', models.CharField(default='pending', max_length=20)),
                ('erpnext_item_code', models.CharField(blank=True, max_length=100, null=True)),
                ('sync_error', models.TextField(blank=True, null=True)),
                ('last_synced_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, db_column='category_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='api.category')),
            ],
            options={
                'db_table': 'api_product',
                'indexes': [
                    models.Index(fields=['slug']),
                    models.Index(fields=['category']),
                    models.Index(fields=['is_active']),
                    models.Index(fields=['is_featured']),
                    models.Index(fields=['is_new']),
                    models.Index(fields=['on_sale']),
                    models.Index(fields=['stock']),
                    models.Index(fields=['created_at']),
                ],
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.CharField(max_length=500)),
                ('alt_text', models.CharField(blank=True, max_length=255, null=True)),
                ('is_main', models.BooleanField(default=False)),
                ('sort_order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.CASCADE, related_name='images', to='api.product')),
            ],
            options={
                'db_table': 'api_productimage',
                'indexes': [
                    models.Index(fields=['product']),
                    models.Index(fields=['product', 'is_main']),
                    models.Index(fields=['sort_order']),
                ],
                'ordering': ['sort_order'],
            },
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('sku', models.CharField(max_length=100, unique=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.IntegerField(default=0)),
                ('attributes', models.JSONField(blank=True, default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='api.product')),
            ],
            options={
                'db_table': 'api_productvariant',
                'indexes': [
                    models.Index(fields=['product']),
                    models.Index(fields=['sku']),
                    models.Index(fields=['is_active']),
                ],
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ProductMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material', models.ForeignKey(db_column='material_id', on_delete=django.db.models.deletion.CASCADE, related_name='product_materials', to='api.material')),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.CASCADE, related_name='product_materials', to='api.product')),
            ],
            options={
                'db_table': 'api_product_materials',
                'indexes': [
                    models.Index(fields=['product']),
                    models.Index(fields=['material']),
                ],
                'unique_together': {('product', 'material')},
            },
        ),
    ]
