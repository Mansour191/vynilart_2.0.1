"""
API URLs for cart and shipping system
"""

from django.urls import path
from . import views
from graphene_django import GraphQLView

app_name = 'api'

urlpatterns = [
    # GraphQL Endpoint
    path('graphql/', GraphQLView.as_view(graphiql=True), name='graphql'),
    
    # Cart Endpoints
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/clear/', views.ClearCartView.as_view(), name='clear-cart'),
    path('cart/merge/', views.MergeCartView.as_view(), name='merge-cart'),
    
    # Shipping Endpoints
    path('shipping/wilayas/', views.WilayasView.as_view(), name='wilayas'),
    path('shipping/wilayas/<int:wilaya_id>/', views.WilayaDetailView.as_view(), name='wilaya-detail'),
    path('shipping/bulk-update/', views.BulkUpdateShippingView.as_view(), name='bulk-update-shipping'),
    path('shipping/calculate/', views.CalculateShippingView.as_view(), name='calculate-shipping'),
    
    # Notifications
    path('notifications/', views.NotificationViewSet.as_view({'get': 'list', 'post': 'create'}), name='notifications'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/mark-all-read/', views.MarkAllReadView.as_view(), name='mark-all-read'),
    path('notifications/unread/', views.UnreadNotificationsView.as_view(), name='unread-notifications'),
    path('notifications/statistics/', views.NotificationStatisticsView.as_view(), name='notification-statistics'),
    
    # Admin Broadcast
    path('admin/broadcast/', views.AdminBroadcastView.as_view(), name='admin-broadcast'),
]
