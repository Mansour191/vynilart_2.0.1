"""
System and Integration Models for VynilArt API
"""
from django.db import models
from django.utils import timezone
import json


class Notification(models.Model):
    """
    Enhanced notification system covering all business domains
    """
    # Enhanced sender and recipient choices
    SENDER_CHOICES = [
        ('system', 'System'),
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('user', 'User'),
        ('automated', 'Automated Process'),
    ]
    
    RECIPIENT_CHOICES = [
        ('user', 'Specific User'),
        ('group', 'User Group'),
        ('all', 'All Users'),
        ('role', 'By Role'),
        ('segment', 'Customer Segment'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
        ('urgent', 'Urgent'),
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
        ('wishlist', 'Wishlist'),
        ('alert', 'Alert'),
    ]
    
    TYPE_CHOICES = [
        # Finance notifications
        ('payment_success', 'Payment Successful'),
        ('payment_failed', 'Payment Failed'),
        ('refund_processed', 'Refund Processed'),
        ('ccp_received', 'CCP Transfer Received'),
        ('coupon_applied', 'Coupon Applied'),
        ('coupon_expired', 'Coupon Expired'),
        
        # Order notifications
        ('order_created', 'Order Created'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_cancelled', 'Order Cancelled'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_returned', 'Order Returned'),
        ('order_modified', 'Order Modified'),
        
        # Inventory notifications
        ('stock_low', 'Low Stock Alert'),
        ('stock_out', 'Out of Stock'),
        ('product_added', 'New Product Added'),
        ('product_updated', 'Product Updated'),
        ('price_drop', 'Price Drop'),
        ('back_in_stock', 'Back in Stock'),
        
        # Security notifications
        ('login_new_device', 'Login from New Device'),
        ('password_changed', 'Password Changed'),
        ('login_failed', 'Failed Login Attempt'),
        ('account_locked', 'Account Locked'),
        ('suspicious_activity', 'Suspicious Activity'),
        
        # Logistics notifications
        ('shipping_confirmed', 'Shipping Confirmed'),
        ('shipping_delayed', 'Shipping Delayed'),
        ('delivery_failed', 'Delivery Failed'),
        ('package_received', 'Package Received at Distribution Center'),
        
        # System notifications
        ('system_maintenance', 'System Maintenance'),
        ('system_update', 'System Update'),
        ('database_backup', 'Database Backup'),
        ('api_error', 'API Error'),
        
        # Marketing notifications
        ('promotion_launched', 'New Promotion'),
        ('newsletter_sent', 'Newsletter Sent'),
        ('campaign_completed', 'Marketing Campaign Completed'),
        
        # Customer Service notifications
        ('support_ticket_created', 'Support Ticket Created'),
        ('support_ticket_resolved', 'Support Ticket Resolved'),
        ('feedback_received', 'Customer Feedback Received'),
        
        # Wishlist notifications
        ('wishlist_item_added', 'Item Added to Wishlist'),
        ('wishlist_price_drop', 'Wishlist Item Price Dropped'),
        ('wishlist_back_in_stock', 'Wishlist Item Back in Stock'),
        
        # Alert notifications
        ('alert_triggered', 'Alert Triggered'),
        ('alert_resolved', 'Alert Resolved'),
    ]

    # Core fields
    user = models.ForeignKey(
        'api_user.User', 
        on_delete=models.CASCADE, 
        related_name='notifications', 
        blank=True, 
        null=True
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    
    # Enhanced fields
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES, default='system')
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default='user')
    recipient_group = models.CharField(max_length=100, blank=True, null=True)
    recipient_segment = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='system')
    
    # Metadata and technical fields
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Technical data like order_id, invoice_id, etc."
    )
    action_url = models.URLField(blank=True, null=True, help_text="Direct link to related resource")
    action_text = models.CharField(max_length=100, blank=True, null=True)
    action_button_color = models.CharField(max_length=7, blank=True, null=True)  # Hex color
    
    # Status and timing
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Additional data
    data = models.JSONField(default=dict, blank=True)
    
    # Delivery tracking
    delivery_channels = models.JSONField(
        default=list,
        help_text="List of channels where notification was sent"
    )
    delivery_status = models.JSONField(
        default=dict,
        help_text="Delivery status per channel"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['recipient_type', 'priority']),
            models.Index(fields=['category', 'created_at']),
            models.Index(fields=['type', 'created_at']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_starred']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username if self.user else 'Broadcast'} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def archive(self):
        """Archive notification"""
        self.is_archived = True
        self.save(update_fields=['is_archived'])

    def star(self):
        """Star notification"""
        self.is_starred = True
        self.save(update_fields=['is_starred'])

    def unstar(self):
        """Unstar notification"""
        self.is_starred = False
        self.save(update_fields=['is_starred'])

    def is_expired(self):
        """Check if notification is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def add_delivery_status(self, channel, status, details=None):
        """Add delivery status for a channel"""
        if not self.delivery_status:
            self.delivery_status = {}
        self.delivery_status[channel] = {
            'status': status,
            'timestamp': timezone.now().isoformat(),
            'details': details or {}
        }
        self.save(update_fields=['delivery_status'])


class ERPNextSyncLog(models.Model):
    """
    ERPNext synchronization logs and monitoring
    """
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('partial', 'Partial Success'),
    ]
    
    ENTITY_CHOICES = [
        ('products', 'Products'),
        ('orders', 'Orders'),
        ('customers', 'Customers'),
        ('inventory', 'Inventory'),
        ('invoices', 'Invoices'),
        ('payments', 'Payments'),
        ('all', 'All Entities'),
    ]
    
    # Sync identification
    sync_id = models.CharField(max_length=100, unique=True)
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=50, choices=ENTITY_CHOICES)
    
    # Status and progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    progress_percentage = models.IntegerField(default=0)
    
    # Statistics
    records_total = models.IntegerField(default=0)
    records_synced = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    records_skipped = models.IntegerField(default=0)
    
    # Timing information
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.IntegerField(blank=True, null=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    error_details = models.JSONField(default=dict, blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Data and metadata
    sync_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    
    # Performance metrics
    api_calls_count = models.IntegerField(default=0)
    data_size_bytes = models.IntegerField(blank=True, null=True)
    average_response_time = models.FloatField(blank=True, null=True)
    
    # User and system context
    triggered_by = models.ForeignKey(
        'api_user.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='triggered_syncs'
    )
    system_version = models.CharField(max_length=50, blank=True, null=True)
    api_version = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['sync_id']),
            models.Index(fields=['entity_type']),
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
            models.Index(fields=['triggered_by']),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.action} - {self.status}"

    def mark_completed(self, success=True, error_message=None):
        """Mark sync as completed"""
        self.status = 'completed' if success else 'failed'
        self.completed_at = timezone.now()
        
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        
        if error_message:
            self.error_message = error_message
        
        self.save(update_fields=['status', 'completed_at', 'duration_seconds', 'error_message'])

    def update_progress(self, synced, failed=0, skipped=0):
        """Update sync progress"""
        self.records_synced = synced
        self.records_failed = failed
        self.records_skipped = skipped
        
        if self.records_total > 0:
            self.progress_percentage = int((synced / self.records_total) * 100)
        
        self.save(update_fields=['records_synced', 'records_failed', 'records_skipped', 'progress_percentage'])

    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
        self.save(update_fields=['retry_count'])

    def can_retry(self):
        """Check if sync can be retried"""
        return self.retry_count < self.max_retries and self.status == 'failed'


class SystemConfiguration(models.Model):
    """
    System-wide configuration settings
    """
    CONFIG_TYPES = [
        ('general', 'General'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('payment', 'Payment'),
        ('shipping', 'Shipping'),
        ('security', 'Security'),
        ('backup', 'Backup'),
        ('api', 'API'),
        ('ai', 'AI Services'),
    ]
    
    key = models.CharField(max_length=255)
    value = models.TextField()
    config_type = models.CharField(max_length=50, choices=CONFIG_TYPES)
    
    # Validation and constraints
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('float', 'Float'),
            ('boolean', 'Boolean'),
            ('json', 'JSON'),
            ('email', 'Email'),
            ('url', 'URL'),
        ],
        default='string'
    )
    is_required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True, null=True)
    
    # Validation rules
    min_value = models.FloatField(blank=True, null=True)
    max_value = models.FloatField(blank=True, null=True)
    allowed_values = models.JSONField(default=list, blank=True)
    validation_regex = models.CharField(max_length=500, blank=True, null=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=True)
    requires_restart = models.BooleanField(default=False)
    
    # Organization and environment
    organization = models.ForeignKey(
        'api_organization.Organization',
        on_delete=models.CASCADE,
        related_name='configurations'
    )
    environment = models.CharField(
        max_length=20,
        choices=[
            ('development', 'Development'),
            ('staging', 'Staging'),
            ('production', 'Production'),
        ],
        default='production'
    )
    
    # Audit trail
    created_by = models.ForeignKey(
        'api_user.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_configs'
    )
    updated_by = models.ForeignKey(
        'api_user.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='updated_configs'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['config_type']),
            models.Index(fields=['organization']),
            models.Index(fields=['environment']),
            models.Index(fields=['is_public']),
        ]
        unique_together = ['key', 'organization', 'environment']

    def __str__(self):
        return f"{self.key} - {self.organization.name}"

    def validate_value(self, value):
        """Validate a value against configuration rules"""
        # Type validation
        if self.data_type == 'integer':
            try:
                value = int(value)
            except ValueError:
                return False, "Must be an integer"
        elif self.data_type == 'float':
            try:
                value = float(value)
            except ValueError:
                return False, "Must be a number"
        elif self.data_type == 'boolean':
            if isinstance(value, str):
                return value.lower() in ['true', 'false', '1', '0']
            return isinstance(value, bool)
        elif self.data_type == 'json':
            try:
                json.loads(value)
            except json.JSONDecodeError:
                return False, "Must be valid JSON"
        
        # Range validation
        if self.min_value is not None and float(value) < self.min_value:
            return False, f"Must be at least {self.min_value}"
        
        if self.max_value is not None and float(value) > self.max_value:
            return False, f"Must be at most {self.max_value}"
        
        # Allowed values validation
        if self.allowed_values and value not in self.allowed_values:
            return False, f"Must be one of: {', '.join(map(str, self.allowed_values))}"
        
        return True, "Valid"

    def get_typed_value(self):
        """Get value in the correct data type"""
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'float':
            return float(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.data_type == 'json':
            return json.loads(self.value)
        else:
            return self.value


class BehaviorTracking(models.Model):
    """User behavior tracking for analytics"""
    user = models.ForeignKey('api.User', on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['target_type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']


class SystemForecast(models.Model):
    """Sales and inventory forecasting"""
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

    product = models.ForeignKey('api.Product', on_delete=models.CASCADE)
    forecast_type = models.CharField(max_length=50, choices=FORECAST_TYPE_CHOICES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    predicted_demand = models.IntegerField(blank=True, null=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name_ar} - {self.forecast_type}"

    class Meta:
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['forecast_type']),
            models.Index(fields=['period']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']


class SystemCustomerSegment(models.Model):
    """Customer segmentation for marketing"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    criteria = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
        ]
        ordering = ['name']


class SystemPricingEngine(models.Model):
    """Pricing configuration and rules"""
    raw_material_cost = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=300)
    international_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=200)

    def __str__(self):
        return "Pricing Engine Configuration"

    class Meta:
        verbose_name = 'Pricing Engine'
        verbose_name_plural = 'Pricing Engines'


class SystemConversationHistory(models.Model):
    """Chat conversation history"""
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

    class Meta:
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['role']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['session_id', 'created_at']


class SystemDashboardSettings(models.Model):
    """User dashboard customization settings"""
    user = models.OneToOneField('api.User', on_delete=models.CASCADE, related_name='dashboard_settings')
    widgets = models.JSONField(default=list, blank=True)
    layout = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Dashboard Settings"

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]


class SystemWishlistSettings(models.Model):
    """User wishlist preferences"""
    user = models.OneToOneField('api.User', on_delete=models.CASCADE, related_name='wishlist_settings')
    auto_add = models.BooleanField(default=True)
    max_items = models.IntegerField(default=100)
    email_reminders = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Wishlist Settings"

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]
