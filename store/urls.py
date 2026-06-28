from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('categories', views.CategoryViewSet)
router.register('orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('cart/', views.cart_view),
    path('register/', views.register_view),
    path('profile/', views.profile_view),
    path('admin-dashboard/', views.admin_dashboard),
    path('user-dashboard/', views.user_dashboard),
    path('admin-users/', views.admin_users),
]
