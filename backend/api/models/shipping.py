"""
Shipping Models for VynilArt API
"""
from django.db import models


class ShippingMethod(models.Model):
    """
    Shipping providers and methods
    """
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
        ('pickup', 'Pickup Point'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Provider Name')
    provider = models.CharField(
        max_length=20, 
        choices=PROVIDER_CHOICES, 
        verbose_name='Provider'
    )
    service_type = models.CharField(
        max_length=20, 
        choices=SERVICE_TYPE_CHOICES, 
        verbose_name='Service Type'
    )
    
    # Delivery information
    expected_delivery_time = models.IntegerField(
        verbose_name='Expected Delivery Time (days)'
    )
    delivery_days = models.JSONField(
        default=list,
        help_text="Days of the week when delivery is available"
    )
    cutoff_time = models.TimeField(
        blank=True, 
        null=True,
        help_text="Order cutoff time for same-day delivery"
    )
    
    # Branding and contact
    logo = models.ImageField(
        upload_to='shipping_logos/', 
        null=True, 
        blank=True, 
        verbose_name='Logo'
    )
    description = models.TextField(blank=True, verbose_name='Description')
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    
    # Service level
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    tracking_available = models.BooleanField(default=True)
    insurance_available = models.BooleanField(default=False)
    cod_available = models.BooleanField(default=True)
    
    # Coverage
    coverage_wilayas = models.JSONField(
        default=list,
        help_text="List of covered wilaya codes"
    )
    max_weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Maximum weight per package (kg)"
    )
    max_dimensions = models.JSONField(
        default=dict,
        help_text="Maximum dimensions (length, width, height) in cm"
    )
    
    # API integration
    tracking_url_template = models.URLField(
        blank=True, 
        verbose_name='Tracking URL Template'
    )
    api_endpoint = models.URLField(
        blank=True, 
        verbose_name='API Endpoint'
    )
    api_key = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='API Key'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shipping Method'
        verbose_name_plural = 'Shipping Methods'
        ordering = ['provider', 'service_type']
        indexes = [
            models.Index(fields=['provider', 'service_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['service_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"


class ShippingPrice(models.Model):
    """
    Shipping prices linking wilayas with shipping methods
    """
    wilaya = models.ForeignKey(
        'Shipping', 
        on_delete=models.CASCADE, 
        related_name='shipping_prices'
    )
    shipping_method = models.ForeignKey(
        ShippingMethod, 
        on_delete=models.CASCADE, 
        related_name='prices'
    )
    
    # Pricing for different service types
    home_delivery_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Home Delivery Price'
    )
    stop_desk_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Stop Desk Price'
    )
    express_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Express Price'
    )
    pickup_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Pickup Point Price'
    )
    
    # Additional pricing options
    free_shipping_minimum = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Free Shipping Minimum'
    )
    weight_surcharge = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Weight Surcharge (per kg)'
    )
    volume_surcharge = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Volume Surcharge (per m³)'
    )
    
    # Service level options
    cod_available = models.BooleanField(default=True, verbose_name='COD Available')
    cod_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='COD Fee'
    )
    insurance_available = models.BooleanField(default=False, verbose_name='Insurance Available')
    insurance_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0, 
        help_text="Insurance rate as percentage of declared value"
    )
    tracking_available = models.BooleanField(default=True, verbose_name='Tracking Available')
    
    # Restrictions
    max_weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Maximum weight for this price"
    )
    max_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Maximum declared value for this price"
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    # Validity period
    valid_from = models.DateField(blank=True, null=True)
    valid_to = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def __str__(self):
        return f"{self.wilaya.name_ar} - {self.shipping_method.name}"


class Shipping(models.Model):
    """
    Shipping model matching api_shipping table
    """
    id = models.AutoField(primary_key=True)
    wilaya_id = models.CharField(max_length=10, unique=True)
    name_ar = models.CharField(max_length=255)
    name_fr = models.CharField(max_length=255)
    stop_desk_price = models.DecimalField(max_digits=10, decimal_places=2, default=400)
    home_delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=700)
    is_active = models.BooleanField(default=True)
    regions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_shipping'
        indexes = [
            models.Index(fields=['wilaya_id']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['wilaya_id']

    def __str__(self):
        return f"{self.name_ar} ({self.wilaya_id})"
