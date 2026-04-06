"""
Order Serializers for VynilArt API
Note: This project uses GraphQL only, but serializers are kept for compatibility
"""
from rest_framework import serializers
from api.models.order import Order, OrderItem, OrderTimeline, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer"""
    product_name = serializers.CharField(source='product.name_ar', read_only=True)
    material_name = serializers.CharField(source='material.name_ar', read_only=True)
    subtotal = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'product_name', 'material',
            'material_name', 'width', 'height', 'dimension_unit',
            'marble_texture', 'custom_design', 'quantity',
            'unit_price', 'material_price', 'discount_amount',
            'total_price', 'status', 'notes', 'production_notes',
            'created_at', 'updated_at', 'subtotal', 'final_price'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_subtotal(self, obj):
        """Calculate subtotal for this item"""
        return (obj.unit_price + obj.material_price) * obj.quantity
    
    def get_final_price(self, obj):
        """Calculate final price after discount"""
        return self.get_subtotal(obj) - obj.discount_amount


class OrderTimelineSerializer(serializers.ModelSerializer):
    """Order timeline serializer"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = OrderTimeline
        fields = [
            'id', 'order', 'status', 'title', 'note', 'user',
            'user_name', 'location', 'latitude', 'longitude',
            'is_public', 'is_internal', 'attachments', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer"""
    is_successful = serializers.SerializerMethodField()
    can_refund = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'currency', 'method', 'gateway',
            'status', 'transaction_id', 'authorization_code',
            'gateway_response', 'gateway_fee', 'refund_amount',
            'refund_reason', 'refund_date', 'processed_at',
            'completed_at', 'created_at', 'updated_at',
            'is_successful', 'can_refund'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_successful(self, obj):
        """Check if payment was successful"""
        return obj.status == 'completed'
    
    def get_can_refund(self, obj):
        """Check if payment can be refunded"""
        return obj.status == 'completed' and obj.refund_amount < obj.amount


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer"""
    customer_info = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)
    timeline = OrderTimelineSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    is_paid = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    can_track = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'reference_number', 'user',
            'customer_name', 'customer_email', 'customer_phone',
            'shipping_address', 'shipping_wilaya', 'shipping_method',
            'delivery_type', 'subtotal', 'shipping_cost', 'tax',
            'discount_amount', 'coupon_discount', 'total_amount',
            'cod_fee', 'insurance_fee', 'status', 'payment_method',
            'payment_status', 'tracking_number', 'tracking_url',
            'order_date', 'expected_delivery_date', 'shipped_at',
            'delivered_at', 'cancelled_at', 'notes',
            'customer_notes', 'admin_notes', 'metadata',
            'created_at', 'updated_at', 'customer_info',
            'items', 'timeline', 'payments', 'is_paid',
            'can_cancel', 'can_track'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_customer_info(self, obj):
        """Get customer information"""
        return {
            'name': obj.customer_name,
            'email': obj.customer_email,
            'phone': obj.customer_phone,
            'address': obj.shipping_address
        }
    
    def get_is_paid(self, obj):
        """Check if order is paid"""
        return obj.payment_status in ['paid', 'partially_refunded']
    
    def get_can_cancel(self, obj):
        """Check if order can be cancelled"""
        return obj.status in ['pending', 'confirmed']
    
    def get_can_track(self, obj):
        """Check if order can be tracked"""
        return (
            obj.status in ['shipped', 'delivered'] and 
            obj.tracking_number
        )


class OrderCreateSerializer(serializers.ModelSerializer):
    """Order creation serializer"""
    items = OrderItemSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'shipping_address', 'shipping_wilaya', 'shipping_method',
            'delivery_type', 'notes', 'customer_notes', 'items'
        ]
    
    def create(self, validated_data):
        """Create order with items"""
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Order update serializer"""
    class Meta:
        model = Order
        fields = [
            'status', 'tracking_number', 'tracking_url',
            'notes', 'admin_notes'
        ]
    
    def update(self, instance, validated_data):
        """Update order"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
