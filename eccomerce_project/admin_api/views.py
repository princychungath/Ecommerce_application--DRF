from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .models import Product,Category 
from user_api.models import Order,OrderItem
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import ProductSerializer,CategorySerializer,OrderconfirmSerializer
from user_api.serializers import OrderSerializer,OrderItemSerializer


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


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'message': 'Category is deleted'})


class ProductCreateView(generics.ListCreateAPIView):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product is Created"})
        else:
            return Response(serializer.errors)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({'message': 'Product is deleted'})


class Admin_OrderListView(generics.ListAPIView):
    queryset= Order.objects.all()
    serializer_class= OrderSerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]

class Admin_OrderDetailView(generics.RetrieveAPIView):
    queryset= Order.objects.all()
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

class OrderConfirmView(generics.UpdateAPIView):
    queryset= Order.objects.all()
    serializer_class= OrderconfirmSerializer
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]

    # def patch(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     print(instance.status)
    #     serializer_status = request.data.get('status')
    #     print(serializer_status)
    #     serializer = self.get_serializer(instance, data={'status': serializer_status}, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         print(instance.status,serializer_status)
    #         if instance.status != serializer_status:
    #             return Response({'message': 'Status updated successfully'})
    #         return Response({'message': 'Status not updated'})

    #     return Response(serializer.errors)

    # def patch(self, request, *args, **kwargs):
    #     try:
    #         instance = self.get_object()
    #         instance_status = instance.status
    #         print(instance.status)
    #         serializer = self.get_serializer(instance)
    #         serializer.save()
    #         serializer_status = serializer.data.get('status')
    #         print(serializer.data)
            
    #         if instance_status != serializer_status:
    #             return Response({'message': 'updated status'})
    #         return Response({'message': 'status not updated'})
    #     except Order.DoesNotExist:
    #         return Response({'message': 'no order'})


   











           