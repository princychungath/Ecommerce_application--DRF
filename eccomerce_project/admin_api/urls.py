from django.urls import path
from admin_api import views

urlpatterns=[
    path('category/create/',views.CategoryCreateView.as_view(),name='category-create'),
    path('category/list/',views.CategoryListView.as_view(),name='category-list'),
    path('category/detail/<int:pk>/',views.CategoryDetailView.as_view(),name='category-detail'),
    path('category/update/<int:pk>/',views.CategoryUpdate.as_view(),name='category-update'),

    path('product/create/',views.ProductCreateView.as_view(),name='product-add'),
    path('product/list/',views.ProductListView.as_view(),name='product-list'),
    path('products/detail/<int:pk>/',views.ProductDetailView.as_view(),name='product-detail'),
    path('products/update/<int:pk>/',views.ProductUpdateView.as_view(),name='product-update'),
    path('products/delete/<int:pk>/',views.ProductRemoveView.as_view(),name='product-delete'),
    
    path('user/list/',views.UserListView.as_view(),name='user-list'),
    path('user/delete/<int:pk>/',views.UserRemoveView.as_view(),name='user-delete'),
    
    path('order/list/',views.Admin_OrderListView.as_view(),name='order-list'),
    path('order/detail/<int:pk>/',views.Admin_OrderDetailView.as_view(),name='order-detail'),
    path('order/confirm/<int:pk>/',views.OrderConfirmView.as_view(),name='confirm-order'),

    path('email/',views.PramotionalMailView.as_view(),name='email') 
    
]