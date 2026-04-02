# Generated manually

from django.db import migrations
from django.contrib.auth import get_user_model
import decimal


def create_sample_data(apps, schema_editor):
    User = apps.get_model('core', 'User')
    Category = apps.get_model('core', 'Category')
    Material = apps.get_model('core', 'Material')
    Product = apps.get_model('core', 'Product')
    ProductImage = apps.get_model('core', 'ProductImage')
    ProductVariant = apps.get_model('core', 'ProductVariant')
    Shipping = apps.get_model('core', 'Shipping')
    UserProfile = apps.get_model('core', 'UserProfile')
    DesignCategory = apps.get_model('core', 'DesignCategory')
    Design = apps.get_model('core', 'Design')
    BlogCategory = apps.get_model('core', 'BlogCategory')
    BlogPost = apps.get_model('core', 'BlogPost')
    PricingEngine = apps.get_model('core', 'PricingEngine')
    
    # Create sample users
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@vynilart.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        is_staff=True,
        is_superuser=True
    )
    
    customer_user = User.objects.create_user(
        username='customer',
        email='customer@example.com',
        password='customer123',
        first_name='Customer',
        last_name='User'
    )
    
    # Create user profiles
    UserProfile.objects.create(
        user=admin_user,
        phone='+213 555 010 001',
        address='Algiers, Algeria',
        bio='System administrator'
    )
    
    UserProfile.objects.create(
        user=customer_user,
        phone='+213 555 010 002',
        address='Oran, Algeria',
        bio='Regular customer'
    )
    
    # Create categories
    vinyl_category = Category.objects.create(
        name_ar='فينيل',
        name_en='Vinyl',
        slug='vinyl',
        icon='vinyl-icon',
        waste_percent=decimal.Decimal('10.00'),
        description='Vinyl products for decoration'
    )
    
    wallpaper_category = Category.objects.create(
        name_ar='ورق جدران',
        name_en='Wallpaper',
        slug='wallpaper',
        icon='wallpaper-icon',
        waste_percent=decimal.Decimal('15.00'),
        description='Wallpaper for home decoration'
    )
    
    # Create materials
    vinyl_premium = Material.objects.create(
        name_ar='فينيل ممتاز',
        name_en='Premium Vinyl',
        description='High quality vinyl material',
        price_per_m2=decimal.Decimal('1200.00'),
        is_premium=True,
        properties={'thickness': '3mm', 'durability': 'high'}
    )
    
    vinyl_standard = Material.objects.create(
        name_ar='فينيل عادي',
        name_en='Standard Vinyl',
        description='Standard quality vinyl material',
        price_per_m2=decimal.Decimal('800.00'),
        is_premium=False,
        properties={'thickness': '2mm', 'durability': 'medium'}
    )
    
    wallpaper_premium = Material.objects.create(
        name_ar='ورق جدران ممتاز',
        name_en='Premium Wallpaper',
        description='High quality wallpaper material',
        price_per_m2=decimal.Decimal('1500.00'),
        is_premium=True,
        properties={'thickness': '0.5mm', 'pattern': 'custom'}
    )
    
    # Create products
    product1 = Product.objects.create(
        name_ar='فينيل زخرفة إسلامية',
        name_en='Islamic Pattern Vinyl',
        slug='islamic-pattern-vinyl',
        description_ar='فينيل بزخارف إسلامية تقليدية',
        description_en='Vinyl with traditional Islamic patterns',
        base_price=decimal.Decimal('5000.00'),
        cost=decimal.Decimal('3000.00'),
        category=vinyl_category,
        is_featured=True,
        is_new=True,
        stock=50,
        weight=decimal.Decimal('2.5'),
        dimensions='100x100 cm',
        tags=['islamic', 'traditional', 'premium'],
        seo_title='Islamic Pattern Vinyl - VynilArt',
        seo_description='High quality vinyl with Islamic patterns'
    )
    
    product2 = Product.objects.create(
        name_ar='ورق جدران زهور',
        name_en='Floral Wallpaper',
        slug='floral-wallpaper',
        description_ar='ورق جدران بتصاميم زهور جميلة',
        description_en='Beautiful floral wallpaper designs',
        base_price=decimal.Decimal('3500.00'),
        cost=decimal.Decimal('2000.00'),
        category=wallpaper_category,
        on_sale=True,
        discount_percent=20,
        stock=30,
        weight=decimal.Decimal('1.5'),
        dimensions='100x100 cm',
        tags=['floral', 'modern', 'sale'],
        seo_title='Floral Wallpaper - VynilArt',
        seo_description='Beautiful floral wallpaper for your home'
    )
    
    product3 = Product.objects.create(
        name_ar='فينيل هندسي',
        name_en='Geometric Vinyl',
        slug='geometric-vinyl',
        description_ar='فينيل بتصاميم هندسية عصرية',
        description_en='Modern geometric vinyl designs',
        base_price=decimal.Decimal('4500.00'),
        cost=decimal.Decimal('2800.00'),
        category=vinyl_category,
        is_featured=True,
        stock=25,
        weight=decimal.Decimal('2.0'),
        dimensions='100x100 cm',
        tags=['geometric', 'modern', 'contemporary'],
        seo_title='Geometric Vinyl - VynilArt',
        seo_description='Modern geometric vinyl designs'
    )
    
    # Create product images
    ProductImage.objects.create(
        product=product1,
        image_url='/media/products/islamic-vinyl-1.jpg',
        alt_text='Islamic Pattern Vinyl - Main Image',
        is_main=True,
        sort_order=1
    )
    
    ProductImage.objects.create(
        product=product1,
        image_url='/media/products/islamic-vinyl-2.jpg',
        alt_text='Islamic Pattern Vinyl - Detail',
        is_main=False,
        sort_order=2
    )
    
    ProductImage.objects.create(
        product=product2,
        image_url='/media/products/floral-wallpaper-1.jpg',
        alt_text='Floral Wallpaper - Main Image',
        is_main=True,
        sort_order=1
    )
    
    ProductImage.objects.create(
        product=product3,
        image_url='/media/products/geometric-vinyl-1.jpg',
        alt_text='Geometric Vinyl - Main Image',
        is_main=True,
        sort_order=1
    )
    
    # Create product variants
    ProductVariant.objects.create(
        product=product1,
        name='حجم صغير',
        sku='VIN-001-S',
        price=decimal.Decimal('2500.00'),
        stock=20,
        attributes={'size': '50x50 cm', 'color': 'gold'}
    )
    
    ProductVariant.objects.create(
        product=product1,
        name='حجم كبير',
        sku='VIN-001-L',
        price=decimal.Decimal('5000.00'),
        stock=15,
        attributes={'size': '100x100 cm', 'color': 'gold'}
    )
    
    ProductVariant.objects.create(
        product=product2,
        name='حجم قياسي',
        sku='WALL-002-M',
        price=decimal.Decimal('3500.00'),
        stock=30,
        attributes={'size': '100x100 cm', 'pattern': 'floral'}
    )
    
    # Create shipping locations (Algerian Wilayas)
    shipping_data = [
        ('16', 'الجزائر', 'Alger'),
        ('01', 'أدرار', 'Adrar'),
        ('02', 'شلف', 'Chlef'),
        ('03', 'أغواط', 'Laghouat'),
        ('04', 'أم البواقي', 'Oum El Bouaghi'),
        ('05', 'باتنة', 'Batna'),
        ('06', 'بجاية', 'Bejaia'),
        ('07', 'بسكرة', 'Biskra'),
        ('08', 'بشار', 'Bechar'),
        ('09', 'البليدة', 'Blida')
    ]
    
    for wilaya_id, name_ar, name_fr in shipping_data:  # Create all wilayas
        Shipping.objects.create(
            wilaya_id=wilaya_id,
            name_ar=name_ar,
            name_fr=name_fr,
            stop_desk_price=decimal.Decimal('400.00'),
            home_delivery_price=decimal.Decimal('700.00')
        )
    
    # Create design categories
    design_cat1 = DesignCategory.objects.create(
        name_ar='زخارف إسلامية',
        name_en='Islamic Patterns',
        slug='islamic-patterns',
        description='Traditional Islamic design patterns',
        is_active=True
    )
    
    design_cat2 = DesignCategory.objects.create(
        name_ar='تصاميم حديثة',
        name_en='Modern Designs',
        slug='modern-designs',
        description='Contemporary design patterns',
        is_active=True
    )
    
    # Create designs
    Design.objects.create(
        name='Islamic Geometric Pattern 1',
        description='Beautiful Islamic geometric pattern with traditional colors',
        category=design_cat1,
        user=admin_user,
        is_featured=True,
        is_active=True,
        likes=25,
        downloads=15,
        tags=['islamic', 'geometric', 'traditional'],
        status='approved'
    )
    
    Design.objects.create(
        name='Modern Abstract Pattern',
        description='Contemporary abstract design for modern spaces',
        category=design_cat2,
        user=admin_user,
        is_active=True,
        likes=18,
        downloads=8,
        tags=['modern', 'abstract', 'contemporary'],
        status='approved'
    )
    
    # Create blog categories
    blog_cat1 = BlogCategory.objects.create(
        name_ar='ديكور',
        name_en='Decoration',
        slug='decoration',
        description='Tips and ideas for home decoration'
    )
    
    blog_cat2 = BlogCategory.objects.create(
        name_ar='تصاميم',
        name_en='Designs',
        slug='designs',
        description='Latest design trends and ideas'
    )
    
    # Create blog posts
    BlogPost.objects.create(
        title_ar='أفكار ديكور لغرفة المعيشة',
        title_en='Living Room Decoration Ideas',
        slug='living-room-decoration-ideas',
        content_ar='هنا تكتب أفكار ديكور رائعة لغرفة المعيشة...',
        content_en='Here you write great decoration ideas for the living room...',
        summary_ar='أفضل أفكار ديكور لغرفة المعيشة',
        summary_en='Best living room decoration ideas',
        category=blog_cat1,
        author=admin_user,
        views=150,
        is_published=True,
        tags=['living room', 'decoration', 'ideas']
    )
    
    BlogPost.objects.create(
        title_ar='أحدث اتجاهات التصميم الداخلي',
        title_en='Latest Interior Design Trends',
        slug='latest-interior-design-trends',
        content_ar='أحدث اتجاهات التصميم الداخلي لعام 2024...',
        content_en='Latest interior design trends for 2024...',
        summary_ar='تعرف على أحدث اتجاهات التصميم',
        summary_en='Discover the latest design trends',
        category=blog_cat2,
        author=admin_user,
        views=200,
        is_published=True,
        tags=['trends', 'interior', 'modern']
    )
    
    # Create pricing engine configuration
    PricingEngine.objects.create(
        raw_material_cost=decimal.Decimal('500.00'),
        labor_cost=decimal.Decimal('300.00'),
        international_shipping=decimal.Decimal('200.00')
    )


def remove_sample_data(apps, schema_editor):
    User = apps.get_model('core', 'User')
    Category = apps.get_model('core', 'Category')
    Material = apps.get_model('core', 'Material')
    Product = apps.get_model('core', 'Product')
    Shipping = apps.get_model('core', 'Shipping')
    UserProfile = apps.get_model('core', 'UserProfile')
    DesignCategory = apps.get_model('core', 'DesignCategory')
    Design = apps.get_model('core', 'Design')
    BlogCategory = apps.get_model('core', 'BlogCategory')
    BlogPost = apps.get_model('core', 'BlogPost')
    PricingEngine = apps.get_model('core', 'PricingEngine')
    
    # Remove created users
    User.objects.filter(username__in=['admin', 'customer']).delete()
    
    # Remove other data
    UserProfile.objects.all().delete()
    Category.objects.all().delete()
    Material.objects.all().delete()
    Product.objects.all().delete()
    Shipping.objects.all().delete()
    DesignCategory.objects.all().delete()
    Design.objects.all().delete()
    BlogCategory.objects.all().delete()
    BlogPost.objects.all().delete()
    PricingEngine.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_sample_data, remove_sample_data),
    ]
