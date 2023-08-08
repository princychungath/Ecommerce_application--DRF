from rest_framework import serializers
from .models import Product,Category
from user_api.models import Order,User

class UserListSerilizer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields=['id','username', 'first_name', 'last_name','date_joined']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','category_name']


class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)
    quantity=serializers.SerializerMethodField()
    
    class Meta:
        model=Product
        fields=['id','name','description','price','quantity','image','categories']

    def get_quantity(self, instance):
        if instance.quantity <= 0:
            return "out of stock"
        else:
            return instance.quantity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']

class OrderconfirmSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Order
        fields = ['id','user','status']