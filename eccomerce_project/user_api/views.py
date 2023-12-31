from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from .serializers import ProductSerializer,CartItemSerializer,UserSignUpSerializer,PasswordResetSerializer,OrderSerializer,AddressSerilizer,ProfileSerilizer,OrderItemSerializer
from .models import User,CartItem,Order,OrderItem,Address,Profile
from admin_api.models import Product
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .pagination import MyCustomPagination
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_decode




def api_documentation(request):
    return render(request, 'home.html')

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
            return Response({'message': 'User registered successfully'})
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
        return Response({"message": "Password reset link has been sent to your email."})





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
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product_name','categories__category_name']
    pagination_class=MyCustomPagination


    def get_queryset(self):
        queryset = Product.objects.prefetch_related('categories').all()

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        return queryset




# Displays the detailed information of a product identified by its unique ID.

class ProductDetail(generics.RetrieveAPIView):

    queryset = Product.objects.all()
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
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        user=request.user

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'})

        if product.quantity <= 0:
            return Response({"error": f" {product.product_name} : Out of stock"})

        if quantity is None:
            quantity=1

        elif quantity == 0:
            return Response({"error": "Quantity must be at least 1"})

        cart_item, item_created = CartItem.objects.get_or_create(user=user, product=product)

        if not item_created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        if product.quantity < cart_item.quantity:
            cart_item.delete()
            return Response({"error": f" {product.product_name} : Quantity exceeds available stock"})

        serializer = CartItemSerializer(cart_item)
        context={
            "cart_items":serializer.data
        }
        return Response(context)




#API for listing all cart items
class CartListView(generics.ListAPIView):
    queryset = CartItem.objects.select_related('user').all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = CartItemSerializer
    pagination_class = None


    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(user=user)




# API for updating cartitems in the user's cart. 
class CartUpdateView(generics.UpdateAPIView):
    queryset = CartItem.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class= CartItemSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.total = instance.quantity * instance.product.price
        instance.save()

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




# API for Removing cartitems in the user's cart.
class CartDeleteView(generics.DestroyAPIView):
    queryset=CartItem.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class= CartItemSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"message": "You don't have the permission to delete this CART"})
        response = super().delete(request, *args, **kwargs)
        return Response({'message': 'Cart items Removed'})



# API endpoint for Addding Address
class AddressCreateView(generics.CreateAPIView):
    queryset=Address.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=AddressSerilizer
    

    def perform_create(self, serializer):
        user = self.request.user
        address_is_default = self.request.data.get('address_is_default', False)
    
        if address_is_default:
            Address.objects.filter(user=user, address_is_default=True).update(address_is_default=False)
        
            instance = serializer.save(user=user, address_is_default=True)
        else:
            instance = serializer.save(user=user)




# API endpoint for listing Address.
class AddresslistView(generics.ListAPIView):
    queryset=Address.objects.all().select_related('user')
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=AddressSerilizer
    pagination_class=None

    def get_queryset(self):
        user = self.request.user
        return Address.objects.filter(user=user)
        



# API endpoint for Detail view of Address.
class AddressDetailView(generics.RetrieveAPIView):
    queryset=Address.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=AddressSerilizer


    def get_object(self):
        address = super().get_object()
        if address.user != self.request.user:
            raise PermissionDenied("You don't have permission to access this address.")
        return address




# API endpoint for Update  Address.
class AddressUpdateView(generics.UpdateAPIView):
    queryset=Address.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=AddressSerilizer

    def get_object(self):
        address = super().get_object()
        if address.user != self.request.user:
            raise PermissionDenied("You don't have permission to access this address.")
        return address




# API endpoint for Remove  Address.
class AddressDestroyView(generics.DestroyAPIView):
    queryset=Address.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=AddressSerilizer


    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied("You don't have permission to delete this address.")
        response = super().delete(request, *args, **kwargs)
        return Response({'message': 'Address has been deleted successfully.'})




# API endpoint for creating a user profile.
class ProfileCreateView(generics.CreateAPIView):
    queryset=Profile.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=ProfileSerilizer


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




# API endpoint for viewuser profile.
class ProfileView(generics.ListAPIView):
    queryset=Profile.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=ProfileSerilizer
    pagination_class=None


    def get_queryset(self):
        user = self.request.user
        return Profile.objects.filter(user=user)




# API endpoint for Update User profile.
class ProfileUpdateView(generics.UpdateAPIView):
    queryset=Profile.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=ProfileSerilizer


    def get_object(self):
        address = super().get_object()
        if address.user != self.request.user:
            raise PermissionDenied("You don't have permission to access this address.")
        return address





# API endpoint for Delete profile.
class ProfileDestroyView(generics.DestroyAPIView):
    queryset=Profile.objects.all()
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=ProfileSerilizer


    def delete(self,request,*args,**kwargs):
        instance=self.get_object()

        if instance.user != self.request.user:
            raise PermissionDenied("You don't have permission to access this address.")
        response=super().delete(self,request,*args,**kwargs)
        return Response({'message': 'Profile has been deleted successfully.'})





#API view for creating  single order 
class BuyNowView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]


    def post(self, request, *args, **kwargs):
        address_id = request.data.get('address_id')
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        user = request.user
        order_items = []

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product DoesNotExist'})

        if product.quantity <= 0:
            return Response({'Error': f"{product.product_name} :Out of stock"})

        if quantity is None:
            quantity = 1
        elif quantity == 0:
            return Response({"error": "Quantity must be at least 1"})

        if product.quantity < quantity:
            return Response({'error': f"{product.product_name} :Quantity exceeds available stock"})

        price = product.price
        total_price = price * quantity

        order_items.append({
            "product": product,
            "quantity": quantity,
            "price": total_price
        })

        address_data = {}
        if address_id:
            try:
                address = Address.objects.get(user=user, id=address_id)
                address_data = {
                    "address_id": address.id,
                    "house_name": address.house_name,
                    "place": address.place,
                    "pin":address.pin,
                    "mobile_number":address.mobile_number
                }
            except Address.DoesNotExist:
                return Response({"error": "Address not found."})
        else:
            try:
                address = Address.objects.get(user=user, address_is_default=True)
                address_data = {
                    "address_id": address.id,
                    "house_name": address.house_name,
                    "place": address.place,
                    "pin":address.pin,
                    "mobile_number":address.mobile_number
                }
            except Address.DoesNotExist:
                return Response({"error": "Address not found."})


        payment_method = request.data.get('payment_method')
        if payment_method is None or payment_method not in ['cash_on_delivery', 'credit_card', 'paypal']:
            return Response({"error": "Invalid payment method"})

        order = Order.objects.create(
            user=user,
            total_amount=total_price,
            payment_method=payment_method,
            address=address_data,
            status='processing'
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price
        )
       
        product.quantity -= quantity
        product.save()


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

        serializer_data=OrderSerializer(order)
        return Response({'order':serializer_data.data})



    
# API view for creating  order
class OrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def post(self, request, *args, **kwargs):
        user = self.request.user
        address_id=request.data.get('address_id')
      
        items = CartItem.objects.filter(user=user)
        order_items = []
        total_amount = 0  

        if not items.exists():
            return Response({"error": "Cart is empty"})

        for item in items:
            product = item.product
            if product.quantity <= 0:
                return Response({"error": f"Product '{product.product_name}' is out of stock"})
            elif product.quantity < item.quantity:
                return Response({'error'  :f"{product.name} :Quantity exceeds available stock"})

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

        address_data = {}
        if address_id:
            try:
                address = Address.objects.get(user=user, id=address_id)
                address_data = {
                    "address_id": address.id,
                    "house_name": address.house_name,
                    "place": address.place,
                    "pin":address.pin,
                    "mobile_number":address.mobile_number
                }
            except Address.DoesNotExist:
                return Response({"error": "Address not found."})
        else:
            try:
                address = Address.objects.get(user=user, address_is_default=True)
                address_data = {
                    "address_id": address.id,
                    "house_name": address.house_name,
                    "place": address.place,
                    "pin":address.pin,
                    "mobile_number":address.mobile_number
                }
            except Address.DoesNotExist:
                return Response({"error": "Address not found."})


        payment_method = request.data.get('payment_method')
        if payment_method is None or payment_method not in ['cash_on_delivery', 'credit_card', 'paypal']:
            return Response({"error": "Invalid payment method"})


        order = Order.objects.create(
            user=user,
            total_amount=total_amount, 
            payment_method=payment_method,
            address=address_data,
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
        return self.queryset.filter(user=user)




# API endpoint for Detail view of Order.
class OrderDetailView(generics.RetrieveAPIView):
    queryset= Order.objects.all()
    serializer_class= OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.user != request.user:
                return Response({'error': "You don't have permission to access this order."})
            serializer = OrderSerializer(instance)
            items = OrderItem.objects.filter(order=instance)
            order_item_serializer = OrderItemSerializer(items, many=True)
       
            order_items_list = [] 
        
            for item in order_item_serializer.data:
                product = item['product']
                quantity = item['quantity']
                total_price = item['price']
            
                order_item_data = {
                    'product': product,
                    'quantity': quantity,
                    'total_price': total_price
                }
                order_items_list.append(order_item_data)
                print('order_items_list',order_items_list)
        
            response_data = {
                'order': serializer.data,
                'order_items': order_items_list
            }
            return Response(response_data)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'})

