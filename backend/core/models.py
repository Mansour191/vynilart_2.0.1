from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
import uuid


class User(AbstractUser):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    preferences = models.JSONField(default=dict, blank=True)
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Category(models.Model):
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    waste_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    is_active = models.BooleanField(default=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_ar


class Material(models.Model):
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price_per_m2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    properties = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_ar


class Product(models.Model):
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description_ar = models.TextField(blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    on_sale = models.BooleanField(default=False)
    discount_percent = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    stock = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    sync_status = models.CharField(max_length=20, default='pending')
    erpnext_item_code = models.CharField(max_length=100, blank=True, null=True)
    sync_error = models.TextField(blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_ar

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=500)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_main = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name_ar} - Image"

    class Meta:
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['product', 'is_main']),
            models.Index(fields=['product', 'sort_order']),
            models.Index(fields=['is_main']),
            models.Index(fields=['sort_order']),
        ]


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    attributes = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name_ar} - {self.name}"


class ProductMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='available_materials')
    material = models.ForeignKey('Material', on_delete=models.CASCADE, related_name='product_assignments')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name_ar} - {self.material.name_ar}"

    class Meta:
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['material']),
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['material', 'is_active']),
            models.Index(fields=['product', 'material']),
        ]
        unique_together = ['product', 'material']


class ShippingMethod(models.Model):
    """Shipping providers/methods table"""
    PROVIDER_CHOICES = [
        ('yalidine', 'Yalidine'),
        ('zr_express', 'ZR Express'),
        ('fedex', 'FedEx'),
        ('dhl', 'DHL'),
        ('aramex', 'Aramex'),
        ('local_post', 'Local Post'),
        ('custom', 'Custom'),
    ]
    
    SERVICE_TYPE_CHOICES = [
        ('home', 'Home Delivery'),
        ('desk', 'Stop Desk'),
        ('express', 'Express Delivery'),
        ('economy', 'Economy Delivery'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Provider Name')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, verbose_name='Provider')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, verbose_name='Service Type')
    expected_delivery_time = models.IntegerField(verbose_name='Expected Delivery Time (days)')
    logo = models.ImageField(upload_to='shipping_logos/', null=True, blank=True, verbose_name='Logo')
    description = models.TextField(blank=True, verbose_name='Description')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    # Tracking and API integration
    tracking_url_template = models.URLField(blank=True, verbose_name='Tracking URL Template')
    api_endpoint = models.URLField(blank=True, verbose_name='API Endpoint')
    api_key = models.CharField(max_length=100, blank=True, verbose_name='API Key')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"

    class Meta:
        verbose_name = 'Shipping Method'
        verbose_name_plural = 'Shipping Methods'
        ordering = ['provider', 'service_type']
        indexes = [
            models.Index(fields=['provider', 'service_type']),
            models.Index(fields=['is_active']),
        ]


class ShippingPrice(models.Model):
    """Shipping prices table linking wilayas with shipping methods"""
    wilaya = models.ForeignKey('Shipping', on_delete=models.CASCADE, related_name='shipping_prices')
    shipping_method = models.ForeignKey('ShippingMethod', on_delete=models.CASCADE, related_name='prices')
    
    home_delivery_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Home Delivery Price')
    stop_desk_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Stop Desk Price')
    express_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Express Price')
    
    # Additional pricing options
    free_shipping_minimum = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Free Shipping Minimum')
    weight_surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Weight Surcharge (per kg)')
    volume_surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Volume Surcharge (per m³)')
    
    # Service level options
    cod_available = models.BooleanField(default=True, verbose_name='COD Available')
    insurance_available = models.BooleanField(default=False, verbose_name='Insurance Available')
    tracking_available = models.BooleanField(default=True, verbose_name='Tracking Available')
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.wilaya.name_ar} - {self.shipping_method.name}"

    class Meta:
        verbose_name = 'Shipping Price'
        verbose_name_plural = 'Shipping Prices'
        unique_together = ['wilaya', 'shipping_method']
        indexes = [
            models.Index(fields=['wilaya', 'shipping_method']),
            models.Index(fields=['is_active']),
            models.Index(fields=['home_delivery_price']),
            models.Index(fields=['stop_desk_price']),
        ]


class Shipping(models.Model):
    """Enhanced Shipping model for wilayas"""
    wilaya_id = models.CharField(max_length=10, unique=True)
    wilaya_code = models.IntegerField(help_text="رقم الولاية (1-58)")
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    regions = models.JSONField(default=list, blank=True)
    
    # Google Maps Integration
    pickup_latitude = models.DecimalField(
        max_digits=22,
        decimal_places=16,
        null=True,
        blank=True,
        verbose_name='خط عرض نقطة الاستلام',
        help_text='إحداثيات خط العرض لنقطة الاستلام أو مركز التوزيع'
    )
    pickup_longitude = models.DecimalField(
        max_digits=22,
        decimal_places=16,
        null=True,
        blank=True,
        verbose_name='خط طول نقطة الاستلام',
        help_text='إحداثيات خط الطول لنقطة الاستلام أو مركز التوزيع'
    )
    radius_km = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='نطاق التوصيل بالكيلومتر',
        help_text='نطاق التوصيل بالكيلومتر حول المقر الرئيسي'
    )
    maps_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='رابط الخريطة',
        help_text='رابط مباشر لخرائط جوجل لنقطة الاستلام'
    )
    
    # Organization integration
    base_city = models.ForeignKey(
        'api_organization.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='base_wilayas',
        verbose_name='Base City Organization'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name_ar} ({self.wilaya_code})"
    
    class Meta:
        ordering = ['wilaya_code']
        indexes = [
            models.Index(fields=['wilaya_id']),
            models.Index(fields=['wilaya_code']),
            models.Index(fields=['is_active']),
        ]
    
    def get_available_shipping_methods(self):
        """Get available shipping methods for this wilaya"""
        return ShippingPrice.objects.filter(
            wilaya=self,
            is_active=True,
            shipping_method__is_active=True
        ).select_related('shipping_method')
    
    def get_delivery_price(self, service_type='home', method_id=None):
        """Get price based on service type and optional method"""
        if method_id:
            try:
                price = ShippingPrice.objects.get(
                    wilaya=self,
                    shipping_method_id=method_id,
                    is_active=True
                )
                if service_type == 'home':
                    return price.home_delivery_price
                elif service_type == 'desk':
                    return price.stop_desk_price
                elif service_type == 'express' and price.express_price:
                    return price.express_price
                return price.home_delivery_price
            except ShippingPrice.DoesNotExist:
                return 0
        
        # Get best price for service type
        prices = ShippingPrice.objects.filter(
            wilaya=self,
            is_active=True,
            shipping_method__is_active=True
        ).select_related('shipping_method')
        
        if service_type == 'home':
            return min(p.home_delivery_price for p in prices) if prices else 0
        elif service_type == 'desk':
            return min(p.stop_desk_price for p in prices) if prices else 0
        elif service_type == 'express':
            express_prices = [p.express_price for p in prices if p.express_price]
            return min(express_prices) if express_prices else 0
        
        return 0
    
    def is_free_shipping_eligible(self, order_total, method_id=None):
        """Check if order qualifies for free shipping"""
        if method_id:
            try:
                price = ShippingPrice.objects.get(
                    wilaya=self,
                    shipping_method_id=method_id,
                    is_active=True
                )
                return price.free_shipping_minimum and order_total >= price.free_shipping_minimum
            except ShippingPrice.DoesNotExist:
                return False
        
        # Check any method
        prices = ShippingPrice.objects.filter(
            wilaya=self,
            is_active=True,
            shipping_method__is_active=True,
            free_shipping_minimum__isnull=False
        ).select_related('shipping_method')
        
        return any(
            price.free_shipping_minimum and order_total >= price.free_shipping_minimum
            for price in prices
        )


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('ccp', 'CCP'),
        ('card', 'Credit Card'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    shipping_address = models.TextField()
    wilaya = models.ForeignKey(Shipping, on_delete=models.SET_NULL, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_status = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    sync_status = models.CharField(max_length=20, default='pending')
    erpnext_sales_order_id = models.CharField(max_length=100, blank=True, null=True)
    sync_error = models.TextField(blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number}"

    class Meta:
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, blank=True, null=True)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    dimension_unit = models.CharField(max_length=10, default='cm')
    marble_texture = models.CharField(max_length=100, blank=True, null=True)
    custom_design = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name_ar}"


class OrderTimeline(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='timeline')
    status = models.CharField(max_length=50)
    note = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.order.order_number}"


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    usage_limit = models.IntegerField(blank=True, null=True)
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class CartItem(models.Model):
    DELIVERY_TYPES = [
        ('home', 'Home Delivery'),
        ('stop_desk', 'Stop Desk'),
        ('express', 'Express Delivery'),
    ]
    
    # User association (optional for guest users)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    
    # Product information
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    options = models.JSONField(default=dict, blank=True)
    
    # Custom dimensions for vinyl products
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dimension_unit = models.CharField(max_length=10, default='cm')
    
    # Pricing snapshot (to handle price changes)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    material_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Shipping information
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPES, default='home')
    wilaya = models.ForeignKey('Shipping', on_delete=models.SET_NULL, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Coupon applied
    applied_coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        identifier = self.user.username if self.user else self.session_id
        return f"{identifier} - {self.product.name_ar}"

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_id', 'created_at']),
            models.Index(fields=['product']),
            models.Index(fields=['updated_at']),
        ]
        unique_together = [
            ['user', 'product', 'material', 'width', 'height'],
            ['session_id', 'product', 'material', 'width', 'height']
        ]

    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return (self.unit_price + self.material_price) * self.quantity

    @property
    def total_with_discount(self):
        """Calculate total after discount"""
        subtotal = self.subtotal
        return max(0, subtotal - self.discount_amount - self.coupon_discount)

    @property
    def final_total(self):
        """Calculate final total including shipping"""
        return self.total_with_discount + self.shipping_cost

    @property
    def is_available(self):
        """Check if product is available"""
        return self.product.is_active and self.product.stock >= self.quantity

    @property
    def max_quantity(self):
        """Get maximum quantity available"""
        return self.product.stock

    def calculate_shipping_cost(self, wilaya, delivery_type='home'):
        """Calculate shipping cost based on wilaya and delivery type"""
        if wilaya:
            if delivery_type == 'express' and wilaya.express_delivery_price:
                return wilaya.express_delivery_price
            elif delivery_type == 'stop_desk':
                return wilaya.stop_desk_price
            else:
                return wilaya.home_delivery_price
        return 0

    def apply_coupon(self, coupon):
        """Apply coupon to this cart item"""
        if coupon and coupon.is_active:
            if coupon.discount_type == 'percentage':
                self.coupon_discount = self.subtotal * (coupon.discount_value / 100)
            else:  # fixed amount
                self.coupon_discount = min(coupon.discount_value, self.subtotal)
            self.applied_coupon = coupon
            self.save()

    def update_pricing(self):
        """Update pricing based on current product/material prices"""
        self.unit_price = self.product.base_price
        if self.material:
            # Calculate material price based on dimensions
            if self.width and self.height:
                area_m2 = (self.width * self.height) / 10000  # Convert cm² to m²
                self.material_price = self.material.price_per_m2 * area_m2
            else:
                self.material_price = self.material.price_per_m2
        self.save()

    def merge_with(self, other_cart_item):
        """Merge this cart item with another (for guest cart merging)"""
        self.quantity += other_cart_item.quantity
        self.options.update(other_cart_item.options)
        self.save()


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name_ar}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name_ar} - {self.rating} stars"


class ReviewReport(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.review.id}"


class DesignCategory(models.Model):
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    design_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_ar


class Design(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(DesignCategory, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    likes = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    generated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    # Enhanced notification types covering all business domains
    SENDER_CHOICES = [
        ('system', 'System'),
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('user', 'User'),
    ]
    
    RECIPIENT_CHOICES = [
        ('user', 'Specific User'),
        ('group', 'User Group'),
        ('all', 'All Users'),
        ('role', 'By Role'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    CATEGORY_CHOICES = [
        ('finance', 'Finance'),
        ('inventory', 'Inventory'),
        ('order', 'Order'),
        ('security', 'Security'),
        ('marketing', 'Marketing'),
        ('system', 'System'),
        ('logistics', 'Logistics'),
        ('customer_service', 'Customer Service'),
    ]
    
    TYPE_CHOICES = [
        # Finance
        ('payment_success', 'Payment Successful'),
        ('payment_failed', 'Payment Failed'),
        ('refund_processed', 'Refund Processed'),
        ('ccp_received', 'CCP Transfer Received'),
        ('coupon_applied', 'Coupon Applied'),
        ('coupon_expired', 'Coupon Expired'),
        
        # Orders
        ('order_created', 'Order Created'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_cancelled', 'Order Cancelled'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_returned', 'Order Returned'),
        ('order_modified', 'Order Modified'),
        
        # Inventory
        ('stock_low', 'Low Stock Alert'),
        ('stock_out', 'Out of Stock'),
        ('product_added', 'New Product Added'),
        ('product_updated', 'Product Updated'),
        
        # Security
        ('login_new_device', 'Login from New Device'),
        ('password_changed', 'Password Changed'),
        ('login_failed', 'Failed Login Attempt'),
        ('account_locked', 'Account Locked'),
        
        # Logistics
        ('shipping_confirmed', 'Shipping Confirmed'),
        ('shipping_delayed', 'Shipping Delayed'),
        ('delivery_failed', 'Delivery Failed'),
        ('package_received', 'Package Received at Distribution Center'),
        
        # System
        ('system_maintenance', 'System Maintenance'),
        ('system_update', 'System Update'),
        ('database_backup', 'Database Backup'),
        
        # Marketing
        ('promotion_launched', 'New Promotion'),
        ('newsletter_sent', 'Newsletter Sent'),
        ('campaign_completed', 'Marketing Campaign Completed'),
        
        # Customer Service
        ('support_ticket_created', 'Support Ticket Created'),
        ('support_ticket_resolved', 'Support Ticket Resolved'),
        ('feedback_received', 'Customer Feedback Received'),
    ]

    # Core fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    
    # Enhanced fields
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES, default='system')
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default='user')
    recipient_group = models.CharField(max_length=100, blank=True, null=True)  # For group/role targeting
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='system')
    
    # Metadata and technical fields
    metadata = models.JSONField(default=dict, blank=True, help_text="Technical data like order_id, invoice_id, etc.")
    action_url = models.URLField(blank=True, null=True, help_text="Direct link to related resource")
    action_text = models.CharField(max_length=100, blank=True, null=True)
    
    # Status and timing
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Additional data
    data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username if self.user else 'Broadcast'} - {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def archive(self):
        self.is_archived = True
        self.save(update_fields=['is_archived'])

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['recipient_type', 'priority']),
            models.Index(fields=['category', 'created_at']),
            models.Index(fields=['type', 'created_at']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']


class Alert(models.Model):
    TYPE_CHOICES = [
        ('price', 'Price Alert'),
        ('stock', 'Stock Alert'),
        ('order', 'Order Alert'),
        ('system', 'System Alert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    conditions = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.type}"


class ERPNextSyncLog(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    action = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    message = models.TextField(blank=True, null=True)
    records_synced = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.status}"


class BehaviorTracking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"


class Forecast(models.Model):
    FORECAST_TYPE_CHOICES = [
        ('demand', 'Demand'),
        ('sales', 'Sales'),
        ('inventory', 'Inventory'),
    ]
    
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    forecast_type = models.CharField(max_length=50, choices=FORECAST_TYPE_CHOICES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    predicted_demand = models.IntegerField(blank=True, null=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name_ar} - {self.forecast_type}"


class CustomerSegment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    criteria = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PricingEngine(models.Model):
    raw_material_cost = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=300)
    international_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=200)

    def __str__(self):
        return "Pricing Engine Configuration"


class BlogCategory(models.Model):
    name_ar = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_ar


class BlogPost(models.Model):
    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content_ar = models.TextField()
    content_en = models.TextField()
    summary_ar = models.TextField(blank=True, null=True)
    summary_en = models.TextField(blank=True, null=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    featured_image = models.CharField(max_length=500, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    views = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title_ar


class ConversationHistory(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    session_id = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message = models.TextField()
    source = models.CharField(max_length=50, default='user')
    confidence = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session_id} - {self.role}"


class DashboardSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_settings')
    widgets = models.JSONField(default=list, blank=True)
    layout = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Dashboard Settings"


class WishlistSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist_settings')
    auto_add = models.BooleanField(default=True)
    max_items = models.IntegerField(default=100)
    email_reminders = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Wishlist Settings"
