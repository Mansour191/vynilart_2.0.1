"""
Order Models for VynilArt API
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Order(models.Model):
    """
    Order model matching api_order table
    """
    id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='orders',
        db_column='user_id'
    )
    customer_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    shipping_address = models.TextField()
    wilaya_id = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        db_column='wilaya_id'
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    payment_method = models.CharField(max_length=20, default='cod')
    payment_status = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    sync_status = models.CharField(max_length=20, default='pending')
    erpnext_sales_order_id = models.CharField(max_length=100, blank=True, null=True)
    sync_error = models.TextField(blank=True, null=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_order'
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['wilaya_id']),
            models.Index(fields=['payment_method']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    """
    Order items matching api_orderitem table
    """
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        db_column='order_id'
    )
    product = models.ForeignKey(
        'product.Product', 
        on_delete=models.CASCADE,
        db_column='product_id'
    )
    material = models.ForeignKey(
        'product.Material', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        db_column='material_id'
    )
    width = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    dimension_unit = models.CharField(max_length=10, default='cm')
    marble_texture = models.CharField(max_length=100, blank=True, null=True)
    custom_design = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_orderitem'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
            models.Index(fields=['material']),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name_ar}"


class OrderTimeline(models.Model):
    """
    Order timeline matching api_ordertimeline table
    """
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='timeline',
        db_column='order_id'
    )
    status = models.CharField(max_length=50)
    note = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        db_column='user_id'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_ordertimeline'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['status']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class Payment(models.Model):
    """
    Payment model matching api_payment table
    """
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='payments',
        db_column='order_id'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_payment'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - {self.order.order_number}"


class Coupon(models.Model):
    """
    Coupon model matching api_coupon table
    """
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, default='percentage')
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

    class Meta:
        db_table = 'api_coupon'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['valid_from']),
            models.Index(fields=['valid_to']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Coupon {self.code}"
