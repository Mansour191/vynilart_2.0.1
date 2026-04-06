"""
Analytics Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Count, Avg, Sum
from decimal import Decimal


class ForecastType(DjangoObjectType):
    """Forecast type"""
    id = graphene.ID(required=True)
    product = Field(lambda: ProductType)
    category = Field(lambda: CategoryType)
    
    # Forecast specifications
    forecast_type = String()
    period = String()
    model_used = String()
    
    # Time range
    start_date = graphene.Date()
    end_date = graphene.Date()
    forecast_date = graphene.Date()
    
    # Forecast values
    predicted_value = Float()
    confidence_interval_lower = Float()
    confidence_interval_upper = Float()
    confidence = Float()
    
    # Accuracy metrics
    actual_value = Float()
    mae = Float()
    mape = Float()
    
    # Computed fields
    accuracy_percentage = Float()
    
    # Metadata
    model_parameters = JSONString()
    training_data_points = Int()
    seasonal_adjustment = Boolean()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Forecast
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'product': ['exact'],
            'category': ['exact'],
            'forecast_type': ['exact'],
            'period': ['exact'],
            'model_used': ['exact'],
            'start_date': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'end_date': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_accuracy_percentage(self, info):
        """Calculate accuracy percentage if actual value exists"""
        if self.actual_value is None or self.predicted_value == 0:
            return None
        return max(0, 100 - abs((self.actual_value - self.predicted_value) / self.predicted_value * 100))


class CustomerSegmentType(DjangoObjectType):
    """Customer segment type"""
    id = graphene.ID(required=True)
    name = String()
    description = String()
    segment_type = String()
    
    # Segment criteria
    criteria = JSONString()
    
    # Segment characteristics
    size = Int()
    percentage = Float()
    
    # Performance metrics
    avg_order_value = Float()
    order_frequency = Float()
    lifetime_value = Float()
    churn_rate = Float()
    
    # Marketing effectiveness
    conversion_rate = Float()
    engagement_rate = Float()
    response_rate = Float()
    
    # Status and lifecycle
    is_active = Boolean()
    auto_update = Boolean()
    last_updated = DateTime()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = CustomerSegment
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'segment_type': ['exact'],
            'is_active': ['exact'],
            'size': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'percentage': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }


class PricingEngineType(DjangoObjectType):
    """Pricing engine type"""
    id = graphene.ID(required=True)
    
    # Base costs
    raw_material_cost = Float()
    labor_cost = Float()
    international_shipping = Float()
    
    # Overhead and profit
    overhead_percentage = Float()
    profit_margin = Float()
    
    # Dynamic pricing factors
    demand_multiplier = Float()
    competition_factor = Float()
    seasonality_factor = Float()
    inventory_factor = Float()
    
    # AI pricing settings
    ai_pricing_enabled = Boolean()
    ai_model_confidence = Float()
    min_confidence_for_pricing = Float()
    
    # Price ranges and limits
    min_price_margin = Float()
    max_price_increase = Float()
    
    # Regional pricing
    regional_pricing_enabled = Boolean()
    regional_multipliers = JSONString()
    
    # Customer segmentation pricing
    customer_segment_pricing = Boolean()
    segment_multipliers = JSONString()
    
    # Time-based pricing
    time_based_pricing = Boolean()
    hour_multipliers = JSONString()
    day_multipliers = JSONString()
    
    # Update frequency
    auto_update_frequency = Int()
    last_update = DateTime()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = PricingEngine
        interfaces = (relay.Node,)
        fields = '__all__'


class DashboardSettingsType(DjangoObjectType):
    """Dashboard settings type"""
    id = graphene.ID(required=True)
    user = Field(lambda: UserType)
    
    # Layout configuration
    layout = JSONString()
    
    # Widget configuration
    widgets = JSONString()
    
    # Preferences
    preferences = JSONString()
    
    # Data filters
    default_date_range = String()
    default_wilaya = String()
    default_category = Field(lambda: CategoryType)
    
    # Notification settings
    email_notifications = Boolean()
    push_notifications = Boolean()
    notification_frequency = String()
    
    # Privacy settings
    share_analytics = Boolean()
    public_dashboard = Boolean()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = DashboardSettings
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'default_date_range': ['exact'],
            'notification_frequency': ['exact'],
        }


# Input Types
class ForecastInput(graphene.InputObjectType):
    """Input for forecast creation and updates"""
    product_id = ID()
    category_id = ID()
    forecast_type = String(required=True)
    period = String(required=True)
    model_used = String(required=True)
    
    # Time range
    start_date = graphene.Date(required=True)
    end_date = graphene.Date(required=True)
    forecast_date = graphene.Date(required=True)
    
    # Forecast values
    predicted_value = Float(required=True)
    confidence_interval_lower = Float()
    confidence_interval_upper = Float()
    confidence = Float()
    
    # Metadata
    model_parameters = JSONString()
    training_data_points = Int()
    seasonal_adjustment = Boolean(default_value=False)


class CustomerSegmentInput(graphene.InputObjectType):
    """Input for customer segment creation and updates"""
    name = String(required=True)
    description = String()
    segment_type = String(required=True)
    criteria = JSONString(required=True)
    
    # Performance metrics
    avg_order_value = Float()
    order_frequency = Float()
    lifetime_value = Float()
    churn_rate = Float()
    
    # Marketing effectiveness
    conversion_rate = Float()
    engagement_rate = Float()
    response_rate = Float()
    
    # Status and lifecycle
    is_active = Boolean(default_value=True)
    auto_update = Boolean(default_value=False)


class PricingEngineInput(graphene.InputObjectType):
    """Input for pricing engine configuration"""
    # Base costs
    raw_material_cost = Float()
    labor_cost = Float()
    international_shipping = Float()
    
    # Overhead and profit
    overhead_percentage = Float()
    profit_margin = Float()
    
    # Dynamic pricing factors
    demand_multiplier = Float()
    competition_factor = Float()
    seasonality_factor = Float()
    inventory_factor = Float()
    
    # AI pricing settings
    ai_pricing_enabled = Boolean()
    ai_model_confidence = Float()
    min_confidence_for_pricing = Float()
    
    # Price ranges and limits
    min_price_margin = Float()
    max_price_increase = Float()
    
    # Regional pricing
    regional_pricing_enabled = Boolean()
    regional_multipliers = JSONString()
    
    # Customer segmentation pricing
    customer_segment_pricing = Boolean()
    segment_multipliers = JSONString()
    
    # Time-based pricing
    time_based_pricing = Boolean()
    hour_multipliers = JSONString()
    day_multipliers = JSONString()
    
    # Update frequency
    auto_update_frequency = Int()


class DashboardSettingsInput(graphene.InputObjectType):
    """Input for dashboard settings"""
    layout = JSONString()
    widgets = JSONString()
    preferences = JSONString()
    
    # Data filters
    default_date_range = String()
    default_wilaya_id = ID()
    default_category_id = ID()
    
    # Notification settings
    email_notifications = Boolean()
    push_notifications = Boolean()
    notification_frequency = String()
    
    # Privacy settings
    share_analytics = Boolean()
    public_dashboard = Boolean()


# Mutations
class CreateForecast(Mutation):
    """Create a new forecast"""
    
    class Arguments:
        input = ForecastInput(required=True)

    success = Boolean()
    message = String()
    forecast = Field(ForecastType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.analytics import Forecast
            from api.models.product import Product, Category
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return CreateForecast(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            # Handle product and category
            product = None
            if 'product_id' in input:
                product = Product.objects.get(id=input['product_id'])
            
            category = None
            if 'category_id' in input:
                category = Category.objects.get(id=input['category_id'])
            
            forecast = Forecast.objects.create(
                product=product,
                category=category,
                **{k: v for k, v in input.items() if k not in ['product_id', 'category_id']}
            )
            
            return CreateForecast(
                success=True,
                message="Forecast created successfully",
                forecast=forecast
            )
            
        except Exception as e:
            return CreateForecast(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateForecast(Mutation):
    """Update an existing forecast"""
    
    class Arguments:
        id = ID(required=True)
        input = ForecastInput(required=True)

    success = Boolean()
    message = String()
    forecast = Field(ForecastType)
    errors = List(String)

    def mutate(self, info, id, input):
        try:
            from api.models.analytics import Forecast
            from api.models.product import Product, Category
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return UpdateForecast(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            forecast = Forecast.objects.get(id=id)
            
            # Handle product and category
            if 'product_id' in input:
                forecast.product = Product.objects.get(id=input['product_id'])
            
            if 'category_id' in input:
                forecast.category = Category.objects.get(id=input['category_id'])
            
            # Update fields
            for field, value in input.items():
                if field not in ['product_id', 'category_id'] and hasattr(forecast, field):
                    setattr(forecast, field, value)
            
            forecast.save()
            
            return UpdateForecast(
                success=True,
                message="Forecast updated successfully",
                forecast=forecast
            )
            
        except Forecast.DoesNotExist:
            return UpdateForecast(
                success=False,
                message="Forecast not found",
                errors=["Forecast not found"]
            )
        except Exception as e:
            return UpdateForecast(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CreateCustomerSegment(Mutation):
    """Create a new customer segment"""
    
    class Arguments:
        input = CustomerSegmentInput(required=True)

    success = Boolean()
    message = String()
    segment = Field(CustomerSegmentType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.analytics import CustomerSegment
            
            user = info.context.user
            
            if not user.is_authenticated or not user.is_staff:
                return CreateCustomerSegment(
                    success=False,
                    message="Admin authentication required",
                    errors=["Admin authentication required"]
                )
            
            segment = CustomerSegment.objects.create(**input)
            
            # Calculate segment size
            segment.calculate_size()
            
            return CreateCustomerSegment(
                success=True,
                message="Customer segment created successfully",
                segment=segment
            )
            
        except Exception as e:
            return CreateCustomerSegment(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateDashboardSettings(Mutation):
    """Update dashboard settings"""
    
    class Arguments:
        input = DashboardSettingsInput(required=True)

    success = Boolean()
    message = String()
    dashboard_settings = Field(DashboardSettingsType)
    errors = List(String)

    def mutate(self, info, input):
        try:
            from api.models.analytics import DashboardSettings
            from api.models.product import Category
            
            user = info.context.user
            
            if not user.is_authenticated:
                return UpdateDashboardSettings(
                    success=False,
                    message="Authentication required",
                    errors=["Authentication required"]
                )
            
            dashboard_settings, created = DashboardSettings.objects.get_or_create(user=user)
            
            # Handle category
            if 'default_category_id' in input:
                dashboard_settings.default_category = Category.objects.get(id=input['default_category_id'])
            
            # Update fields
            for field, value in input.items():
                if field != 'default_category_id' and hasattr(dashboard_settings, field):
                    setattr(dashboard_settings, field, value)
            
            dashboard_settings.save()
            
            return UpdateDashboardSettings(
                success=True,
                message="Dashboard settings updated successfully",
                dashboard_settings=dashboard_settings
            )
            
        except Exception as e:
            return UpdateDashboardSettings(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class AnalyticsQuery(ObjectType):
    """Analytics queries"""
    
    # Forecast queries
    forecasts = List(ForecastType)
    forecast = Field(ForecastType, id=ID(required=True))
    product_forecasts = List(ForecastType, product_id=ID(required=True))
    
    # Customer segment queries
    customer_segments = List(CustomerSegmentType)
    customer_segment = Field(CustomerSegmentType, id=ID(required=True))
    
    # Pricing engine queries
    pricing_engine = Field(PricingEngineType)
    
    # Dashboard settings queries
    my_dashboard_settings = Field(DashboardSettingsType)
    
    def resolve_forecasts(self, info):
        """Get all forecasts (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return Forecast.objects.all()
        return []
    
    def resolve_forecast(self, info, id):
        """Get forecast by ID"""
        user = info.context.user
        try:
            forecast = Forecast.objects.get(id=id)
            if user.is_authenticated and user.is_staff:
                return forecast
            return None
        except Forecast.DoesNotExist:
            return None
    
    def resolve_product_forecasts(self, info, product_id):
        """Get forecasts for specific product"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return Forecast.objects.filter(product_id=product_id)
        return []
    
    def resolve_customer_segments(self, info):
        """Get all customer segments (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return CustomerSegment.objects.all()
        return []
    
    def resolve_customer_segment(self, info, id):
        """Get customer segment by ID"""
        user = info.context.user
        try:
            segment = CustomerSegment.objects.get(id=id)
            if user.is_authenticated and user.is_staff:
                return segment
            return None
        except CustomerSegment.DoesNotExist:
            return None
    
    def resolve_pricing_engine(self, info):
        """Get pricing engine configuration (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            try:
                return PricingEngine.objects.first()
            except PricingEngine.DoesNotExist:
                return None
        return None
    
    def resolve_my_dashboard_settings(self, info):
        """Get current user's dashboard settings"""
        user = info.context.user
        if user.is_authenticated:
            try:
                return user.dashboard_settings
            except DashboardSettings.DoesNotExist:
                return None
        return None


# Mutation Class
class AnalyticsMutation(ObjectType):
    """Analytics mutations"""
    
    create_forecast = CreateForecast.Field()
    update_forecast = UpdateForecast.Field()
    create_customer_segment = CreateCustomerSegment.Field()
    update_dashboard_settings = UpdateDashboardSettings.Field()
