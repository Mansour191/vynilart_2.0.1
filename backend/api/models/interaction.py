"""
User Interaction Models for VynilArt API
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class ReviewReport(models.Model):
    """
    Reports for inappropriate reviews
    """
    review = models.ForeignKey(
        'ReviewReport', 
        on_delete=models.CASCADE,
        related_name='reports'
    )
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.CASCADE,
        related_name='review_reports'
    )
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.review.id}"

    class Meta:
        indexes = [
            models.Index(fields=['review']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['review', 'user']
        ordering = ['-created_at']


class UserBehaviorTracking(models.Model):
    """
    Track user behavior for analytics and personalization
    """
    ACTION_CHOICES = [
        # Product interactions
        ('product_view', 'Product View'),
        ('product_like', 'Product Like'),
        ('product_share', 'Product Share'),
        ('product_search', 'Product Search'),
        
        # Cart interactions
        ('cart_add', 'Add to Cart'),
        ('cart_remove', 'Remove from Cart'),
        ('cart_abandon', 'Cart Abandonment'),
        
        # Order interactions
        ('order_initiate', 'Order Initiation'),
        ('order_complete', 'Order Completion'),
        ('order_cancel', 'Order Cancellation'),
        
        # Search interactions
        ('search_query', 'Search Query'),
        ('search_filter', 'Search Filter'),
        
        # Content interactions
        ('blog_view', 'Blog View'),
        ('design_view', 'Design View'),
        ('review_write', 'Write Review'),
        
        # System interactions
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('profile_update', 'Profile Update'),
    ]
    
    TARGET_TYPE_CHOICES = [
        ('product', 'Product'),
        ('category', 'Category'),
        ('search', 'Search'),
        ('cart', 'Cart'),
        ('order', 'Order'),
        ('blog', 'Blog'),
        ('design', 'Design'),
        ('user', 'User'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(
        'api.User', 
        on_delete=models.CASCADE,
        related_name='behavior_tracking'
    )
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=50, choices=TARGET_TYPE_CHOICES, blank=True, null=True)
    target_id = models.IntegerField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['target_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['ip_address']),
        ]
        ordering = ['-created_at']


class ConversationHistory(models.Model):
    """
    Chat conversation history
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    session_id = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.session_id} - {self.role}"

    class Meta:
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['role']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['session_id', 'timestamp']
