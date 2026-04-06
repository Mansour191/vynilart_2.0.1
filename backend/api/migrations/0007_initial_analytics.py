# Generated migration for analytics and AI models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_initial_notifications'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='BehaviorTracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=100)),
                ('target_type', models.CharField(blank=True, max_length=50, null=True)),
                ('target_id', models.IntegerField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'api_behaviortracking',
                'indexes': [
                    models.Index(fields=['user']),
                    models.Index(fields=['action']),
                    models.Index(fields=['target_type']),
                    models.Index(fields=['created_at']),
                ],
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Forecast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forecast_type', models.CharField(max_length=50)),
                ('period', models.CharField(max_length=20)),
                ('predicted_demand', models.IntegerField(blank=True, null=True)),
                ('confidence', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(db_column='product_id', on_delete=django.db.models.deletion.CASCADE, to='api.product')),
            ],
            options={
                'db_table': 'api_forecast',
                'indexes': [
                    models.Index(fields=['product']),
                    models.Index(fields=['forecast_type']),
                    models.Index(fields=['period']),
                    models.Index(fields=['created_at']),
                ],
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CustomerSegment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('criteria', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'api_customersegment',
                'indexes': [
                    models.Index(fields=['name']),
                    models.Index(fields=['created_at']),
                ],
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CustomerSegmentUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customersegment', models.ForeignKey(db_column='customersegment_id', on_delete=django.db.models.deletion.CASCADE, to='api.customersegment')),
                ('user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'api_customersegment_users',
                'indexes': [
                    models.Index(fields=['customersegment']),
                    models.Index(fields=['user']),
                ],
                'unique_together': {('customersegment', 'user')},
            },
        ),
        migrations.CreateModel(
            name='PricingEngine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_material_cost', models.DecimalField(decimal_places=2, default=500, max_digits=10)),
                ('labor_cost', models.DecimalField(decimal_places=2, default=300, max_digits=10)),
                ('international_shipping', models.DecimalField(decimal_places=2, default=200, max_digits=10)),
            ],
            options={
                'db_table': 'api_pricingengine',
            },
        ),
        migrations.CreateModel(
            name='ERPNextSyncLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=100)),
                ('status', models.CharField(default='running', max_length=20)),
                ('message', models.TextField(blank=True, null=True)),
                ('records_synced', models.IntegerField(default=0)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'api_erpnextsynclog',
                'indexes': [
                    models.Index(fields=['action']),
                    models.Index(fields=['status']),
                    models.Index(fields=['timestamp']),
                ],
                'ordering': ['-timestamp'],
            },
        ),
    ]
