from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .models import Product,Category 
from user_api.models import Order,OrderItem,User
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import ProductSerializer,CategorySerializer,OrderconfirmSerializer,UserListSerilizer
from user_api.serializers import OrderSerializer,OrderItemSerializer
from user_api.pagination import MyCustomPagination

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


#listing all users
class  UserListView(generics.ListAPIView):
    queryset=User.objects.all().order_by('username')
    serializer_class= UserListSerilizer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]



#removing Users
class UserRemoveView(generics.DestroyAPIView):
    queryset=User.objects.all()
    serializer_class= UserListSerilizer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]

    def delete(self,request,*args,**kwargs):
        response=super().delete(self,request,*args,**kwargs)
        return Response({'message','User is deleted'})


#view for adding new categories
class CategoryCreateView(generics.ListCreateAPIView):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]
    
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Category is Added"})
        else:
            return Response(serializer.errors)


#detailview for category- update,delete 
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'message': 'Category is deleted'})



#view for creating new products
class ProductCreateView(generics.ListCreateAPIView):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]
    pagination_class=MyCustomPagination

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product is Created"})
        else:
            return Response(serializer.errors)


#detailview of products
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.prefetch_related('categories').all()
    serializer_class = ProductSerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'message': 'Product is deleted'})



#view for listing all orders
class Admin_OrderListView(generics.ListAPIView):
    queryset= Order.objects.all().select_related('user', 'profile')
    serializer_class= OrderSerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]
    pagination_class=MyCustomPagination


# detailview for orders
class Admin_OrderDetailView(generics.RetrieveAPIView):
    queryset= Order.objects.all().select_related('user', 'profile')
    serializer_class= OrderSerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = OrderSerializer(instance)
            items = OrderItem.objects.filter(order=instance)
            order_item_serializer = OrderItemSerializer(items, many=True)
            response_data = {
                'order': serializer.data,
                'order_items': order_item_serializer.data
            }
            return Response(response_data)
        except Order.DoesNotExist:
            return Response({'error':'Order not found'})



# UpdateAPIView for order-status update , passing statusupdates through email
class OrderConfirmView(generics.UpdateAPIView):
    queryset= Order.objects.all().select_related('user', 'profile')
    serializer_class= OrderconfirmSerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_status=instance.status
        serializer_status = request.data.get('status')
        serializer = self.get_serializer(instance, data={'status': serializer_status}, partial=True)
        if serializer.is_valid():
            serializer.save()
            if instance_status != serializer_status:
                context={
                    'order_id':instance.id,
                    'status':serializer_status
                }
                subject="Order Status Updated"
                email_to=[instance.user.email]
                html_content=render_to_string('status_update.html',context)
                email=EmailMultiAlternatives(subject,html_content,settings.DEFAULT_FROM_EMAIL,email_to)
                email.attach_alternative(html_content,"text/html")
                email.send()
                return Response({'message': 'Status updated successfully'})
            return Response({'message': 'Status not updated'})
        return Response(serializer.errors)


   











           