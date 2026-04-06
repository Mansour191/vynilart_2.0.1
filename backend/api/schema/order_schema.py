"""
Order Schema for VynilArt API
"""
import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Float, Boolean, DateTime, ID, JSONString
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Sum, Count, Avg
from decimal import Decimal
from api.models.order import Order, OrderItem, OrderTimeline, Payment
from api.models.shipping import Shipping


class OrderType(DjangoObjectType):
    """Enhanced order type"""
    id = graphene.ID(required=True)
    order_number = String()
    reference_number = String()
    
    # Customer information
    user = Field(lambda: UserType)
    customer_name = String()
    customer_email = String()
    customer_phone = String()
    
    # Shipping information
    shipping_address = String()
    shipping_wilaya = Field(lambda: ShippingType)
    shipping_method = Field(lambda: ShippingMethodType)
    delivery_type = String()
    
    # Financial information
    subtotal = Float()
    shipping_cost = Float()
    tax = Float()
    discount_amount = Float()
    coupon_discount = Float()
    total_amount = Float()
    
    # Additional charges
    cod_fee = Float()
    insurance_fee = Float()
    
    # Status and workflow
    status = String()
    payment_method = String()
    payment_status = String()
    is_paid = Boolean()
    
    # Tracking
    tracking_number = String()
    tracking_url = String()
    
    # Dates
    order_date = graphene.Date()
    expected_delivery_date = graphene.Date()
    shipped_at = DateTime()
    delivered_at = DateTime()
    cancelled_at = DateTime()
    
    # Relations
    items = List(lambda: OrderItemType)
    payments = List(lambda: PaymentType)
    timeline = List(lambda: OrderTimelineType)
    
    # Computed fields
    can_cancel = Boolean()
    can_track = Boolean()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Order
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order_number': ['exact', 'icontains'],
            'status': ['exact'],
            'payment_status': ['exact'],
            'user': ['exact'],
            'shipping_wilaya': ['exact'],
            'payment_method': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'order_date': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_paid(self, info):
        """Check if order is paid"""
        return self.payment_status in ['paid', 'partially_refunded']

    def resolve_can_cancel(self, info):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed']

    def resolve_can_track(self, info):
        """Check if order can be tracked"""
        return (
            self.status in ['shipped', 'delivered'] and 
            self.tracking_number
        )


class OrderItemType(DjangoObjectType):
    """Order item type"""
    id = graphene.ID(required=True)
    order = Field(OrderType)
    product = Field(lambda: ProductType)
    product_snapshot = JSONString()
    
    # Material and customization
    material = Field(lambda: MaterialType)
    material_snapshot = JSONString()
    width = Float()
    height = Float()
    dimension_unit = String()
    marble_texture = String()
    custom_design = String()
    
    # Pricing
    quantity = Int()
    unit_price = Float()
    material_price = Float()
    discount_amount = Float()
    total_price = Float()
    final_price = Float()
    
    # Status
    status = String()
    
    # Notes
    notes = String()
    production_notes = String()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = OrderItem
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order': ['exact'],
            'product': ['exact'],
            'material': ['exact'],
            'status': ['exact'],
        }

    def resolve_subtotal(self, info):
        """Calculate subtotal for this item"""
        return (self.unit_price + self.material_price) * self.quantity

    def resolve_final_price(self, info):
        """Calculate final price after discount"""
        return self.subtotal - self.discount_amount


class OrderTimelineType(DjangoObjectType):
    """Order timeline type"""
    id = graphene.ID(required=True)
    order = Field(OrderType)
    status = String()
    title = String()
    note = String()
    
    # User tracking
    user = Field(lambda: UserType)
    
    # Location tracking
    location = String()
    latitude = Float()
    longitude = Float()
    
    # Visibility
    is_public = Boolean()
    is_internal = Boolean()
    
    # Attachments
    attachments = List(String)
    
    timestamp = DateTime()

    class Meta:
        model = OrderTimeline
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order': ['exact'],
            'status': ['exact'],
            'is_public': ['exact'],
            'timestamp': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }


class PaymentType(DjangoObjectType):
    """Payment type"""
    id = graphene.ID(required=True)
    order = Field(OrderType)
    
    # Payment details
    amount = Float()
    currency = String()
    method = String()
    gateway = String()
    
    # Status and tracking
    status = String()
    transaction_id = String()
    authorization_code = String()
    
    # Gateway response
    gateway_response = JSONString()
    gateway_fee = Float()
    
    # Refund information
    refund_amount = Float()
    refund_reason = String()
    refund_date = DateTime()
    
    # Dates
    processed_at = DateTime()
    completed_at = DateTime()
    
    created_at = DateTime()
    updated_at = DateTime()

    class Meta:
        model = Payment
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order': ['exact'],
            'status': ['exact'],
            'gateway': ['exact'],
            'transaction_id': ['exact'],
            'created_at': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }

    def resolve_is_successful(self, info):
        """Check if payment was successful"""
        return self.status == 'completed'

    def resolve_can_refund(self, info):
        """Check if payment can be refunded"""
        return self.status == 'completed' and self.refund_amount < self.amount


# Input Types
class OrderInput(graphene.InputObjectType):
    """Input for order creation"""
    customer_name = String(required=True)
    customer_email = String()
    customer_phone = String(required=True)
    shipping_address = String(required=True)
    shipping_wilaya_id = ID()
    shipping_method_id = ID()
    delivery_type = String()
    notes = String()
    customer_notes = String()


class OrderItemInput(graphene.InputObjectType):
    """Input for order item"""
    product_id = ID(required=True)
    material_id = ID()
    width = Float(required=True)
    height = Float(required=True)
    dimension_unit = String(default_value='cm')
    marble_texture = String()
    custom_design = String()
    quantity = Int(default_value=1)


class PaymentInput(graphene.InputObjectType):
    """Input for payment processing"""
    order_id = ID(required=True)
    amount = Float()
    method = String()
    gateway = String()
    transaction_id = String()
    gateway_response = JSONString()


# Mutations
class CreateOrder(Mutation):
    """Create a new order"""
    
    class Arguments:
        input = OrderInput(required=True)
        items = List(OrderItemInput, required=True)

    success = Boolean()
    message = String()
    order = Field(OrderType)
    errors = List(String)

    def mutate(self, info, input, items):
        try:
            from api.models.order import Order, OrderItem
            from api.models.product import Product, Material
            from api.models.shipping import Shipping, ShippingMethod
            
            user = info.context.user
            
            # Get shipping info
            shipping_wilaya = None
            if 'shipping_wilaya_id' in input:
                shipping_wilaya = Shipping.objects.get(id=input['shipping_wilaya_id'])
            
            shipping_method = None
            if 'shipping_method_id' in input:
                shipping_method = ShippingMethod.objects.get(id=input['shipping_method_id'])
            
            # Create order
            order = Order.objects.create(
                order_number=Order.generate_order_number(),
                user=user if user.is_authenticated else None,
                customer_name=input.customer_name,
                customer_email=input.customer_email,
                customer_phone=input.customer_phone,
                shipping_address=input.shipping_address,
                shipping_wilaya=shipping_wilaya,
                shipping_method=shipping_method,
                delivery_type=input.get('delivery_type', 'home'),
                notes=input.notes,
                customer_notes=input.customer_notes
            )
            
            # Create order items
            total_amount = 0
            for item_data in items:
                product = Product.objects.get(id=item_data['product_id'])
                material = None
                if 'material_id' in item_data:
                    material = Material.objects.get(id=item_data['material_id'])
                
                # Calculate pricing
                unit_price = product.base_price
                material_price = material.price_per_m2 if material else 0
                
                # Calculate material price based on dimensions
                if material and item_data.get('width') and item_data.get('height'):
                    area_m2 = (item_data['width'] * item_data['height']) / 10000
                    material_price = material.price_per_m2 * area_m2
                
                item_total = (unit_price + material_price) * item_data['quantity']
                total_amount += item_total
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    material=material,
                    width=item_data['width'],
                    height=item_data['height'],
                    dimension_unit=item_data.get('dimension_unit', 'cm'),
                    marble_texture=item_data.get('marble_texture'),
                    custom_design=item_data.get('custom_design'),
                    quantity=item_data['quantity'],
                    unit_price=unit_price,
                    material_price=material_price,
                    total_price=item_total
                )
            
            # Update order totals
            order.subtotal = total_amount
            order.total_amount = total_amount
            order.save()
            
            return CreateOrder(
                success=True,
                message="Order created successfully",
                order=order
            )
            
        except Exception as e:
            return CreateOrder(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class UpdateOrderStatus(Mutation):
    """Update order status"""
    
    class Arguments:
        order_id = ID(required=True)
        status = String(required=True)
        note = String()
        tracking_number = String()
        
    success = Boolean()
    message = String()
    order = Field(OrderType)
    errors = List(String)

    def mutate(self, info, order_id, status, note=None, tracking_number=None):
        try:
            order = Order.objects.get(id=order_id)
            
            # Update status
            order.status = status
            
            # Add status to timeline
            OrderTimeline.objects.create(
                order=order,
                status=status,
                title=f"Order {status}",
                note=note,
                user=info.context.user
            )
            
            # Update tracking if provided
            if tracking_number:
                order.tracking_number = tracking_number
            
            # Update timestamps based on status
            if status == 'shipped':
                order.shipped_at = timezone.now()
            elif status == 'delivered':
                order.delivered_at = timezone.now()
            elif status == 'cancelled':
                order.cancelled_at = timezone.now()
            
            order.save()
            
            return UpdateOrderStatus(
                success=True,
                message="Order status updated successfully",
                order=order
            )
            
        except Order.DoesNotExist:
            return UpdateOrderStatus(
                success=False,
                message="Order not found",
                errors=["Order not found"]
            )
        except Exception as e:
            return UpdateOrderStatus(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


class CancelOrder(Mutation):
    """Cancel an order"""
    
    class Arguments:
        order_id = ID(required=True)
        reason = String()

    success = Boolean()
    message = String()
    order = Field(OrderType)
    errors = List(String)

    def mutate(self, info, order_id, reason=None):
        try:
            order = Order.objects.get(id=order_id)
            
            if not order.can_cancel:
                return CancelOrder(
                    success=False,
                    message="Order cannot be cancelled",
                    errors=["Order cannot be cancelled"]
                )
            
            order.cancel(reason)
            
            return CancelOrder(
                success=True,
                message="Order cancelled successfully",
                order=order
            )
            
        except Order.DoesNotExist:
            return CancelOrder(
                success=False,
                message="Order not found",
                errors=["Order not found"]
            )
        except Exception as e:
            return CancelOrder(
                success=False,
                message=str(e),
                errors=[str(e)]
            )


# Query Class
class OrderQuery(ObjectType):
    """Order queries"""
    
    orders = List(OrderType)
    order = Field(OrderType, id=ID(required=True))
    orders_connection = DjangoFilterConnectionField(OrderType)
    my_orders = List(OrderType)
    
    def resolve_orders(self, info):
        """Get all orders (admin only)"""
        user = info.context.user
        if user.is_authenticated and user.is_staff:
            return Order.objects.all()
        return []
    
    def resolve_order(self, info, id):
        """Get order by ID"""
        user = info.context.user
        try:
            order = Order.objects.get(id=id)
            # Check if user can access this order
            if user.is_authenticated and (
                user.is_staff or 
                order.user == user
            ):
                return order
            return None
        except Order.DoesNotExist:
            return None


# Node Classes from core/schema.py
class ShippingNode(DjangoObjectType):
    """Shipping node with enhanced filtering"""
    class Meta:
        model = models.Shipping
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'is_active': ['exact'],
            'home_delivery_price': ['lt', 'lte', 'gt', 'gte'],
            'stop_desk_price': ['lt', 'lte', 'gt', 'gte'],
        }


class OrderNode(DjangoObjectType, IsAuthenticatedMixin):
    """Enhanced order node with relationships"""
    user = Field('UserNode')
    items = List('OrderItemNode')
    payments = List('PaymentNode')
    shipping = Field('ShippingNode')
    
    class Meta:
        model = models.Order
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order_number': ['exact', 'icontains'],
            'status': ['exact'],
            'user': ['exact'],
            'created_at': ['lt', 'lte', 'gt', 'gte'],
        }


class OrderItemNode(DjangoObjectType):
    """Order item node with product details"""
    product = Field('ProductNode')
    material = Field('MaterialNode')
    
    class Meta:
        model = models.OrderItem
        interfaces = (relay.Node,)
        fields = '__all__'


class OrderTimelineNode(DjangoObjectType):
    """Order timeline node for tracking"""
    class Meta:
        model = models.OrderTimeline
        interfaces = (relay.Node,)
        fields = '__all__'


class PaymentNode(DjangoObjectType):
    """Payment node with enhanced filtering"""
    class Meta:
        model = models.Payment
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order': ['exact'],
            'status': ['exact'],
            'payment_method': ['exact'],
            'amount': ['lt', 'lte', 'gt', 'gte'],
        }
    
    def resolve_my_orders(self, info):
        """Get current user's orders"""
        user = info.context.user
        if user.is_authenticated:
            return Order.objects.filter(user=user)
        return []


# Mutation Class
class OrderMutation(ObjectType):
    """Order mutations"""
    
    create_order = CreateOrder.Field()
    update_order_status = UpdateOrderStatus.Field()
    cancel_order = CancelOrder.Field()
