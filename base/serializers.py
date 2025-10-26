# products/serializers.py
from rest_framework import serializers
from .models import Product, Order, OrderItem, ShippingAddress
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.conf import settings

class ProductSerializer(serializers.ModelSerializer):
    _id = serializers.IntegerField(source='id', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            '_id', 'name', 'image', 'description', 'brand', 'category',
            'price', 'countInStock', 'rating', 'numReviews', 'createdAt'
        ]
        read_only_fields = ['_id', 'createdAt']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be ≥ 0.")
        return value

    def validate_countInStock(self, value):
        if value < 0:
            raise serializers.ValidationError("countInStock must be ≥ 0.")
        return value
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            image_url = obj.image.url
            # If a request is available, build absolute URI
            if request is not None:
                return request.build_absolute_uri(image_url)
            # Fallback if no request context is given
            return f"{settings.MEDIA_URL}{obj.image}"
        return None

class ProductUpdateSerializer(serializers.ModelSerializer):
    _id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Product
        fields = [
            '_id', 'name', 'description', 'brand', 'category', 'price', 'countInStock'
        ]
        read_only_fields = ['_id', 'createdAt']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be ≥ 0.")
        return value

    def validate_countInStock(self, value):
        if value < 0:
            raise serializers.ValidationError("countInStock must be ≥ 0.")
        return value

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.username
        token['email'] = user.email

        return token

class UserSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email', 'name', 'isAdmin']

    def get__id(self, obj):
        return obj.id

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email

        return name

class UserSerializerWithToken(UserSerializer):
    # this is additional field
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        # target model
        model = User
        # target fields
        fields = ['id', '_id', 'username', 'email', 'name', 'isAdmin', 'token']

    # method to get additional field
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["user", "paymentMethod", "taxPrice", "shippingPrice", "totalPrice"]

class OrderReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "paymentMethod", "taxPrice", "shippingPrice", "totalPrice", "isPaid", "paidAt", "isDelivered", "deliveredAt", "createdAt"]

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "order", "name", "qty", "price", "image"]

class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ["order", "address", "city", "postalCode", "country", "shippingPrice"]
