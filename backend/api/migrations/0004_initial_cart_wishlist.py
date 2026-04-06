# Generated migration for cart and wishlist models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_initial_orders'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('options', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('material', models.ForeignKey(blank=True, db_column='material_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.material')),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='api.product')),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='auth.user')),
            ],
            options={
                'db_table': 'api_cartitem',
                'indexes': [
                    models.Index(fields=['user']),
                    models.Index(fields=['product']),
                    models.Index(fields=['material']),
                    models.Index(fields=['created_at']),
                ],
            },
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_entries', to='api.product')),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_items', to='auth.user')),
            ],
            options={
                'db_table': 'api_wishlist',
                'indexes': [
                    models.Index(fields=['user']),
                    models.Index(fields=['product']),
                    models.Index(fields=['created_at']),
                ],
                'unique_together': {('user', 'product')},
            },
        ),
    ]
