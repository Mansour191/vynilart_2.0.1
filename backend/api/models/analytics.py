"""
Analytics and Business Intelligence Models for VynilArt API
"""
from django.db import models
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from decimal import Decimal


class DemandForecast(models.Model):
    """
    Demand and sales forecasting
    """
    FORECAST_TYPE_CHOICES = [
        ('demand', 'Demand'),
        ('sales', 'Sales'),
        ('inventory', 'Inventory'),
        ('revenue', 'Revenue'),
    ]
    
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    MODEL_CHOICES = [
        ('linear', 'Linear Regression'),
        ('arima', 'ARIMA'),
        ('prophet', 'Prophet'),
        ('lstm', 'LSTM Neural Network'),
        ('ensemble', 'Ensemble Model'),
    ]
    
    # Target and scope
    product = models.ForeignKey(
        'api_product.Product', 
        on_delete=models.CASCADE,
        related_name='forecasts'
    )
    category = models.ForeignKey(
        'api_product.Category',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='forecasts'
    )
    
    # Forecast specifications
    forecast_type = models.CharField(max_length=50, choices=FORECAST_TYPE_CHOICES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    model_used = models.CharField(max_length=50, choices=MODEL_CHOICES)
    
    # Time range
    start_date = models.DateField()
    end_date = models.DateField()
    forecast_date = models.DateField()
    
    # Forecast values
    predicted_value = models.DecimalField(max_digits=15, decimal_places=2)
    confidence_interval_lower = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    confidence_interval_upper = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # Accuracy metrics (after the fact)
    actual_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    mae = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Mean Absolute Error
    mape = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Mean Absolute Percentage Error
    
    # Metadata
    model_parameters = models.JSONField(default=dict, blank=True)
    training_data_points = models.IntegerField(blank=True, null=True)
    seasonal_adjustment = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['category']),
            models.Index(fields=['forecast_type']),
            models.Index(fields=['period']),
            models.Index(fields=['forecast_date']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        unique_together = ['product', 'forecast_type', 'period', 'start_date']

    def __str__(self):
        return f"{self.product.name_ar} - {self.forecast_type}"

    @property
    def accuracy_percentage(self):
        """Calculate accuracy percentage if actual value exists"""
        if self.actual_value is None or self.predicted_value == 0:
            return None
        return max(0, 100 - abs((self.actual_value - self.predicted_value) / self.predicted_value * 100))

    def calculate_accuracy(self, actual_value):
        """Calculate and update accuracy metrics"""
        self.actual_value = actual_value
        if self.predicted_value != 0:
            self.mae = abs(self.actual_value - self.predicted_value)
            self.mape = abs((self.actual_value - self.predicted_value) / self.predicted_value * 100)
        self.save(update_fields=['actual_value', 'mae', 'mape'])


class CustomerSegment(models.Model):
    """
    Customer segmentation for marketing and personalization
    """
    SEGMENT_TYPE_CHOICES = [
        ('demographic', 'Demographic'),
        ('behavioral', 'Behavioral'),
        ('geographic', 'Geographic'),
        ('psychographic', 'Psychographic'),
        ('value_based', 'Value-Based'),
        ('rfm', 'RFM Analysis'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    segment_type = models.CharField(max_length=50, choices=SEGMENT_TYPE_CHOICES)
    
    # Segment criteria
    criteria = models.JSONField(
        default=dict,
        help_text="Segmentation rules and criteria"
    )
    
    # Segment characteristics
    size = models.IntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Performance metrics
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_frequency = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    churn_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # Marketing effectiveness
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    response_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    # Status and lifecycle
    is_active = models.BooleanField(default=True)
    auto_update = models.BooleanField(default=False)
    last_updated = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['segment_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['size']),
            models.Index(fields=['percentage']),
        ]

    def __str__(self):
        return self.name

    def calculate_size(self):
        """Calculate segment size based on criteria"""
        from api_user.models import User
        
        # This would implement the actual filtering logic
        # based on the criteria JSON
        users = User.objects.all()  # Apply criteria here
        self.size = users.count()
        total_users = User.objects.count()
        self.percentage = (self.size / total_users * 100) if total_users > 0 else 0
        self.save(update_fields=['size', 'percentage', 'last_updated'])

    def update_metrics(self):
        """Update performance metrics for this segment"""
        from api_order.models import Order
        
        # Get users in this segment
        # This would apply the segment criteria to get users
        segment_users = []  # Apply criteria here
        
        if segment_users:
            orders = Order.objects.filter(user__in=segment_users)
            
            # Calculate metrics
            self.avg_order_value = orders.aggregate(
                avg=Avg('total_amount')
            )['avg'] or 0
            
            # Calculate other metrics...
            self.save(update_fields=[
                'avg_order_value', 'order_frequency', 
                'lifetime_value', 'conversion_rate'
            ])


class PricingEngine(models.Model):
    """
    Dynamic pricing engine configuration
    """
    # Base costs
    raw_material_cost = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=300)
    international_shipping = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    
    # Overhead and profit
    overhead_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=25)
    
    # Dynamic pricing factors
    demand_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    competition_factor = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    seasonality_factor = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    inventory_factor = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    
    # AI pricing settings
    ai_pricing_enabled = models.BooleanField(default=False)
    ai_model_confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0.8)
    min_confidence_for_pricing = models.DecimalField(max_digits=5, decimal_places=2, default=0.7)
    
    # Price ranges and limits
    min_price_margin = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    max_price_increase = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    
    # Regional pricing
    regional_pricing_enabled = models.BooleanField(default=False)
    regional_multipliers = models.JSONField(
        default=dict,
        help_text="Price multipliers by region/wilaya"
    )
    
    # Customer segmentation pricing
    customer_segment_pricing = models.BooleanField(default=False)
    segment_multipliers = models.JSONField(
        default=dict,
        help_text="Price multipliers by customer segment"
    )
    
    # Time-based pricing
    time_based_pricing = models.BooleanField(default=False)
    hour_multipliers = models.JSONField(
        default=dict,
        help_text="Price multipliers by hour of day"
    )
    day_multipliers = models.JSONField(
        default=dict,
        help_text="Price multipliers by day of week"
    )
    
    # Update frequency
    auto_update_frequency = models.IntegerField(
        default=24,
        help_text="Hours between automatic pricing updates"
    )
    last_update = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Pricing Engine Configuration"

    def calculate_base_price(self, material_cost=0, labor_hours=1):
        """Calculate base price from costs"""
        total_cost = (
            self.raw_material_cost + 
            material_cost + 
            (self.labor_cost * labor_hours)
        )
        
        # Add overhead
        total_cost *= (1 + self.overhead_percentage / 100)
        
        # Add profit margin
        base_price = total_cost * (1 + self.profit_margin / 100)
        
        return base_price

    def apply_dynamic_factors(self, base_price, product=None, customer=None, region=None):
        """Apply dynamic pricing factors"""
        adjusted_price = base_price
        
        # Apply demand multiplier
        adjusted_price *= self.demand_multiplier
        
        # Apply competition factor
        adjusted_price *= self.competition_factor
        
        # Apply seasonality factor
        adjusted_price *= self.seasonality_factor
        
        # Apply inventory factor
        adjusted_price *= self.inventory_factor
        
        # Apply regional pricing
        if self.regional_pricing_enabled and region:
            regional_multiplier = self.regional_multipliers.get(region, 1.0)
            adjusted_price *= regional_multiplier
        
        # Apply customer segment pricing
        if self.customer_segment_pricing and customer:
            # This would determine customer's segment
            segment_multiplier = self.segment_multipliers.get('default', 1.0)
            adjusted_price *= segment_multiplier
        
        # Apply time-based pricing
        if self.time_based_pricing:
            current_hour = timezone.now().hour
            current_day = timezone.now().weekday()
            
            hour_multiplier = self.hour_multipliers.get(str(current_hour), 1.0)
            day_multiplier = self.day_multipliers.get(str(current_day), 1.0)
            adjusted_price *= hour_multiplier * day_multiplier
        
        return adjusted_price

    def validate_price(self, final_price, base_price):
        """Validate final price against constraints"""
        min_price = base_price * (1 + self.min_price_margin / 100)
        max_price = base_price * (1 + self.max_price_increase / 100)
        
        return max(min_price, min(final_price, max_price))


class DashboardSettings(models.Model):
    """
    User-specific dashboard configuration
    """
    user = models.OneToOneField(
        'api_user.User', 
        on_delete=models.CASCADE, 
        related_name='dashboard_settings'
    )
    
    # Layout configuration
    layout = models.JSONField(
        default=dict,
        help_text="Dashboard layout configuration"
    )
    
    # Widget configuration
    widgets = models.JSONField(
        default=list,
        help_text="List of dashboard widgets and their settings"
    )
    
    # Preferences
    preferences = models.JSONField(
        default=dict,
        help_text="User preferences like theme, language, etc."
    )
    
    # Data filters
    default_date_range = models.CharField(
        max_length=20,
        choices=[
            ('7d', 'Last 7 Days'),
            ('30d', 'Last 30 Days'),
            ('90d', 'Last 90 Days'),
            ('1y', 'Last Year'),
            ('all', 'All Time'),
        ],
        default='30d'
    )
    
    default_wilaya = models.CharField(max_length=10, blank=True, null=True)
    default_category = models.ForeignKey(
        'api_product.Category',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    
    # Notification settings
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ('realtime', 'Real-time'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        default='realtime'
    )
    
    # Privacy settings
    share_analytics = models.BooleanField(default=False)
    public_dashboard = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} Dashboard Settings"

    def add_widget(self, widget_type, position=None, settings=None):
        """Add a widget to dashboard"""
        widget = {
            'id': f"widget_{len(self.widgets) + 1}",
            'type': widget_type,
            'position': position or {'x': 0, 'y': 0, 'w': 4, 'h': 4},
            'settings': settings or {},
            'visible': True
        }
        self.widgets.append(widget)
        self.save(update_fields=['widgets'])

    def remove_widget(self, widget_id):
        """Remove a widget from dashboard"""
        self.widgets = [w for w in self.widgets if w['id'] != widget_id]
        self.save(update_fields=['widgets'])

    def update_layout(self, layout_config):
        """Update dashboard layout"""
        self.layout.update(layout_config)
        self.save(update_fields=['layout'])
