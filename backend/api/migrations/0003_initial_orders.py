# Generated migration for shipping and order models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_initial_products'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shipping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wilaya_id', models.CharField(max_length=10, unique=True)),
                ('name_ar', models.CharField(max_length=255)),
                ('name_fr', models.CharField(max_length=255)),
                ('stop_desk_price', models.DecimalField(decimal_places=2, default=400, max_digits=10)),
                ('home_delivery_price', models.DecimalField(decimal_places=2, default=700, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('regions', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'api_shipping',
                'indexes': [
                    models.Index(fields=['wilaya_id']),
                    models.Index(fields=['is_active']),
                ],
                'ordering': ['wilaya_id'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=50, unique=True)),
                ('customer_name', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('shipping_address', models.TextField()),
                ('wilaya_id', models.CharField(blank=True, db_column='wilaya_id', max_length=10, null=True)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('payment_method', models.CharField(default='cod', max_length=20)),
                ('payment_status', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True, null=True)),
                ('sync_status', models.CharField(default='pending', max_length=20)),
                ('erpnext_sales_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('sync_error', models.TextField(blank=True, null=True)),
                ('last_synced_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, db_column='user_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='auth.user')),
            ],
            options={
                'db_table': 'api_order',
                'indexes': [
                    models.Index(fields=['order_number']),
                    models.Index(fields=['user']),
                    models.Index(fields=['status']),
                    models.Index(fields=['created_at']),
                    models.Index(fields=['wilaya_id']),
                    models.Index(fields=['payment_method']),
                ],
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('width', models.DecimalField(decimal_places=2, max_digits=10)),
                ('height', models.DecimalField(decimal_places=2, max_digits=10)),
                ('dimension_unit', models.CharField(default='cm', max_length=10)),
                ('marble_texture', models.CharField(blank=True, max_length=100, null=True)),
                ('custom_design', models.TextField(blank=True, null=True)),
                ('quantity', models.IntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('material', models.ForeignKey(blank=True, db_column='material_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.material')),
                ('order', models.ForeignKey(db_column='order_id', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='api.order')),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.CASCADE, to='api.product')),
            ],
            options={
                'db_table': 'api_orderitem',
                'indexes': [
                    models.Index(fields=['order']),
                    models.Index(fields=['product']),
                    models.Index(fields=['material']),
                ],
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderTimeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=50)),
                ('note', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(db_column='order_id', on_delete=django.db.models.deletion.CASCADE, related_name='timeline', to='api.order')),
                ('user', models.ForeignKey(blank=True, db_column='user_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'db_table': 'api_ordertimeline',
                'indexes': [
                    models.Index(fields=['order']),
                    models.Index(fields=['status']),
                    models.Index(fields=['timestamp']),
                ],
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('method', models.CharField(max_length=50)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('gateway_response', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(db_column='order_id', on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='api.order')),
            ],
            options={
                'db_table': 'api_payment',
                'indexes': [
                    models.Index(fields=['order']),
                    models.Index(fields=['status']),
                    models.Index(fields=['transaction_id']),
                    models.Index(fields=['created_at']),
                ],
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_type', models.CharField(default='percentage', max_length=20)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('min_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('max_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('usage_limit', models.IntegerField(blank=True, null=True)),
                ('used_count', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('valid_from', models.DateTimeField(blank=True, null=True)),
                ('valid_to', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'api_coupon',
                'indexes': [
                    models.Index(fields=['code']),
                    models.Index(fields=['is_active']),
                    models.Index(fields=['valid_from']),
                    models.Index(fields=['valid_to']),
                ],
                'ordering': ['-created_at'],
            },
        ),
    ]
