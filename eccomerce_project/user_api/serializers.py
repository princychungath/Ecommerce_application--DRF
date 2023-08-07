from rest_framework import serializers
from .models import User,Cart,Order,OrderItem,Profile
from  admin_api.serializers import ProductSerializer

class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password", "password2"]

    def save(self):
        register = User(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Password should match'})
        register.set_password(password)
        register.save()
        return register


class PasswordResetSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']
        

class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity']

    

class ProfileSerilizer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model =Profile
        fields = ['user','house_name','place','pin','mobile_number']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Order
        fields = ['id','user','created_at','total_amount','payment_method']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True) 
    order = OrderSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id','order','product', 'quantity', 'price']
