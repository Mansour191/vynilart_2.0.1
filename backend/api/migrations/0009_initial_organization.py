# Generated migration for organization models (additional models not in original SQL schema)
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_initial_blog_conversation'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=255, verbose_name='الاسم بالعربية', help_text='اسم المؤسسة باللغة العربية')),
                ('name_en', models.CharField(max_length=255, verbose_name='الاسم بالإنجليزية', help_text='اسم المؤسسة باللغة الإنجليزية')),
                ('logo', models.ImageField(help_text='شعار المؤسسة', max_length=255, upload_to='org/logo/', verbose_name='الشعار')),
                ('slogan_ar', models.CharField(max_length=500, verbose_name='الشعار بالعربية', help_text='الشعار التسويقي بالعربية')),
                ('slogan_en', models.CharField(max_length=500, verbose_name='الشعار بالإنجليزية', help_text='الشعار التسويقي بالإنجليزية')),
                ('about_ar', models.TextField(verbose_name='نبذة بالعربية', help_text='قصة المؤسسة ونبذة عنها بالعربية')),
                ('about_en', models.TextField(verbose_name='نبذة بالإنجليزية', help_text='قصة المؤسسة ونبذة عنها بالإنجليزية')),
                ('contact_email', models.EmailField(help_text='البريد الرسمي للتواصل', max_length=255, verbose_name='البريد الإلكتروني للتواصل')),
                ('phone_1', models.CharField(help_text='رقم الهاتف الرئيسي', max_length=20, verbose_name='الهاتف الأول')),
                ('phone_2', models.CharField(blank=True, help_text='رقم الهاتف الثانوي', max_length=20, null=True, verbose_name='الهاتف الثاني')),
                ('address', models.TextField(help_text='عنوان المقر الرئيسي', verbose_name='العنوان')),
                ('latitude', models.DecimalField(blank=True, decimal_places=16, help_text='إحداثيات خط العرض من جوجل مابس', max_digits=22, null=True, verbose_name='خط العرض')),
                ('longitude', models.DecimalField(blank=True, decimal_places=16, help_text='إحداثيات خط الطول من جوجل مابس', max_digits=22, null=True, verbose_name='خط الطول')),
                ('google_place_id', models.CharField(blank=True, help_text='معرف المكان من جوجل لضمان فتح الخريطة بدقة', max_length=255, verbose_name='معرف المكان في جوجل')),
                ('maps_url', models.URLField(blank=True, help_text='رابط مباشر لخرائط جوجل', max_length=500, verbose_name='رابط الخريطة')),
                ('tax_number', models.CharField(blank=True, help_text='الرقم الجبائي (NIF/NIS)', max_length=100, null=True, verbose_name='الرقم الضريبي')),
                ('is_active', models.BooleanField(default=True, help_text='هل المؤسسة نشطة حالياً', verbose_name='نشط')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('base_city', models.ForeignKey(blank=True, help_text='المدينة التي يقع فيها المقر الرئيسي', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='organizations', to='api.shipping', verbose_name='المدينة الأساسية')),
                ('created_by', models.ForeignKey(blank=True, help_text='المستخدم الذي أنشأ السجل', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_organizations', to='auth.user', verbose_name='أنشئ بواسطة')),
            ],
            options={
                'verbose_name': 'المؤسسة',
                'verbose_name_plural': 'المؤسسات',
                'ordering': ['-created_at'],
                'db_table': 'api_organization',
                'db_tablespace': '',
                'constraints': [
                    models.UniqueConstraint(
                        condition=models.Q(is_active=True),
                        fields=['id'],
                        name='singleton_active_organization'
                    )
                ],
                'indexes': [
                    models.Index(fields=['is_active'], name='org_is_active_idx'),
                    models.Index(fields=['base_city'], name='org_base_city_idx'),
                    models.Index(fields=['created_by'], name='org_created_by_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Social',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform_name', models.CharField(help_text='مثل: Facebook, TikTok, Instagram', max_length=50, verbose_name='اسم المنصة')),
                ('platform_type', models.CharField(choices=[('public', 'عام (للزبائن)'), ('internal', 'داخلي (للموظفين)'), ('partners', 'شركاء')], default='public', help_text='هل الرابط للزبائن أم للموظفين أم للشركاء', max_length=20, verbose_name='نوع المنصة')),
                ('url', models.URLField(help_text='رابط الحساب على المنصة', max_length=500, verbose_name='الرابط')),
                ('icon_class', models.CharField(help_text='مثل: fa-brands fa-facebook, fa-brands fa-instagram', max_length=100, verbose_name='كود الأيقونة')),
                ('order_index', models.PositiveIntegerField(default=0, help_text='ترتيب ظهور الرابط في القائمة', verbose_name='ترتيب الظهور')),
                ('is_active', models.BooleanField(default=True, help_text='هل الرابط نشط ومرئي', verbose_name='نشط')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_links', to='api.organization', verbose_name='المؤسسة')),
            ],
            options={
                'verbose_name': 'رابط اجتماعي',
                'verbose_name_plural': 'الروابط الاجتماعية',
                'ordering': ['order_index', 'platform_name'],
                'db_table': 'api_social',
                'db_tablespace': '',
                'indexes': [
                    models.Index(fields=['platform_name'], name='social_platform_name_idx'),
                    models.Index(fields=['is_active'], name='social_is_active_idx'),
                    models.Index(fields=['organization', 'is_active'], name='social_org_active_idx'),
                    models.Index(fields=['platform_type'], name='social_platform_type_idx'),
                    models.Index(fields=['order_index'], name='social_order_idx'),
                ],
                'unique_together': {('organization', 'platform_name')},
            },
        ),
    ]
