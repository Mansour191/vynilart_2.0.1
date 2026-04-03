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


class Shipping(models.Model):
    wilaya_id = models.CharField(max_length=10, unique=True)
    name_ar = models.CharField(max_length=255)
    name_fr = models.CharField(max_length=255)
    stop_desk_price = models.DecimalField(max_digits=10, decimal_places=2, default=400)
    home_delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=700)
    is_active = models.BooleanField(default=True)
    regions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_ar


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    options = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name_ar}"


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
    TYPE_CHOICES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


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
