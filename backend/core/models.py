"""
Core Models Aggregation - Central import point for all API models
This file serves as the main models import point for the application.
All actual model definitions are organized in the api/models/ directory.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
import uuid

# Import all models from api package to maintain compatibility
from api.models import (
    # User models
    user,
    
    # Product models
    product,
    
    # Order models
    order,
    
    # Cart models
    cart,
    
    # Shipping models
    shipping,
    
    # Promotion models
    promotion,
    
    # Wishlist models
    wishlist,
    
    # Review models
    review,
    
    # Design models
    design,
    
    # Notification models
    notification,
    
    # Blog models
    blog,
    
    # System models
    system,
    
    # Organization models
    organization,
    
    # Analytics models
    analytics,
    
    # Alert models
    alert,
    
    # Content models
    content,
    
    # Interaction models
    interaction,
)

# Legacy imports for backward compatibility
User = api.models.user.User

# Export all models for easy access
__all__ = [
    # Import all from api.models
    *api.models.__all__,
]
