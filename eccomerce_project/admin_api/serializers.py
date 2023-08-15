from rest_framework import serializers
from .models import Product,Category
from user_api.models import Order,User


class CategoryViewSerializer(serializers.ModelSerializer): 
    created_user=serializers.SerializerMethodField()
    updated_user=serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id','category_name','created_user','updated_user','created_at','updated_at']
        
    def get_created_user(self, instance):
        return instance.created_user.username

    def get_updated_user(select_related,instance):
        return instance.updated_user.username


class UserListSerilizer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields=['id','username', 'first_name', 'last_name','date_joined']



class ProductCreateSerializer(serializers.ModelSerializer):
    created_user=serializers.SerializerMethodField()
    updated_user=serializers.SerializerMethodField()

    class Meta:
        model=Product
        fields=['id','product_name','description','price','quantity','image','created_user','updated_user','created_at','updated_at']

    def get_created_user(self,instance):
        return instance.created_user.username

    def get_updated_user(self,instance):
        return instance.updated_user.username



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']
       
class ProductSerializer(serializers.ModelSerializer):
    categories =CategorySerializer(many=True)
    quantity=serializers.SerializerMethodField()
    
    class Meta:
        model=Product
        fields=['id','product_name','description','price','quantity','image','created_user','updated_user','created_at','updated_at','categories']

    def get_quantity(self, instance):
        if instance.quantity <= 0:
            return "out of stock"
        else:
            return instance.quantity



class OrderconfirmSerializer(serializers.ModelSerializer):
    created_user=serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id','user','status']

    def get_created_user(self,instance):
        return instance.created_user.username
