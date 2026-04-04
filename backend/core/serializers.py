"""
Serializers for Notification, Cart, and Shipping System
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification, Shipping, ShippingMethod, ShippingPrice, CartItem, Product, Material, Coupon

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model
    """
    
    # Additional fields for API responses
    time_ago = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'type', 'sender', 
            'recipient_type', 'recipient_group', 'priority', 'category',
            'metadata', 'action_url', 'action_text', 'is_read', 
            'is_archived', 'read_at', 'expires_at', 'created_at', 
            'updated_at', 'time_ago', 'priority_display', 
            'category_display', 'type_display'
        ]
        read_only_fields = [
            'id', 'user', 'sender', 'read_at', 'created_at', 'updated_at',
            'time_ago', 'priority_display', 'category_display', 'type_display'
        ]

    def get_time_ago(self, obj):
        """Get human-readable time ago string"""
        from django.utils import timezone
        import math
        
        if not obj.created_at:
            return ''
        
        now = timezone.now()
        diff = now - obj.created_at
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return 'الآن'
        elif seconds < 3600:
            minutes = math.floor(seconds / 60)
            return f'منذ {minutes} دقيقة'
        elif seconds < 86400:
            hours = math.floor(seconds / 3600)
            return f'منذ {hours} ساعة'
        elif seconds < 604800:
            days = math.floor(seconds / 86400)
            return f'منذ {days} يوم'
        else:
            return obj.created_at.strftime('%Y-%m-%d')

    def get_priority_display(self, obj):
        """Get priority display label"""
        labels = {
            'low': 'منخفض',
            'medium': 'متوسط',
            'high': 'عالي',
            'critical': 'حرج'
        }
        return labels.get(obj.priority, obj.priority)

    def get_category_display(self, obj):
        """Get category display label"""
        labels = {
            'finance': 'المالية',
            'inventory': 'المخزون',
            'order': 'الطلبات',
            'security': 'الأمان',
            'marketing': 'التسويق',
            'system': 'النظام',
            'logistics': 'اللوجستيات',
            'customer_service': 'خدمة العملاء'
        }
        return labels.get(obj.category, obj.category)

    def get_type_display(self, obj):
        """Get type display label"""
        labels = {
            'payment_success': 'نجاح الدفع',
            'payment_failed': 'فشل الدفع',
            'refund_processed': 'معالجة الاسترداد',
            'ccp_received': 'استلام تحويل CCP',
            'coupon_applied': 'تطبيق كوبون',
            'coupon_expired': 'انتهاء كوبون',
            'order_created': 'إنشاء طلب',
            'order_confirmed': 'تأكيد طلب',
            'order_cancelled': 'إلغاء طلب',
            'order_shipped': 'شحن طلب',
            'order_delivered': 'تسليم طلب',
            'order_returned': 'إرجاع طلب',
            'order_modified': 'تعديل طلب',
            'stock_low': 'مخزون منخفض',
            'stock_out': 'نفاد المخزون',
            'product_added': 'إضافة منتج',
            'product_updated': 'تحديث منتج',
            'login_new_device': 'تسجيل دخول من جهاز جديد',
            'password_changed': 'تغيير كلمة المرور',
            'login_failed': 'فشل تسجيل الدخول',
            'account_locked': 'قفل الحساب',
            'shipping_confirmed': 'تأكيد الشحن',
            'shipping_delayed': 'تأخير الشحن',
            'delivery_failed': 'فشل التسليم',
            'package_received': 'استلام الطرد',
            'system_maintenance': 'صيانة النظام',
            'system_update': 'تحديث النظام',
            'database_backup': 'نسخ احتياطي',
            'promotion_launched': 'إطلاق ترويج',
            'newsletter_sent': 'إرسال نشرة بريدية',
            'campaign_completed': 'اكتمال الحملة',
            'support_ticket_created': 'إنشاء تذكرة دعم',
            'support_ticket_resolved': 'حل تذكرة الدعم',
            'feedback_received': 'استلام ملاحظات',
            'cart_abandonment': 'إهمال السلة',
            'invoice_generated': 'إنشاء فاتورة',
            'payment_reminder': 'تذكير بالدفع',
            'coupon_expiry_reminder': 'تذكير انتهاء كوبون'
        }
        return labels.get(obj.type, obj.type)

    def validate_priority(self, value):
        """Validate priority field"""
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if value not in valid_priorities:
            raise serializers.ValidationError(f'Priority must be one of: {valid_priorities}')
        return value

    def validate_category(self, value):
        """Validate category field"""
        valid_categories = [
            'finance', 'inventory', 'order', 'security', 
            'marketing', 'system', 'logistics', 'customer_service'
        ]
        if value not in valid_categories:
            raise serializers.ValidationError(f'Category must be one of: {valid_categories}')
        return value

    def validate_recipient_type(self, value):
        """Validate recipient type field"""
        valid_types = ['user', 'group', 'all', 'role']
        if value not in valid_types:
            raise serializers.ValidationError(f'Recipient type must be one of: {valid_types}')
        return value


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for Shipping Method model"""
    
    class Meta:
        model = ShippingMethod
        fields = '__all__'
    
    def get_provider_display(self, obj):
        """Get provider display label"""
        labels = {
            'yalidine': 'Yalidine',
            'zr_express': 'ZR Express',
            'fedex': 'FedEx',
            'dhl': 'DHL',
            'aramex': 'Aramex',
            'local_post': 'Local Post',
            'custom': 'Custom'
        }
        return labels.get(obj.provider, obj.provider)
    
    def get_service_type_display(self, obj):
        """Get service type display label"""
        labels = {
            'home': 'توصيل للمنزل',
            'desk': 'نقطة استلام',
            'express': 'توصيل سريع',
            'economy': 'توصيل اقتصادي'
        }
        return labels.get(obj.service_type, obj.service_type)


class ShippingPriceSerializer(serializers.ModelSerializer):
    """Serializer for Shipping Price model"""
    
    # Include related data
    wilaya = serializers.SerializerMethodField()
    shipping_method = ShippingMethodSerializer(read_only=True)
    
    class Meta:
        model = ShippingPrice
        fields = '__all__'
    
    def get_wilaya(self, obj):
        """Get wilaya information"""
        return {
            'id': obj.wilaya.id,
            'wilaya_id': obj.wilaya.wilaya_id,
            'wilaya_code': obj.wilaya.wilaya_code,
            'name_ar': obj.wilaya.name_ar,
            'name_en': obj.wilaya.name_en,
            'is_active': obj.wilaya.is_active
        }


class ShippingPriceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating shipping prices"""
    
    class Meta:
        model = ShippingPrice
        fields = '__all__'
    
    def validate(self, data):
        """Validate shipping price data"""
        # Ensure at least one price is set
        if not any([data.get('home_delivery_price'), data.get('stop_desk_price')]):
            raise serializers.ValidationError(
                "At least one of home_delivery_price or stop_desk_price must be provided"
            )
        
        # Validate free shipping minimum
        free_shipping_min = data.get('free_shipping_minimum')
        if free_shipping_min and free_shipping_min <= 0:
            raise serializers.ValidationError(
                "Free shipping minimum must be greater than 0"
            )
        
        return data


class ShippingWithPricesSerializer(serializers.ModelSerializer):
    """Enhanced Shipping serializer with available methods and prices"""
    
    available_methods = serializers.SerializerMethodField()
    best_prices = serializers.SerializerMethodField()
    
    class Meta:
        model = Shipping
        fields = '__all__'
    
    def get_available_methods(self, obj):
        """Get all available shipping methods for this wilaya"""
        prices = ShippingPrice.objects.filter(
            wilaya=obj,
            is_active=True,
            shipping_method__is_active=True
        ).select_related('shipping_method')
        
        return ShippingPriceSerializer(prices, many=True).data
    
    def get_best_prices(self, obj):
        """Get best prices per service type"""
        prices = ShippingPrice.objects.filter(
            wilaya=obj,
            is_active=True,
            shipping_method__is_active=True
        ).select_related('shipping_method')
        
        result = {}
        
        # Group by service type and find best price
        for price in prices:
            service_type = price.shipping_method.service_type
            
            if service_type not in result:
                result[service_type] = {
                    'price': float(price.home_delivery_price),
                    'method': ShippingMethodSerializer(price.shipping_method).data
                }
            else:
                current_price = result[service_type]['price']
                if price.home_delivery_price < current_price:
                    result[service_type] = {
                        'price': float(price.home_delivery_price),
                        'method': ShippingMethodSerializer(price.shipping_method).data
                    }
        
        return result


class ShippingMethod
    """Serializer for Shipping model"""
    
    class Meta:
        model = Shipping
        fields = '__all__'
    
    def get_delivery_price(self, obj):
        """Get delivery price based on type"""
        return obj.get_delivery_price()


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model with computed fields"""
    
    # Computed fields
    subtotal = serializers.SerializerMethodField()
    total_with_discount = serializers.SerializerMethodField()
    final_total = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    max_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = '__all__'
        depth = 2  # Include related objects
    
    def get_subtotal(self, obj):
        """Calculate subtotal for this cart item"""
        return float(obj.subtotal)
    
    def get_total_with_discount(self, obj):
        """Calculate total after discount"""
        return float(obj.total_with_discount)
    
    def get_final_total(self, obj):
        """Calculate final total including shipping"""
        return float(obj.final_total)
    
    def get_is_available(self, obj):
        """Check if product is available"""
        return obj.is_available
    
    def get_max_quantity(self, obj):
        """Get maximum quantity available"""
        return obj.max_quantity


class ProductSimpleSerializer(serializers.ModelSerializer):
    """Simple product serializer for cart items"""
    
    class Meta:
        model = Product
        fields = ['id', 'name_ar', 'name_en', 'base_price', 'stock', 'is_active']


class MaterialSimpleSerializer(serializers.ModelSerializer):
    """Simple material serializer for cart items"""
    
    class Meta:
        model = Material
        fields = ['id', 'name_ar', 'name_en', 'price_per_m2']


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model"""
    
    class Meta:
        model = Coupon
        fields = '__all__'


class BroadcastNotificationSerializer(serializers.Serializer):
    """Serializer for admin broadcast notifications"""
    
    recipient_type = serializers.ChoiceField(
        choices=['all', 'group', 'role', 'users'],
        default='all'
    )
    recipient_group = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high', 'critical'],
        default='medium'
    )
    category = serializers.ChoiceField(
        choices=['finance', 'inventory', 'order', 'security', 'marketing', 'system', 'logistics', 'customer_service'],
        default='system'
    )
    action_url = serializers.URLField(required=False, allow_blank=True)
    action_text = serializers.CharField(max_length=100, required=False, allow_blank=True)
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    schedule_at = serializers.DateTimeField(required=False, allow_null=True)


class CartSummarySerializer(serializers.Serializer):
    """Serializer for cart summary"""
    
    total_items = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)


class ShippingCalculationSerializer(serializers.Serializer):
    """Serializer for shipping calculation requests"""
    
    wilaya_id = serializers.CharField()
    delivery_type = serializers.ChoiceField(
        choices=['home', 'stop_desk', 'express'],
        default='home'
    )
    order_weight = serializers.DecimalField(required=False, allow_null=True)
    order_volume = serializers.DecimalField(required=False, allow_null=True)
    order_total = serializers.DecimalField(required=False, allow_null=True)


class BulkUpdateShippingSerializer(serializers.Serializer):
    """Serializer for bulk shipping updates"""
    
    wilaya_ids = serializers.ListField(
        child=serializers.CharField()
    )
    updates = serializers.DictField()
    
    home_delivery_price = serializers.DecimalField(required=False, allow_null=True)
    stop_desk_price = serializers.DecimalField(required=False, allow_null=True)
    express_delivery_price = serializers.DecimalField(required=False, allow_null=True)
    free_shipping_minimum = serializers.DecimalField(required=False, allow_null=True)
    delivery_time_days = serializers.IntegerField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications
    """
    
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="List of user IDs for targeted notifications"
    )
    
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'type', 'sender', 'recipient_type', 
            'recipient_group', 'priority', 'category', 'metadata', 
            'action_url', 'action_text', 'expires_at', 'user_ids'
        ]

    def create(self, validated_data):
        """Create notification with enhanced logic"""
        user_ids = validated_data.pop('user_ids', None)
        recipient_type = validated_data.get('recipient_type', 'user')
        
        if recipient_type == 'all':
            # Create broadcast notification
            notification = Notification.objects.create(**validated_data)
            
            # Create individual notifications for all active users
            from django.contrib.auth import get_user_model
            User = get_user_model()
            users = User.objects.filter(is_active=True)
            
            created_notifications = []
            for user in users:
                user_notification = Notification.objects.create(
                    user=user,
                    **validated_data
                )
                created_notifications.append(user_notification)
            
            return created_notifications[0]  # Return first created notification
            
        elif recipient_type == 'users' and user_ids:
            # Create notifications for specific users
            from django.contrib.auth import get_user_model
            User = get_user_model()
            users = User.objects.filter(id__in=user_ids, is_active=True)
            
            created_notifications = []
            for user in users:
                user_notification = Notification.objects.create(
                    user=user,
                    **validated_data
                )
                created_notifications.append(user_notification)
            
            return created_notifications[0] if created_notifications else None
            
        else:
            # Create single notification
            return super().create(validated_data)


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating notifications
    """
    
    class Meta:
        model = Notification
        fields = ['is_read', 'is_archived', 'read_at']
    
    def update(self, instance, validated_data):
        """Update notification with automatic read_at timestamp"""
        if validated_data.get('is_read') and not instance.is_read:
            validated_data['read_at'] = timezone.now()
        
        return super().update(instance, validated_data)


class NotificationStatsSerializer(serializers.Serializer):
    """
    Serializer for notification statistics
    """
    
    total = serializers.IntegerField()
    unread = serializers.IntegerField()
    read = serializers.IntegerField()
    high_priority = serializers.IntegerField()
    recent = serializers.IntegerField()
    by_category = serializers.ListField(
        child=serializers.DictField()
    )
    by_priority = serializers.ListField(
        child=serializers.DictField()
    )
    by_type = serializers.ListField(
        child=serializers.DictField()
    )


class BroadcastNotificationSerializer(serializers.Serializer):
    """
    Serializer for broadcast notifications
    """
    
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    recipient_type = serializers.ChoiceField(
        choices=['all', 'group', 'role', 'users']
    )
    recipient_group = serializers.CharField(
        required=False,
        allow_blank=True
    )
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high', 'critical'],
        default='medium'
    )
    category = serializers.ChoiceField(
        choices=[
            'finance', 'inventory', 'order', 'security',
            'marketing', 'system', 'logistics', 'customer_service'
        ],
        default='system'
    )
    type = serializers.CharField(
        default='system_update'
    )
    action_url = serializers.URLField(
        required=False,
        allow_blank=True
    )
    action_text = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100
    )
    metadata = serializers.JSONField(
        default=dict,
        required=False
    )
    schedule_at = serializers.DateTimeField(
        required=False,
        allow_null=True
    )
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

    def validate(self, attrs):
        """Validate broadcast notification data"""
        recipient_type = attrs.get('recipient_type')
        recipient_group = attrs.get('recipient_group')
        user_ids = attrs.get('user_ids')
        
        if recipient_type == 'group' and not recipient_group:
            raise serializers.ValidationError(
                'recipient_group is required when recipient_type is "group"'
            )
        
        if recipient_type == 'users' and not user_ids:
            raise serializers.ValidationError(
                'user_ids is required when recipient_type is "users"'
            )
        
        if attrs.get('action_text') and not attrs.get('action_url'):
            raise serializers.ValidationError(
                'action_url is required when action_text is provided'
            )
        
        return attrs


class NotificationPreferenceSerializer(serializers.Serializer):
    """
    Serializer for notification preferences
    """
    
    email_notifications = serializers.BooleanField(default=True)
    push_notifications = serializers.BooleanField(default=True)
    sms_notifications = serializers.BooleanField(default=False)
    categories = serializers.DictField(
        default=dict,
        child=serializers.BooleanField(),
        help_text="Category-wise notification preferences"
    )
    
    def validate_categories(self, value):
        """Validate category preferences"""
        valid_categories = [
            'order', 'finance', 'marketing', 'system', 
            'security', 'logistics', 'inventory', 'customer_service'
        ]
        
        for category in value:
            if category not in valid_categories:
                raise serializers.ValidationError(
                    f'Invalid category: {category}. Valid categories are: {valid_categories}'
                )
        
        return value
