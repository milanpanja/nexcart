from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import *
from .serializers import *

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]
    
    def get_queryset(self):
        qs = Product.objects.all()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        featured = self.request.query_params.get('featured')
        if category:
            qs = qs.filter(category__id=category)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if featured:
            qs = qs.filter(is_featured=True)
        return qs

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    def create(self, request):
        data = request.data
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=400)
        
        total = sum(item.product.price * item.quantity for item in cart.items.all())
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            shipping_address=data.get('shipping_address', ''),
            payment_method=data.get('payment_method', 'cod'),
            payment_status='paid' if data.get('payment_method') != 'cod' else 'pending'
        )
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        cart.items.all().delete()
        return Response(OrderSerializer(order).data, status=201)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()
        order.status = request.data.get('status', order.status)
        order.save()
        return Response(OrderSerializer(order).data)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        return Response(CartSerializer(cart).data)
    
    elif request.method == 'POST':
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = Product.objects.get(id=product_id)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += int(quantity)
        else:
            item.quantity = int(quantity)
        item.save()
        return Response(CartSerializer(cart).data)
    
    elif request.method == 'DELETE':
        item_id = request.data.get('item_id')
        CartItem.objects.filter(id=item_id, cart=cart).delete()
        return Response(CartSerializer(cart).data)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered'}, status=400)
    
    user = User.objects.create_user(
        username=username, email=email, password=password,
        first_name=first_name, last_name=last_name
    )
    UserProfile.objects.create(user=user)
    return Response({'message': 'User created successfully'}, status=201)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    if request.method == 'GET':
        return Response(UserSerializer(user).data)
    
    user.first_name = request.data.get('first_name', user.first_name)
    user.last_name = request.data.get('last_name', user.last_name)
    user.email = request.data.get('email', user.email)
    user.save()
    
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.phone = request.data.get('phone', profile.phone)
    profile.address = request.data.get('address', profile.address)
    profile.save()
    
    return Response(UserSerializer(user).data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    total_revenue = Order.objects.filter(
        status__in=['confirmed','processing','shipped','delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    monthly_revenue = Order.objects.filter(
        created_at__gte=thirty_days_ago,
        status__in=['confirmed','processing','shipped','delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    orders_by_status = {}
    for s in ['pending','confirmed','processing','shipped','delivered','cancelled']:
        orders_by_status[s] = Order.objects.filter(status=s).count()
    
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    return Response({
        'total_users': User.objects.filter(is_staff=False).count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_revenue': float(total_revenue),
        'monthly_revenue': float(monthly_revenue),
        'pending_orders': orders_by_status['pending'],
        'orders_by_status': orders_by_status,
        'recent_orders': OrderSerializer(recent_orders, many=True).data,
        'low_stock_products': ProductSerializer(
            Product.objects.filter(stock__lt=10).order_by('stock')[:5], many=True
        ).data,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    total_spent = orders.filter(
        status__in=['confirmed','processing','shipped','delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    return Response({
        'total_orders': orders.count(),
        'total_spent': float(total_spent),
        'pending_orders': orders.filter(status='pending').count(),
        'delivered_orders': orders.filter(status='delivered').count(),
        'recent_orders': OrderSerializer(orders.order_by('-created_at')[:5], many=True).data,
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users(request):
    users = User.objects.filter(is_staff=False).order_by('-date_joined')
    return Response(UserSerializer(users, many=True).data)
