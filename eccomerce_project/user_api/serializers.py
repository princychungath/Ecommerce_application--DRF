from rest_framework import serializers
from .models import User,CartItem,Order,OrderItem,Address,Profile
from admin_api.models import Product,Category

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
    new_password_1= serializers.CharField(required=True)


    def validate(self, data):
        new_password = data.get('new_password')
        new_password_1 = data.get('new_password_1')

        if new_password != new_password_1:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def save(self):
        uid = self.validated_data['uid']
        new_password = self.validated_data['new_password']

        user = User.objects.get(id=uid)
        user.set_password(new_password)
        user.save()
        return user



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']
 
       
class ProductSerializer(serializers.ModelSerializer):
    categories =CategorySerializer(many=True)
    quantity=serializers.SerializerMethodField()
    
    class Meta:
        model=Product
        fields=['id','product_name','description','price','quantity','image','categories']

    def get_quantity(self, instance):
        if instance.quantity <= 0:
            return "out of stock"
        else:
            return instance.quantity




class ProfileSerilizer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    first_name=serializers.SerializerMethodField()
    last_name=serializers.SerializerMethodField()
    email=serializers.SerializerMethodField()

    class Meta:
        model =Profile
        fields = ['user','profile_picture','email','first_name', 'last_name','mobile_number','created_at']

    def get_user(self,instance):
        return instance.user.username
    def get_first_name(self,instance):
        return instance.user.first_name
    def get_last_name(self,instance):
        return instance.user.last_name
    def get_email(self,instance):
        return instance.user.email

class AddressSerilizer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model =Address
        fields = ['id','user','house_name','place','pin','mobile_number','address_is_default']

    def get_user(self,instance):
        return instance.user.username



class ProductviewSerializer(serializers.ModelSerializer):
       class Meta:
        model=Product
        fields=['id','product_name','price','image']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductviewSerializer(read_only=True)
    user = serializers.SerializerMethodField() 
    total=serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id','user', 'product', 'quantity','total']

    def get_user(self,instance):
        return instance.user.username

    def get_total(self,instance):
        return instance.product.price* instance.quantity
     

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id','user','created_at','total_amount','payment_method','status']

    def get_user(self,instance):
        return instance.user.username


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductviewSerializer(read_only=True) 

    class Meta:
        model = OrderItem
        fields = ['id','order','product', 'quantity', 'price']



