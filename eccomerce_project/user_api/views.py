from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from .serializers import UserSignUpSerializer,PasswordResetSerializer,CartSerializer,OrderSerializer,ProfileSerilizer
from admin_api.serializers import ProductSerializer
from .models import User,Cart,Order,OrderItem,Profile
from admin_api.models import Product
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_decode



class RegisterUser(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            subject = 'User Registration'
            email_to=[user.email]
            html_content = render_to_string('user_reg.html', {'username': user.username})
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(subject,text_content,settings.DEFAULT_FROM_EMAIL,email_to)
            email.attach_alternative(html_content,"text/html")
            email.send()
            return Response({"message": "User created."})
        else:
            return Response(serializer.errors)


class SendPasswordResetEmail(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Please provide an email address.'})
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User with this email address does not exist.'})
        # generates a password reset token that is associated with the specific user. 
        token = default_token_generator.make_token(user)
        #encode pk
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = 'http://127.0.0.1:8000/app_user/reset-password/'  

        context = {
            'reset_url': reset_url,
            'token':token,
            'uid':uid,
            'user':user
        }
        subject = 'Password Reset'
        email_to = [email]
        html_content = render_to_string('reset_password.html',context)
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(subject,text_content , settings.DEFAULT_FROM_EMAIL, email_to)
        email.attach_alternative(html_content,"text/html")
        email.send()
        return Response({'success': 'Password reset email sent.'})


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
                    # Set the new password and save the user object
                    user.set_password(new_password)
                    user.save()
                    return Response({'message': 'Password successfully reset.'})
            except User.DoesNotExist:
                return Response({'User': 'User DoesNotExist'})
        return Response({'error': 'Invalid password reset link.'})


class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name','price','quantity','categories']



class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({"message": "Product not found."})



class CartAddView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def post(self, request, *args, **kwargs):
        product_id = int(request.data.get('product_id'))
        quantity = int(request.data.get('quantity', 1))
        user = request.user

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'})

        cart_item, created = Cart.objects.get_or_create(user=user, product=product)

        if created or quantity > 1:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()
        serializer = CartSerializer(cart_item)
        return Response({'message': 'Product added to cart.'})


class CartListView(generics.ListAPIView):
    queryset=Cart.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class= CartSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)


class CartUpdateView(generics.UpdateAPIView):
    queryset=Cart.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class= CartSerializer


    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
           return Response({"message":"You don't have the permission to update this Comment"})
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
           return Response({"message":"You don't have the permission to update this CART"})
        return super().put(request, *args, **kwargs)
        


class CartDeleteView(generics.DestroyAPIView):
    queryset=Cart.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class= CartSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"message": "You don't have the permission to delete this CART"})
        response = super().delete(request, *args, **kwargs)
        return Response({'message': 'Cart items Removed'})


class ProfileView(generics.CreateAPIView):
    queryset=Profile.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=ProfileSerilizer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        items = Cart.objects.filter(user=user)
        order_items = []
        total_amount = 0  

        if not items.exists():
            return Response({"error": "Cart is empty"})

        for item in items:
            product = item.product
            if product.quantity < item.quantity:
                return Response({"error": f"Out of stock: {product.name}"})

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
            items.delete()

        profile = Profile.objects.get(user=user)

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
        text_content=strip_tags(html_content)
        email=EmailMultiAlternatives(subject,text_content,settings.DEFAULT_FROM_EMAIL,email_to)
        email.attach_alternative(html_content,"text/html")
        email.send()


        subject="New Order Received"
        email_to=['admin@gmail.com']
        html_content=render_to_string('order_admin.html',context)
        text_content=strip_tags(html_content)
        email=EmailMultiAlternatives(subject,text_content,settings.DEFAULT_FROM_EMAIL,email_to)
        email.attach_alternative(html_content,"text/html")
        email.send()
        return Response({"message": "Order Submitted successfully."})



class OrderListView(generics.ListAPIView):
    queryset= Order.objects.all()
    serializer_class= OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)

