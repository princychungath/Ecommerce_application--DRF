from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from .serializers import UserSignUpSerializer,PasswordResetSerializer,CartSerializer,OrderSerializer,ProfileSerilizer,CartViewSerializer
from admin_api.serializers import ProductSerializer
from .models import User,CartItem,Order,OrderItem,Profile,Cart
from admin_api.models import Product
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .pagination import MyCustomPagination

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_decode



# API view for user registration

class RegisterUser(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            context={"user":user}
            subject = 'User Registration'
            email_to=[user.email]
            html_content = render_to_string('user_reg.html',context)
            email = EmailMultiAlternatives(subject,html_content,settings.DEFAULT_FROM_EMAIL,email_to)
            email.attach_alternative(html_content,"text/html")
            email.send()
            return Response({'message':'User registered successfully'})
        else:
            return Response(serializer.errors)



# API endpoint for sending a password reset email to the provided email address

class SendPasswordResetEmail(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Please provide an email address.'})
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User with this email address does not exist.'})
        # generates a password reset token 
        token = default_token_generator.make_token(user)
        #encode pk
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = 'http://127.0.0.1:8000/app_user/reset/password/'  

        context = {
            'reset_url': reset_url,
            'token':token,
            'uid':uid,
            'user':user
        }
        subject = 'Password Reset'
        email_to = [email]
        html_content = render_to_string('reset_password.html',context)
        email = EmailMultiAlternatives(subject,html_content,settings.DEFAULT_FROM_EMAIL, email_to)
        email.attach_alternative(html_content,"text/html")
        email.send()
        response_data={
            'success': 'Password reset email sent.',
            'token':token,
            'uid':uid,
        }
        return Response(response_data)




# Resets the user's password using a provided reset link. 

class PasswordResetView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            uid = serializer.data.get('uid')
            token = serializer.data.get('token')
            new_password = serializer.data.get('new_password')
            try:
                # Decode pk
                user_id = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=user_id)
                # Verify the token's validity
                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    return Response({'New Password':new_password})
            except User.DoesNotExist:
                return Response({'User': 'User DoesNotExist'})
        return Response({'error': 'Invalid password reset link '})




# API to list products with filtering and pagination

class ProductList(generics.ListAPIView):
    queryset = Product.objects.prefetch_related('categories').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name','price','quantity','categories']
    pagination_class=MyCustomPagination





# Displays the detailed information of a product identified by its unique ID.

class ProductDetail(generics.RetrieveAPIView):

    queryset = Product.objects.prefetch_related('categories').all()
    serializer_class = ProductSerializer
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"message": "Product not found."})



# API  to add products to the user's cart.
class CartAddView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        product_id = int(request.data.get('product_id'))
        quantity = int(request.data.get('quantity'))
        user = request.user

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'})

        if product.quantity <= 0:
            return Response({"error": f" {product.name} : Out of stock"})

        cart, created = Cart.objects.get_or_create(user=user)

        if quantity == 0:
            return Response({"error": "Quantity must be at least 1"})
        
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not item_created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = int(quantity)
        
        if product.quantity < cart_item.quantity:
            cart_item.delete()
            return Response({"error": f" {product.name} : Quantity exceeds available stock"})

        cart_item.total = product.price * cart_item.quantity
        cart_item.save()

        cart_total = sum(item.total for item in cart.cartitem_set.all())
        serializer = CartSerializer(cart_item)
        context={
            'cart_total':cart_total,
            "cart_items":serializer.data
        }
        return Response(context)



#API for listing all cart items
class CartListView(generics.ListAPIView):
    queryset = CartItem.objects.select_related('cart').all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = CartViewSerializer

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(cart__user=user)



# API for updating cartitems in the user's cart. 
class CartUpdateView(generics.UpdateAPIView):
    queryset = CartItem.objects.select_related('cart').all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class= CartViewSerializer

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.cart.user != request.user:
           return Response({"message":"You don't have the permission to update this Comment"})
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.cart.user != request.user:
           return Response({"message":"You don't have the permission to update this CART"})
        return super().put(request, *args, **kwargs)
        

# API for Removing cartitems in the user's cart.
class CartDeleteView(generics.DestroyAPIView):
    queryset=CartItem.objects.select_related('cart').all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class= CartSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.cart.user != request.user:
            return Response({"message": "You don't have the permission to delete this CART"})
        response = super().delete(request, *args, **kwargs)
        return Response({'message': 'Cart items Removed'})


# API endpoint for creating a user profile.
class ProfileView(generics.CreateAPIView):
    queryset=Profile.objects.select_related('user').all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=ProfileSerilizer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


#  Detail,update,delete viewsfor user-Profile
class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Profile.objects.select_related('user').all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=ProfileSerilizer

    def get_object(self):
        profile = super().get_object()
        if profile.user != self.request.user:
            raise PermissionDenied("You don't have permission to access this profile.")
        return profile



# API view for creating  order
class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        items = CartItem.objects.filter(cart__user=user).select_related('cart')
        order_items = []
        total_amount = 0  

        if not items.exists():
            return Response({"error": "Cart is empty"})

        for item in items:
            product = item.product
            individual_price = product.price
            individual_total = individual_price * item.quantity
            total_amount += individual_total

            order_items.append({
                "product": product,
                "quantity": item.quantity,
                "price": individual_total
            })

            product.quantity -= item.quantity
            product.save()

        profile = Profile.objects.select_related('user').filter(user=user).first()

        if not profile:
            return Response({"error":"Profile does not exist. Please provide the complete address by following this link.",
            "link":" http://127.0.0.1:8000/app_user/profile/"})

        order = Order.objects.create(
            user=user,
            total_amount=total_amount, 
            payment_method='cash_on_delivery',
            profile=profile,
            status='processing' 
        )
        
        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
        
        
        context={
            'order':order,
            'order_items':order_items
        }

        subject="Order Placed Successfully"
        email_to=[user.email]
        html_content=render_to_string('order.html',context)
        email=EmailMultiAlternatives(subject,html_content,settings.DEFAULT_FROM_EMAIL,email_to)
        email.attach_alternative(html_content,"text/html")
        email.send()


        subject="New Order Received"
        email_to=['admin@gmail.com']
        html_content=render_to_string('order_admin.html',context)
        email=EmailMultiAlternatives(subject,html_content,settings.DEFAULT_FROM_EMAIL,email_to)
        email.attach_alternative(html_content,"text/html")
        email.send()
        items.delete()
        serializer_data=OrderSerializer(order)
        return Response({'order':serializer_data.data})


# API view for listing Orders associated with User
class OrderListView(generics.ListAPIView):

    queryset= Order.objects.select_related('user').all()
    serializer_class= OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class=MyCustomPagination

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)
