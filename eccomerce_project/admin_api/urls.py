from django.urls import path
from admin_api import views

urlpatterns=[
    path('category/create/',views.CategoryCreateView.as_view(),name='category-list'),
    path('category/<int:pk>/',views.CategoryDetailView.as_view(),name='category-detail'),
    path('product/create/',views.ProductCreateView.as_view(),name='product-add'),
    path('product/list/',views.ProductListView.as_view(),name='product-list'),
    path('products/update/<int:pk>/',views.ProductDetailView.as_view(),name='product-detail'),
    path('order/list/',views.Admin_OrderListView.as_view(),name='order-list'),
    path('order/detail/<int:pk>/',views.Admin_OrderDetailView.as_view(),name='order-detail'),
    path('order/confirm/<int:pk>/',views.OrderConfirmView.as_view(),name='confirm-order'),
    path('user/list/',views.UserListView.as_view(),name='user-list'),
    path('user/delete/<int:pk>/',views.UserRemoveView.as_view(),name='user-delete'),
    path('email/',views.PramotionalMailView.as_view(),name='email')
    
    
]