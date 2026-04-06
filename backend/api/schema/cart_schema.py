"""
Enhanced Cart Schema for VynilArt API
"""
import graphene
import json
from graphene import relay, ObjectType, Mutation, Field, List, String, Int, Float, Boolean, DateTime, JSONString, ID
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from api.models.cart import CartItem
from api.models.promotion import Coupon
from api.models.product import Product, Material
from api.models.shipping import Shipping

User = get_user_model()


class CartItemType(DjangoObjectType):
    """Enhanced Cart Item type with all required fields"""
    
    # Enhanced product details for better UI integration
    product_details = Field(JSONString)
    
    # Computed fields
    subtotal = Field(Float)
    total_with_discount = Field(Float)
    final_total = Field(Float)
    is_available = Field(Boolean)
    max_quantity = Field(Int)
    
    # Real-time pricing fields
    current_unit_price = Field(Float)
    current_material_price = Field(Float)
    price_changed = Field(Boolean)
    
    # Additional fields for better integration
    weight = Field(Float)
    dimensions = Field(String)
    
    class Meta:
        model = models.CartItem
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'user': ['exact'],
            'product': ['exact'],
            'material': ['exact'],
            'delivery_type': ['exact'],
            'session_id': ['exact'],
        }

    def resolve_product_details(self, info):
        """Get enhanced product details for UI"""
        return {
            'id': self.product.id,
            'name_ar': self.product.name_ar,
            'name_en': self.product.name_en,
            'slug': self.product.slug,
            'base_price': float(self.product.base_price),
            'stock': self.product.stock,
            'is_active': self.product.is_active,
            'images': [
                {
                    'id': img.id,
                    'image_url': img.image_url,
                    'is_main': img.is_main
                } for img in self.product.images.all()
            ]
        }
    
    def resolve_subtotal(self, info):
        """Calculate subtotal for this cart item"""
        return float(self.subtotal)
    
    def resolve_total_with_discount(self, info):
        """Calculate total after discount"""
        return float(self.total_with_discount)
    
    def resolve_final_total(self, info):
        """Calculate final total including shipping"""
        return float(self.final_total)
    
    def resolve_is_available(self, info):
        """Check if product is available"""
        return self.is_available
    
    def resolve_max_quantity(self, info):
        """Get maximum quantity available"""
        return self.max_quantity
    
    def resolve_current_unit_price(self, info):
        """Get current unit price from product"""
        return float(self.product.base_price)
    
    def resolve_current_material_price(self, info):
        """Get current material price"""
        if self.material:
            if self.width and self.height:
                area_m2 = (float(self.width) * float(self.height)) / 10000
                return float(self.material.price_per_m2 * area_m2)
            return float(self.material.price_per_m2)
        return 0.0
    
    def resolve_price_changed(self, info):
        """Check if price has changed since cart item was created"""
        current_unit = float(self.product.base_price)
        current_material = self.resolve_current_material_price(info)
        
        return (current_unit != float(self.unit_price) or 
                current_material != float(self.material_price))
    
    def resolve_weight(self, info):
        """Get total weight for this cart item"""
        product_weight = float(self.product.weight) if self.product.weight else 0
        return product_weight * self.quantity
    
    def resolve_dimensions(self, info):
        """Get formatted dimensions"""
        if self.width and self.height:
            return f"{self.width}×{self.height} {self.dimension_unit}"
        return None


# Input Types
class CartItemInput(graphene.InputObjectType):
    """Enhanced input for cart item operations"""
    product_id = Int(required=True)
    material_id = Int()
    quantity = Int(default_value=1)
    width = Float()
    height = Float()
    dimension_unit = String(default_value='cm')
    delivery_type = String(default_value='home')
    wilaya_id = String()
    options = JSONString()


class UpdateCartInput(graphene.InputObjectType):
    """Input for updating cart quantity"""
    cart_item_id = Int(required=True)
    quantity = Int(required=True)


class ApplyCouponInput(graphene.InputObjectType):
    """Input for applying coupon"""
    coupon_code = String(required=True)
    cart_item_ids = List(Int)  # Optional: apply to specific items


class SetShippingInput(graphene.InputObjectType):
    """Input for setting shipping"""
    wilaya_id = String(required=True)
    delivery_type = String(default_value='home')
    cart_item_ids = List(Int)  # Optional: apply to specific items


class MergeCartInput(graphene.InputObjectType):
    """Input for merging guest cart with user cart"""
    session_id = String(required=True)


# Enhanced Mutations
class AddToCart(Mutation):
    """Enhanced add to cart mutation with stock validation and price warnings"""
    
    class Arguments:
        input = CartItemInput(required=True)

    cart_item = Field(CartItemType)
    success = Boolean()
    message = String()
    cart_summary = Field(JSONString)
    price_warnings = Field(JSONString)
    stock_warnings = Field(JSONString)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            # For guest users, use session
            session_id = info.context.session.session_key or info.context.session.create()
        else:
            session_id = None
        
        try:
            with transaction.atomic():
                product = models.Product.objects.select_for_update().get(id=input.product_id)
                
                # Enhanced stock validation
                if not product.is_active:
                    return AddToCart(
                        success=False, 
                        message="Product is not available",
                        stock_warnings={'product_id': product.id, 'reason': 'inactive'}
                    )
                
                if product.stock < input.quantity:
                    return AddToCart(
                        success=False, 
                        message=f"Only {product.stock} items available",
                        stock_warnings={
                            'available_stock': product.stock,
                            'requested_quantity': input.quantity,
                            'product_id': product.id
                        }
                    )
                
                material = None
                if input.material_id:
                    material = models.Material.objects.get(id=input.material_id)
                
                wilaya = None
                if input.wilaya_id:
                    wilaya = models.Shipping.objects.get(wilaya_id=input.wilaya_id)
                    if not wilaya.is_active:
                        return AddToCart(
                            success=False, 
                            message="Shipping to this wilaya is not available"
                        )
                
                # Get or create cart item with enhanced defaults
                cart_item, created = models.CartItem.objects.get_or_create(
                    user=user if user.is_authenticated else None,
                    session_id=session_id if not user.is_authenticated else None,
                    product=product,
                    material=material,
                    width=input.width,
                    height=input.height,
                    defaults={
                        'quantity': input.quantity,
                        'dimension_unit': input.dimension_unit or 'cm',
                        'delivery_type': input.delivery_type or 'home',
                        'wilaya': wilaya,
                        'options': json.loads(input.options) if input.options else {},
                        'unit_price': product.base_price,
                        'material_price': material.price_per_m2 if material else 0,
                    }
                )
                
                if not created:
                    # Update existing item with stock validation
                    new_quantity = cart_item.quantity + input.quantity
                    if new_quantity > product.stock:
                        return AddToCart(
                            success=False, 
                            message=f"Only {product.stock} items available in total",
                            stock_warnings={
                                'available_stock': product.stock,
                                'current_quantity': cart_item.quantity,
                                'requested_additional': input.quantity,
                                'product_id': product.id
                            }
                        )
                    
                    cart_item.quantity = new_quantity
                    cart_item.save()
                
                # Calculate shipping cost
                if wilaya:
                    cart_item.shipping_cost = cart_item.calculate_shipping_cost(wilaya, input.delivery_type or 'home')
                    cart_item.save()
                
                # Get enhanced cart summary
                cart_items = models.CartItem.objects.filter(
                    user=user if user.is_authenticated else None,
                    session_id=session_id if not user.is_authenticated else None
                ).select_related('product', 'material', 'wilaya', 'applied_coupon')
                
                # Check for price changes
                price_warnings = []
                for item in cart_items:
                    current_unit_price = float(item.product.base_price)
                    current_material_price = 0
                    if item.material:
                        if item.width and item.height:
                            area_m2 = (float(item.width) * float(item.height)) / 10000
                            current_material_price = float(item.material.price_per_m2 * area_m2)
                        else:
                            current_material_price = float(item.material.price_per_m2)
                    
                    if (current_unit_price != float(item.unit_price) or 
                        current_material_price != float(item.material_price)):
                        price_warnings.append({
                            'cart_item_id': item.id,
                            'product_name': item.product.name_ar,
                            'old_unit_price': float(item.unit_price),
                            'new_unit_price': current_unit_price,
                            'old_material_price': float(item.material_price),
                            'new_material_price': current_material_price,
                            'old_total': float(item.subtotal),
                            'new_total': float((current_unit_price + current_material_price) * item.quantity)
                        })
                
                cart_summary = {
                    'total_items': cart_items.count(),
                    'subtotal': sum(float(item.subtotal) for item in cart_items),
                    'discount_total': sum(float(item.discount_amount) + float(item.coupon_discount) for item in cart_items),
                    'shipping_cost': sum(float(item.shipping_cost) for item in cart_items),
                    'total': sum(float(item.final_total) for item in cart_items),
                    'price_warnings_count': len(price_warnings),
                    'unavailable_items': sum(1 for item in cart_items if not item.is_available)
                }
                
                return AddToCart(
                    cart_item=cart_item,
                    success=True,
                    message="Added to cart successfully",
                    cart_summary=json.dumps(cart_summary),
                    price_warnings=json.dumps(price_warnings) if price_warnings else None
                )
                
        except models.Product.DoesNotExist:
            return AddToCart(success=False, message="Product not found")
        except models.Material.DoesNotExist:
            return AddToCart(success=False, message="Material not found")
        except models.Shipping.DoesNotExist:
            return AddToCart(success=False, message="Wilaya not found")
        except Exception as e:
            return AddToCart(success=False, message=str(e))


class UpdateCartQuantity(Mutation):
    """Enhanced update cart quantity mutation"""
    
    class Arguments:
        input = UpdateCartInput(required=True)

    cart_item = Field(CartItemType)
    success = Boolean()
    message = String()
    cart_summary = Field(JSONString)
    stock_warnings = Field(JSONString)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateCartQuantity(success=False, message="Authentication required")
        
        try:
            with transaction.atomic():
                cart_item = models.CartItem.objects.select_for_update().get(
                    id=input.cart_item_id,
                    user=user
                )
                
                # Check availability
                if input.quantity > cart_item.product.stock:
                    return UpdateCartQuantity(
                        success=False, 
                        message=f"Only {cart_item.product.stock} items available",
                        stock_warnings={
                            'available_stock': cart_item.product.stock,
                            'requested_quantity': input.quantity,
                            'current_quantity': cart_item.quantity
                        }
                    )
                
                if input.quantity <= 0:
                    cart_item.delete()
                    message = "Item removed from cart"
                    cart_item = None
                else:
                    cart_item.quantity = input.quantity
                    cart_item.save()
                    message = "Cart updated successfully"
                
                # Get updated cart summary
                cart_items = models.CartItem.objects.filter(user=user)
                cart_summary = {
                    'total_items': cart_items.count(),
                    'subtotal': sum(float(item.subtotal) for item in cart_items),
                    'discount_total': sum(float(item.discount_amount) + float(item.coupon_discount) for item in cart_items),
                    'shipping_cost': sum(float(item.shipping_cost) for item in cart_items),
                    'total': sum(float(item.final_total) for item in cart_items),
                    'unavailable_items': sum(1 for item in cart_items if not item.is_available)
                }
                
                return UpdateCartQuantity(
                    cart_item=cart_item,
                    success=True,
                    message=message,
                    cart_summary=json.dumps(cart_summary)
                )
                
        except models.CartItem.DoesNotExist:
            return UpdateCartQuantity(success=False, message="Cart item not found")
        except Exception as e:
            return UpdateCartQuantity(success=False, message=str(e))


class RemoveFromCart(Mutation):
    """Enhanced remove from cart mutation"""
    
    class Arguments:
        cart_item_id = Int(required=True)

    success = Boolean()
    message = String()
    cart_summary = Field(JSONString)

    def mutate(self, info, cart_item_id):
        user = info.context.user
        if not user.is_authenticated:
            return RemoveFromCart(success=False, message="Authentication required")
        
        try:
            with transaction.atomic():
                cart_item = models.CartItem.objects.get(
                    id=cart_item_id,
                    user=user
                )
                cart_item.delete()
                
                # Get updated cart summary
                cart_items = models.CartItem.objects.filter(user=user)
                cart_summary = {
                    'total_items': cart_items.count(),
                    'subtotal': sum(float(item.subtotal) for item in cart_items),
                    'discount_total': sum(float(item.discount_amount) + float(item.coupon_discount) for item in cart_items),
                    'shipping_cost': sum(float(item.shipping_cost) for item in cart_items),
                    'total': sum(float(item.final_total) for item in cart_items),
                    'unavailable_items': sum(1 for item in cart_items if not item.is_available)
                }
                
                return RemoveFromCart(
                    success=True,
                    message="Item removed from cart",
                    cart_summary=json.dumps(cart_summary)
                )
                
        except models.CartItem.DoesNotExist:
            return RemoveFromCart(success=False, message="Cart item not found")
        except Exception as e:
            return RemoveFromCart(success=False, message=str(e))


class MergeCart(Mutation):
    """Merge guest cart with user cart"""
    
    class Arguments:
        input = MergeCartInput(required=True)

    success = Boolean()
    message = String()
    cart_summary = Field(JSONString)
    merged_items = Field(JSONString)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return MergeCart(success=False, message="Authentication required")
        
        try:
            with transaction.atomic():
                # Get guest cart items
                guest_items = models.CartItem.objects.filter(
                    session_id=input.session_id,
                    user__isnull=True
                ).select_related('product', 'material', 'wilaya', 'applied_coupon')
                
                # Merge with user cart
                merged_items = []
                for guest_item in guest_items:
                    # Check if similar item exists in user cart
                    existing_item = models.CartItem.objects.filter(
                        user=user,
                        product=guest_item.product,
                        material=guest_item.material,
                        width=guest_item.width,
                        height=guest_item.height
                    ).first()
                    
                    if existing_item:
                        # Merge quantities
                        old_quantity = existing_item.quantity
                        existing_item.quantity += guest_item.quantity
                        existing_item.options.update(guest_item.options)
                        existing_item.save()
                        
                        merged_items.append({
                            'product_name': guest_item.product.name_ar,
                            'guest_quantity': guest_item.quantity,
                            'existing_quantity': old_quantity,
                            'new_quantity': existing_item.quantity,
                            'action': 'merged'
                        })
                        
                        guest_item.delete()
                    else:
                        # Transfer to user cart
                        guest_item.user = user
                        guest_item.session_id = None
                        guest_item.save()
                        
                        merged_items.append({
                            'product_name': guest_item.product.name_ar,
                            'quantity': guest_item.quantity,
                            'action': 'transferred'
                        })
                
                # Get updated cart summary
                cart_items = models.CartItem.objects.filter(user=user)
                cart_summary = {
                    'total_items': cart_items.count(),
                    'subtotal': sum(float(item.subtotal) for item in cart_items),
                    'discount_total': sum(float(item.discount_amount) + float(item.coupon_discount) for item in cart_items),
                    'shipping_cost': sum(float(item.shipping_cost) for item in cart_items),
                    'total': sum(float(item.final_total) for item in cart_items),
                    'unavailable_items': sum(1 for item in cart_items if not item.is_available)
                }
                
                return MergeCart(
                    success=True,
                    message=f"Cart merged successfully. {len(merged_items)} items processed.",
                    cart_summary=json.dumps(cart_summary),
                    merged_items=json.dumps(merged_items)
                )
                
        except Exception as e:
            return MergeCart(success=False, message=str(e))


# Query Class
class CartQuery(ObjectType):
    """Cart queries"""
    
    my_cart = List(CartItemType)
    cart_item = Field(CartItemType, id=ID(required=True))
    cart_summary = Field(JSONString)
    
    def resolve_my_cart(self, info):
        """Get current user's cart"""
        if not info.context.user.is_authenticated:
            return []
        
        return models.CartItem.objects.active().for_user(info.context.user)
    
    def resolve_cart_item(self, info, id):
        """Get specific cart item"""
        if not info.context.user.is_authenticated:
            return None
        
        try:
            return models.CartItem.objects.get(
                id=id,
                user=info.context.user
            )
        except models.CartItem.DoesNotExist:
            return None
    
    def resolve_cart_summary(self, info):
        """Get cart summary"""
        if not info.context.user.is_authenticated:
            return json.dumps({})
        
        cart_items = models.CartItem.objects.active().for_user(info.context.user)
        
        summary = {
            'total_items': cart_items.count(),
            'subtotal': sum(float(item.subtotal) for item in cart_items),
            'discount_total': sum(float(item.discount_amount) + float(item.coupon_discount) for item in cart_items),
            'shipping_cost': sum(float(item.shipping_cost) for item in cart_items),
            'total': sum(float(item.final_total) for item in cart_items),
            'available_items': sum(1 for item in cart_items if item.is_available),
            'unavailable_items': sum(1 for item in cart_items if not item.is_available),
            'price_changed_items': sum(1 for item in cart_items if item.price_changed)
        }
        
        return json.dumps(summary)


# Node Classes from core/schema.py
class CartItemNode(DjangoObjectType, IsAuthenticatedMixin):
    """Enhanced cart item node with product details"""
    user = Field('UserNode')
    product = Field('ProductNode')
    material = Field('MaterialNode')
    
    class Meta:
        model = models.CartItem
        interfaces = (relay.Node,)
        fields = '__all__'


class CouponNode(DjangoObjectType):
    """Coupon node with enhanced filtering"""
    class Meta:
        model = models.Coupon
        interfaces = (relay.Node,)
        fields = '__all__'
        filter_fields = {
            'code': ['exact', 'icontains'],
            'is_active': ['exact'],
            'discount_type': ['exact'],
            'min_amount': ['lt', 'lte', 'gt', 'gte'],
        }


# Mutation Class
class CartMutation(ObjectType):
    """Cart mutations"""
    
    add_to_cart = AddToCart.Field()
    update_cart_quantity = UpdateCartQuantity.Field()
    remove_from_cart = RemoveFromCart.Field()
    merge_cart = MergeCart.Field()
