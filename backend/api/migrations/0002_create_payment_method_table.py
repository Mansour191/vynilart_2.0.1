"""
Create Payment Method Table Migration

This migration creates the api_payment_method table for storing
configurable payment methods with multilingual support and account details.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=100, verbose_name='الاسم بالعربية', help_text='اسم طريقة الدفع بالعربية')),
                ('name_en', models.CharField(max_length=100, verbose_name='الاسم بالإنجليزية', help_text='اسم طريقة الدفع بالإنجليزية')),
                ('payment_type', models.CharField(max_length=20, default='cash', verbose_name='نوع الدفع', help_text='نوع طريقة الدفع', choices=[
                    ('cash', 'الدفع عند الاستلام'),
                    ('bank_transfer', 'تحويل بنكي'),
                    ('wallet', 'محفظة إلكترونية'),
                    ('card', 'بطاقة بنكية'),
                    ('other', 'أخرى')
                ])),
                ('gateway_provider', models.CharField(max_length=50, blank=True, null=True, verbose_name='مزود البوابة', help_text='مزود بوابة الدفع')),
                ('account_name', models.CharField(max_length=200, blank=True, null=True, verbose_name='اسم الحساب', help_text='اسم صاحب الحساب أو المستفيد')),
                ('account_number', models.CharField(max_length=100, blank=True, null=True, verbose_name='رقم الحساب/الحساب البريدي الجاري', help_text='رقم الحساب البنكي أو الحساب البريدي الجاري (CCP)')),
                ('iban', models.CharField(max_length=34, blank=True, null=True, verbose_name='IBAN', help_text='رقم الحساب البنكي الدولي (IBAN)')),
                ('instructions_ar', models.TextField(blank=True, null=True, verbose_name='التعليمات بالعربية', help_text='تعليمات الدفع للزبائن بالعربية')),
                ('instructions_en', models.TextField(blank=True, null=True, verbose_name='التعليمات بالإنجليزية', help_text='تعليمات الدفع للزبائن بالإنجليزية')),
                ('icon', models.CharField(max_length=100, blank=True, null=True, verbose_name='الأيقونة', help_text='كود أيقونة Font Awesome')),
                ('logo', models.ImageField(upload_to='payment_methods/logos/', max_length=255, blank=True, null=True, verbose_name='الشعار', help_text='شعار البنك أو خدمة الدفع')),
                ('order_index', models.PositiveIntegerField(default=0, verbose_name='ترتيب الظهور', help_text='ترتيب ظهور طريقة الدفع في القائمة')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط', help_text='هل طريقة الدفع نشطة ومتاحة للزبائن')),
                ('is_default', models.BooleanField(default=False, verbose_name='افتراضي', help_text='طريقة الدفع الافتراضية (واحدة فقط)')),
                ('max_amount', models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='الحد الأقصى للمبلغ', help_text='الحد الأقصى للمبلغ المسموح بهذه الطريقة')),
                ('fee_percentage', models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='نسبة الرسوم', help_text='نسبة الرسوم المضافة للمبلغ (%)')),
                ('fee_fixed', models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='رسوم ثابتة', help_text='رسوم ثابتة مضافة للمبلغ')),
                ('created_by', models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='أنشئ بواسطة', help_text='المستخدم الذي أنشأ طريقة الدفع', related_name='created_payment_methods')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
            ],
            options={
                'verbose_name': 'طريقة دفع',
                'verbose_name_plural': 'طرق الدفع',
                'db_table': 'api_payment_method',
                'db_tablespace': '',
                'indexes': [
                    models.Index(fields=['is_active'], name='payment_method_is_active_idx'),
                    models.Index(fields=['payment_type'], name='payment_method_type_idx'),
                    models.Index(fields=['order_index'], name='payment_method_order_idx'),
                    models.Index(fields=['is_default'], name='payment_method_default_idx'),
                ],
                'constraints': [
                    models.UniqueConstraint(
                        fields=['is_default'],
                        condition=models.Q(is_default=True),
                        name='single_default_payment_method'
                    )
                ]
            }
        ),
        
        # Create default payment methods
        migrations.RunSQL(
            sql="""
            INSERT INTO api_payment_method (
                name_ar, name_en, payment_type, instructions_ar, instructions_en, 
                icon, order_index, is_active, is_default, created_at, updated_at
            ) VALUES
            ('الدفع عند الاستلام', 'Cash on Delivery', 'cash', 
             'يمكنك الدفع نقداً عند استلام المنتجات من الساعي.', 
             'You can pay cash when courier delivers your products.', 
             'fas fa-hand-holding-usd', 1, true, true, NOW(), NOW()),
            
            ('تحويل بنكي - CCP', 'Bank Transfer - CCP', 'bank_transfer',
             'قم بتحويل المبلغ إلى الحساب البريدي الجاري (CCP) المحدد. يرجى إرسال إيصال التحويل عبر الواتساب.',
             'Transfer amount to the specified CCP account. Please send transfer receipt via WhatsApp.',
             'fas fa-university', 2, true, false, NOW(), NOW()),
            
            ('BaridiMob', 'BaridiMob', 'wallet',
             'افتح تطبيق BaridiMob وقم بتحويل المبلغ إلى الرقم المحدد.',
             'Open BaridiMob app and transfer amount to the specified number.',
             'fas fa-mobile-alt', 3, true, false, NOW(), NOW());
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
    ]
