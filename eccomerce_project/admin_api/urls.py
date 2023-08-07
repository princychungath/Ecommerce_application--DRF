from django.urls import path
from admin_api import views

urlpatterns=[
    path('category/create/',views.CategoryCreateView.as_view(),name='category-list'),
    path('category/<int:pk>/',views.CategoryDetailView.as_view(),name='category-detail'),
    path('product/create/',views.ProductCreateView.as_view(),name='product-list'),
    path('products/<int:pk>/',views.ProductDetailView.as_view(),name='product-detail'),
    path('order/list/',views.Admin_OrderListView.as_view(),name='order-list'),
    path('order/detail/<int:pk>/',views.Admin_OrderDetailView.as_view(),name='order-detail'),


]