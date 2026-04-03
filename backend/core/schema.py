from graphene import relay, ObjectType, Schema, Mutation, Field, List, String, Int, Float, Boolean, DateTime, JSONString, ID
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from . import models

User = get_user_model()


# Authentication and Permission Mixins
class IsAuthenticatedMixin:
    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_authenticated:
            return queryset
        return queryset.none()


class IsStaffMixin:
    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return queryset
        return queryset.none()


class UserNode(DjangoObjectType):
    class Meta:
        model = models.User
        interfaces = (relay.Node,)
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')


class UserProfileNode(DjangoObjectType):
    class Meta:
        model = models.UserProfile
        interfaces = (relay.Node,)
        fields = '__all__'


class CategoryNode(DjangoObjectType):
    class Meta:
        model = models.Category
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
        }


class MaterialNode(DjangoObjectType):
    class Meta:
        model = models.Material
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'is_active': ['exact'],
            'is_premium': ['exact'],
        }


class ProductNode(DjangoObjectType):
    images = List('ProductImageNode')
    variants = List('ProductVariantNode')
    category = Field('CategoryNode')
    
    class Meta:
        model = models.Product
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
            'is_featured': ['exact'],
            'is_new': ['exact'],
            'on_sale': ['exact'],
            'category': ['exact'],
            'base_price': ['lt', 'lte', 'gt', 'gte'],
        }


class ProductImageNode(DjangoObjectType):
    class Meta:
        model = models.ProductImage
        interfaces = (relay.Node,)
        fields = '__all__'


class ProductVariantNode(DjangoObjectType):
    class Meta:
        model = models.ProductVariant
        interfaces = (relay.Node,)
        fields = '__all__'


class ShippingNode(DjangoObjectType):
    class Meta:
        model = models.Shipping
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'wilaya_id': ['exact'],
            'name_ar': ['exact', 'icontains'],
            'is_active': ['exact'],
        }


class OrderNode(DjangoObjectType, IsAuthenticatedMixin):
    user = Field(UserNode)
    items = List('OrderItemNode')
    payments = List('PaymentNode')
    timeline = List('OrderTimelineNode')
    wilaya = Field('ShippingNode')
    
    class Meta:
        model = models.Order
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'order_number': ['exact', 'icontains'],
            'status': ['exact'],
            'payment_method': ['exact'],
            'payment_status': ['exact'],
            'user': ['exact'],
        }


class OrderItemNode(DjangoObjectType):
    class Meta:
        model = models.OrderItem
        interfaces = (relay.Node,)
        fields = '__all__'


class OrderTimelineNode(DjangoObjectType):
    class Meta:
        model = models.OrderTimeline
        interfaces = (relay.Node,)
        fields = '__all__'


class PaymentNode(DjangoObjectType):
    class Meta:
        model = models.Payment
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'status': ['exact'],
            'method': ['exact'],
            'order': ['exact'],
        }


class CouponNode(DjangoObjectType):
    class Meta:
        model = models.Coupon
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'code': ['exact'],
            'is_active': ['exact'],
        }


class CartItemNode(DjangoObjectType, IsAuthenticatedMixin):
    user = Field(UserNode)
    product = Field('ProductNode')
    material = Field('MaterialNode')
    
    class Meta:
        model = models.CartItem
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'product': ['exact'],
        }


class WishlistNode(DjangoObjectType, IsAuthenticatedMixin):
    user = Field(UserNode)
    product = Field('ProductNode')
    
    class Meta:
        model = models.Wishlist
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
        }


class ReviewNode(DjangoObjectType):
    user = Field(UserNode)
    product = Field('ProductNode')
    
    class Meta:
        model = models.Review
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'rating': ['exact', 'gte', 'lte'],
            'is_verified': ['exact'],
            'product': ['exact'],
            'user': ['exact'],
        }


class ReviewReportNode(DjangoObjectType):
    class Meta:
        model = models.ReviewReport
        interfaces = (relay.Node,)
        fields = '__all__'


class DesignCategoryNode(DjangoObjectType):
    class Meta:
        model = models.DesignCategory
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_active': ['exact'],
        }


class DesignNode(DjangoObjectType):
    class Meta:
        model = models.Design
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name': ['exact', 'icontains'],
            'status': ['exact'],
            'is_featured': ['exact'],
            'is_active': ['exact'],
            'category': ['exact'],
        }


class NotificationNode(DjangoObjectType):
    class Meta:
        model = models.Notification
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'type': ['exact'],
            'is_read': ['exact'],
            'user': ['exact'],
        }


class AlertNode(DjangoObjectType):
    class Meta:
        model = models.Alert
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'type': ['exact'],
            'is_active': ['exact'],
            'user': ['exact'],
        }


class ERPNextSyncLogNode(DjangoObjectType):
    class Meta:
        model = models.ERPNextSyncLog
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'action': ['exact', 'icontains'],
            'status': ['exact'],
        }


class BehaviorTrackingNode(DjangoObjectType):
    class Meta:
        model = models.BehaviorTracking
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'action': ['exact', 'icontains'],
            'target_type': ['exact'],
            'user': ['exact'],
        }


class ForecastNode(DjangoObjectType):
    class Meta:
        model = models.Forecast
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'forecast_type': ['exact'],
            'period': ['exact'],
            'product': ['exact'],
        }


class CustomerSegmentNode(DjangoObjectType):
    class Meta:
        model = models.CustomerSegment
        interfaces = (relay.Node,)
        fields = '__all__'


class PricingEngineNode(DjangoObjectType):
    class Meta:
        model = models.PricingEngine
        interfaces = (relay.Node,)
        fields = '__all__'


class BlogCategoryNode(DjangoObjectType):
    class Meta:
        model = models.BlogCategory
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'name_ar': ['exact', 'icontains'],
            'name_en': ['exact', 'icontains'],
            'slug': ['exact'],
        }


class BlogPostNode(DjangoObjectType):
    class Meta:
        model = models.BlogPost
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'title_ar': ['exact', 'icontains'],
            'title_en': ['exact', 'icontains'],
            'slug': ['exact'],
            'is_published': ['exact'],
            'category': ['exact'],
            'author': ['exact'],
        }


class ConversationHistoryNode(DjangoObjectType):
    class Meta:
        model = models.ConversationHistory
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'session_id': ['exact'],
            'role': ['exact'],
            'source': ['exact'],
        }


class DashboardSettingsNode(DjangoObjectType):
    class Meta:
        model = models.DashboardSettings
        interfaces = (relay.Node,)
        fields = '__all__'


class WishlistSettingsNode(DjangoObjectType):
    class Meta:
        model = models.WishlistSettings
        interfaces = (relay.Node,)
        fields = '__all__'


# Enhanced Mutations with Authentication and Permissions

# Input Types
class ProductInput(graphene.InputObjectType):
    name_ar = String(required=True)
    name_en = String(required=True)
    slug = String(required=True)
    description_ar = String()
    description_en = String()
    base_price = Float(required=True)
    cost = Float()
    category_id = Int()
    on_sale = Boolean()
    discount_percent = Int()
    is_featured = Boolean()
    is_new = Boolean()
    is_active = Boolean()
    stock = Int()
    weight = Float()
    dimensions = String()
    tags = List(String)
    seo_title = String()
    seo_description = String()


class OrderInput(graphene.InputObjectType):
    customer_name = String(required=True)
    phone = String(required=True)
    email = String()
    shipping_address = String(required=True)
    wilaya_id = String()
    payment_method = String()
    notes = String()
    items = List(lambda: OrderItemInput)


class OrderItemInput(graphene.InputObjectType):
    product_id = Int(required=True)
    material_id = Int()
    width = Float(required=True)
    height = Float(required=True)
    dimension_unit = String()
    marble_texture = String()
    custom_design = String()
    quantity = Int(default_value=1)


class PaymentInput(graphene.InputObjectType):
    order_id = Int(required=True)
    amount = Float(required=True)
    method = String(required=True)
    transaction_id = String()


class ReviewInput(graphene.InputObjectType):
    product_id = Int(required=True)
    rating = Int(required=True)
    comment = String()


class CreateCategory(Mutation):
    class Arguments:
        name_ar = String(required=True)
        name_en = String(required=True)
        slug = String(required=True)
        description = String()
        icon = String()
        waste_percent = Float()
        image = String()
        parent_id = Int()

    category = Field(CategoryNode)
    success = Boolean()
    message = String()

    def mutate(self, info, name_ar, name_en, slug, **kwargs):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return CreateCategory(success=False, message="Authentication and staff privileges required")
        
        try:
            category = models.Category.objects.create(
                name_ar=name_ar,
                name_en=name_en,
                slug=slug,
                **kwargs
            )
            return CreateCategory(category=category, success=True, message="Category created successfully")
        except Exception as e:
            return CreateCategory(success=False, message=str(e))


class CreateProduct(Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = Field(ProductNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            return CreateProduct(success=False, message="Authentication and staff privileges required")
        
        try:
            category = None
            if input.category_id:
                category = models.Category.objects.get(id=input.category_id)
            
            product = models.Product.objects.create(
                name_ar=input.name_ar,
                name_en=input.name_en,
                slug=input.slug,
                description_ar=input.description_ar,
                description_en=input.description_en,
                base_price=input.base_price,
                cost=input.cost or 0,
                category=category,
                on_sale=input.on_sale or False,
                discount_percent=input.discount_percent or 0,
                is_featured=input.is_featured or False,
                is_new=input.is_new or True,
                is_active=input.is_active or True,
                stock=input.stock or 0,
                weight=input.weight,
                dimensions=input.dimensions,
                tags=input.tags or [],
                seo_title=input.seo_title,
                seo_description=input.seo_description
            )
            
            return CreateProduct(product=product, success=True, message="Product created successfully")
        except Exception as e:
            return CreateProduct(success=False, message=str(e))


class CreateOrder(Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = Field(OrderNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            return CreateOrder(success=False, message="Authentication required")
        
        try:
            import uuid
            order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            wilaya = None
            if input.wilaya_id:
                wilaya = models.Shipping.objects.get(wilaya_id=input.wilaya_id)
            
            # Calculate totals
            subtotal = 0
            order_items = []
            
            for item_input in input.items:
                product = models.Product.objects.get(id=item_input.product_id)
                material = None
                if item_input.material_id:
                    material = models.Material.objects.get(id=item_input.material_id)
                
                # Calculate item price (simplified)
                item_price = product.base_price * item_input.quantity
                if material:
                    item_price += material.price_per_m2 * (item_input.width * item_input.height / 10000)  # Convert to m2
                
                subtotal += item_price
                order_items.append((product, material, item_input, item_price))
            
            # Calculate shipping and tax (simplified)
            shipping_cost = wilaya.home_delivery_price if wilaya else 0
            tax = subtotal * 0.19  # 19% tax
            total_amount = subtotal + shipping_cost + tax
            
            # Create order
            order = models.Order.objects.create(
                order_number=order_number,
                user=info.context.user,
                customer_name=input.customer_name,
                phone=input.phone,
                email=input.email,
                shipping_address=input.shipping_address,
                wilaya=wilaya,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax=tax,
                total_amount=total_amount,
                payment_method=input.payment_method or 'cod',
                notes=input.notes
            )
            
            # Create order items
            for product, material, item_input, item_price in order_items:
                models.OrderItem.objects.create(
                    order=order,
                    product=product,
                    material=material,
                    width=item_input.width,
                    height=item_input.height,
                    dimension_unit=item_input.dimension_unit or 'cm',
                    marble_texture=item_input.marble_texture,
                    custom_design=item_input.custom_design,
                    quantity=item_input.quantity,
                    price=item_price
                )
            
            return CreateOrder(order=order, success=True, message="Order created successfully")
        except Exception as e:
            return CreateOrder(success=False, message=str(e))


class ProcessPayment(Mutation):
    class Arguments:
        input = PaymentInput(required=True)

    payment = Field(PaymentNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            return ProcessPayment(success=False, message="Authentication required")
        
        try:
            order = models.Order.objects.get(id=input.order_id)
            
            # Verify user owns the order or is staff
            if order.user != info.context.user and not info.context.user.is_staff:
                return ProcessPayment(success=False, message="Permission denied")
            
            # Create payment record
            payment = models.Payment.objects.create(
                order=order,
                amount=input.amount,
                method=input.method,
                status='completed',  # Simplified - in real app, this would be 'pending' then updated
                transaction_id=input.transaction_id
            )
            
            # Update order payment status
            if payment.amount >= order.total_amount:
                order.payment_status = True
                order.status = 'confirmed'
                order.save()
            
            return ProcessPayment(payment=payment, success=True, message="Payment processed successfully")
        except Exception as e:
            return ProcessPayment(success=False, message=str(e))


class AddToCart(Mutation):
    class Arguments:
        product_id = Int(required=True)
        material_id = Int()
        quantity = Int(default_value=1)
        options = JSONString()

    cart_item = Field(CartItemNode)
    success = Boolean()
    message = String()

    def mutate(self, info, product_id, material_id=None, quantity=1, options=None):
        if not info.context.user.is_authenticated:
            return AddToCart(success=False, message="Authentication required")
        
        try:
            product = models.Product.objects.get(id=product_id)
            material = None
            if material_id:
                material = models.Material.objects.get(id=material_id)
            
            cart_item, created = models.CartItem.objects.get_or_create(
                user=info.context.user,
                product=product,
                material=material,
                defaults={
                    'quantity': quantity,
                    'options': options or {}
                }
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return AddToCart(cart_item=cart_item, success=True, message="Added to cart")
        except Exception as e:
            return AddToCart(success=False, message=str(e))


class AddToWishlist(Mutation):
    class Arguments:
        product_id = Int(required=True)

    wishlist_item = Field(WishlistNode)
    success = Boolean()
    message = String()

    def mutate(self, info, product_id):
        if not info.context.user.is_authenticated:
            return AddToWishlist(success=False, message="Authentication required")
        
        try:
            product = models.Product.objects.get(id=product_id)
            
            wishlist_item, created = models.Wishlist.objects.get_or_create(
                user=info.context.user,
                product=product
            )
            
            if created:
                return AddToWishlist(wishlist_item=wishlist_item, success=True, message="Added to wishlist")
            else:
                return AddToWishlist(success=False, message="Already in wishlist")
        except Exception as e:
            return AddToWishlist(success=False, message=str(e))


class CreateReview(Mutation):
    class Arguments:
        input = ReviewInput(required=True)

    review = Field(ReviewNode)
    success = Boolean()
    message = String()

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            return CreateReview(success=False, message="Authentication required")
        
        try:
            product = models.Product.objects.get(id=input.product_id)
            
            # Check if user already reviewed this product
            if models.Review.objects.filter(user=info.context.user, product=product).exists():
                return CreateReview(success=False, message="You have already reviewed this product")
            
            review = models.Review.objects.create(
                user=info.context.user,
                product=product,
                rating=input.rating,
                comment=input.comment
            )
            
            return CreateReview(review=review, success=True, message="Review created successfully")
        except Exception as e:
            return CreateReview(success=False, message=str(e))


class Mutation(ObjectType):
    # Product mutations (Staff only)
    create_category = CreateCategory.Field()
    create_product = CreateProduct.Field()
    
    # Order and Payment mutations (Financial operations)
    create_order = CreateOrder.Field()
    process_payment = ProcessPayment.Field()
    
    # User interactions
    add_to_cart = AddToCart.Field()
    add_to_wishlist = AddToWishlist.Field()
    create_review = CreateReview.Field()


# Enhanced Query with Vinyls and Investors focus
class Query(ObjectType):
    hello = String(name=String(default_value="World"))

    # Node interface for relay
    node = relay.Node.Field()

    # User related
    me = Field(UserNode)
    my_profile = Field(UserProfileNode)
    my_orders = List(OrderNode)
    my_cart = List(CartItemNode)
    my_wishlist = List(WishlistNode)

    # Products (Vinyls) - Main focus
    products = DjangoFilterConnectionField(ProductNode)
    product = relay.Node.Field(ProductNode)
    featured_products = List(ProductNode)
    new_products = List(ProductNode)
    sale_products = List(ProductNode)
    search_products = List(ProductNode, query=String())

    # Categories and Materials
    categories = DjangoFilterConnectionField(CategoryNode)
    materials = DjangoFilterConnectionField(MaterialNode)

    # Orders (Financial operations)
    orders = DjangoFilterConnectionField(OrderNode)
    order = relay.Node.Field(OrderNode)
    order_by_number = Field(OrderNode, order_number=String())

    # Users (Investors) - Staff only
    users = List(UserNode)
    user = relay.Node.Field(UserNode)
    investors = List(UserNode)  # Alias for users with specific permissions

    # Other entities
    shipping_options = DjangoFilterConnectionField(ShippingNode)
    reviews = DjangoFilterConnectionField(ReviewNode)
    designs = DjangoFilterConnectionField(DesignNode)
    blog_posts = DjangoFilterConnectionField(BlogPostNode)
    notifications = DjangoFilterConnectionField(NotificationNode)
    
    # Categories and Materials (Expanded)
    category = relay.Node.Field(CategoryNode)
    material = relay.Node.Field(MaterialNode)
    
    # Orders and Payments (Expanded)
    payment = relay.Node.Field(PaymentNode)
    order_timeline = List(OrderTimelineNode, orderId=ID())
    
    # Cart and Wishlist (Expanded)
    cart_item = relay.Node.Field(CartItemNode)
    wishlist_item = relay.Node.Field(WishlistNode)
    
    # Reviews and Reports
    review = relay.Node.Field(ReviewNode)
    review_reports = List(ReviewReportNode, reviewId=ID())
    
    # Designs and Categories
    design = relay.Node.Field(DesignNode)
    design_category = relay.Node.Field(DesignCategoryNode)
    design_categories = DjangoFilterConnectionField(DesignCategoryNode)
    
    # Blog and Content
    blog_post = relay.Node.Field(BlogPostNode)
    blog_category = relay.Node.Field(BlogCategoryNode)
    blog_categories = DjangoFilterConnectionField(BlogCategoryNode)
    
    # Notifications and Alerts
    notification = relay.Node.Field(NotificationNode)
    alerts = DjangoFilterConnectionField(AlertNode)
    alert = relay.Node.Field(AlertNode)
    
    # System and Analytics
    erp_sync_logs = DjangoFilterConnectionField(ERPNextSyncLogNode)
    behavior_tracking = DjangoFilterConnectionField(BehaviorTrackingNode)
    forecasts = DjangoFilterConnectionField(ForecastNode)
    customer_segments = List(CustomerSegmentNode)
    pricing_engine = Field(PricingEngineNode)
    
    # Conversations and AI
    conversation_history = List(ConversationHistoryNode, sessionId=String())
    
    # Dashboard and Settings
    dashboard_settings = Field(DashboardSettingsNode)
    wishlist_settings = Field(WishlistSettingsNode)
    
    # Coupons and Discounts
    coupons = DjangoFilterConnectionField(CouponNode)
    coupon = relay.Node.Field(CouponNode)
    validate_coupon = Field(CouponNode, code=String())

    def resolve_hello(self, info, name):
        return f'Hello {name}!'

    def resolve_me(self, info):
        if info.context.user.is_authenticated:
            return info.context.user
        return None

    def resolve_my_profile(self, info):
        if info.context.user.is_authenticated:
            try:
                return info.context.user.profile
            except models.UserProfile.DoesNotExist:
                return None
        return None

    def resolve_my_orders(self, info):
        if info.context.user.is_authenticated:
            return models.Order.objects.filter(user=info.context.user)
        return []

    def resolve_my_cart(self, info):
        if info.context.user.is_authenticated:
            return models.CartItem.objects.filter(user=info.context.user)
        return []

    def resolve_my_wishlist(self, info):
        if info.context.user.is_authenticated:
            return models.Wishlist.objects.filter(user=info.context.user)
        return []

    def resolve_products(self, info, **kwargs):
        return models.Product.objects.filter(is_active=True)

    def resolve_featured_products(self, info):
        return models.Product.objects.filter(is_featured=True, is_active=True)[:10]

    def resolve_new_products(self, info):
        return models.Product.objects.filter(is_new=True, is_active=True)[:10]

    def resolve_sale_products(self, info):
        return models.Product.objects.filter(on_sale=True, is_active=True)[:10]

    def resolve_search_products(self, info, query=None):
        if not query:
            return models.Product.objects.none()
        
        return models.Product.objects.filter(
            is_active=True
        ).filter(
            models.Q(name_ar__icontains=query) |
            models.Q(name_en__icontains=query) |
            models.Q(description_ar__icontains=query) |
            models.Q(description_en__icontains=query) |
            models.Q(tags__contains=[query])
        )

    def resolve_orders(self, info, **kwargs):
        if info.context.user.is_authenticated:
            if info.context.user.is_staff:
                return models.Order.objects.all()
            else:
                return models.Order.objects.filter(user=info.context.user)
        return models.Order.objects.none()

    def resolve_order_by_number(self, info, order_number):
        if info.context.user.is_authenticated:
            try:
                order = models.Order.objects.get(order_number=order_number)
                # Check permissions
                if order.user == info.context.user or info.context.user.is_staff:
                    return order
            except models.Order.DoesNotExist:
                return None
        return None

    def resolve_users(self, info):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return User.objects.filter(is_active=True)
        return []

    def resolve_investors(self, info):
        """Query for investors - users with specific permissions or groups"""
        if info.context.user.is_authenticated and info.context.user.is_staff:
            # You can customize this logic based on your investor definition
            # For example, users in 'investors' group or with specific permissions
            return User.objects.filter(
                is_active=True,
                groups__name__in=['investors']  # Assuming you have an 'investors' group
            ).distinct()
        return []
    
    def resolve_category(self, info, id=None, slug=None):
        if id:
            try:
                return models.Category.objects.get(id=id, is_active=True)
            except models.Category.DoesNotExist:
                return None
        elif slug:
            try:
                return models.Category.objects.get(slug=slug, is_active=True)
            except models.Category.DoesNotExist:
                return None
        return None
    
    def resolve_material(self, info, id):
        try:
            return models.Material.objects.get(id=id, is_active=True)
        except models.Material.DoesNotExist:
            return None
    
    def resolve_payment(self, info, id):
        if info.context.user.is_authenticated:
            try:
                payment = models.Payment.objects.get(id=id)
                # Check permissions
                if (payment.order.user == info.context.user or 
                    info.context.user.is_staff):
                    return payment
            except models.Payment.DoesNotExist:
                return None
        return None
    
    def resolve_order_timeline(self, info, orderId):
        if info.context.user.is_authenticated:
            try:
                order = models.Order.objects.get(id=orderId)
                if (order.user == info.context.user or 
                    info.context.user.is_staff):
                    return models.OrderTimeline.objects.filter(order=order)
            except models.Order.DoesNotExist:
                return []
        return []
    
    def resolve_cart_item(self, info, id):
        if info.context.user.is_authenticated:
            try:
                return models.CartItem.objects.get(id=id, user=info.context.user)
            except models.CartItem.DoesNotExist:
                return None
        return None
    
    def resolve_wishlist_item(self, info, id):
        if info.context.user.is_authenticated:
            try:
                return models.Wishlist.objects.get(id=id, user=info.context.user)
            except models.Wishlist.DoesNotExist:
                return None
        return None
    
    def resolve_review(self, info, id):
        try:
            return models.Review.objects.get(id=id, is_verified=True)
        except models.Review.DoesNotExist:
            return None
    
    def resolve_review_reports(self, info, reviewId):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return models.ReviewReport.objects.filter(review_id=reviewId)
        return []
    
    def resolve_design(self, info, id):
        try:
            return models.Design.objects.get(id=id, is_active=True)
        except models.Design.DoesNotExist:
            return None
    
    def resolve_design_category(self, info, id):
        try:
            return models.DesignCategory.objects.get(id=id, is_active=True)
        except models.DesignCategory.DoesNotExist:
            return None
    
    def resolve_blog_post(self, info, id=None, slug=None):
        try:
            if id:
                return models.BlogPost.objects.get(id=id, is_published=True)
            elif slug:
                return models.BlogPost.objects.get(slug=slug, is_published=True)
        except models.BlogPost.DoesNotExist:
            return None
        return None
    
    def resolve_blog_category(self, info, id):
        try:
            return models.BlogCategory.objects.get(id=id)
        except models.BlogCategory.DoesNotExist:
            return None
    
    def resolve_notification(self, info, id):
        if info.context.user.is_authenticated:
            try:
                return models.Notification.objects.get(id=id, user=info.context.user)
            except models.Notification.DoesNotExist:
                return None
        return None
    
    def resolve_alerts(self, info, **kwargs):
        if info.context.user.is_authenticated:
            return models.Alert.objects.filter(user=info.context.user, is_active=True)
        return models.Alert.objects.none()
    
    def resolve_alert(self, info, id):
        if info.context.user.is_authenticated:
            try:
                return models.Alert.objects.get(id=id, user=info.context.user)
            except models.Alert.DoesNotExist:
                return None
        return None
    
    def resolve_erp_sync_logs(self, info, **kwargs):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return models.ERPNextSyncLog.objects.all()
        return models.ERPNextSyncLog.objects.none()
    
    def resolve_behavior_tracking(self, info, **kwargs):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return models.BehaviorTracking.objects.all()
        return models.BehaviorTracking.objects.none()
    
    def resolve_forecasts(self, info, **kwargs):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return models.Forecast.objects.all()
        return models.Forecast.objects.none()
    
    def resolve_customer_segments(self, info):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return models.CustomerSegment.objects.all()
        return []
    
    def resolve_pricing_engine(self, info):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            try:
                return models.PricingEngine.objects.first()
            except models.PricingEngine.DoesNotExist:
                return None
        return None
    
    def resolve_conversation_history(self, info, sessionId=None):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            if sessionId:
                return models.ConversationHistory.objects.filter(session_id=sessionId)
            return models.ConversationHistory.objects.all()
        return []
    
    def resolve_dashboard_settings(self, info):
        if info.context.user.is_authenticated:
            try:
                return info.context.user.dashboard_settings
            except models.DashboardSettings.DoesNotExist:
                return None
        return None
    
    def resolve_wishlist_settings(self, info):
        if info.context.user.is_authenticated:
            try:
                return info.context.user.wishlist_settings
            except models.WishlistSettings.DoesNotExist:
                return None
        return None
    
    def resolve_validate_coupon(self, info, code):
        try:
            coupon = models.Coupon.objects.get(code=code.upper(), is_active=True)
            # Add validation logic here (check dates, usage limits, etc.)
            return coupon
        except models.Coupon.DoesNotExist:
            return None


schema = Schema(query=Query, mutation=Mutation)
