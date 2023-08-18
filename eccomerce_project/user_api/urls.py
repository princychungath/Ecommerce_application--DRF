from django.urls import path
from user_api import views

urlpatterns=[
    path('user/register/', views.RegisterUser.as_view(), name='user-register'),
    path('user/resetpassword/mail/',views.SendPasswordResetEmail.as_view(),name='resetpassword-mail'),
    path('reset/password/',views.PasswordResetView.as_view(), name='password-reset'),

    path('Product/list/',views.ProductList.as_view(), name='Product-list'),
    path('Product/detail/<int:pk>/',views.ProductDetail.as_view(), name='Product-detail'),

    path('cart/add/',views.CartAddView.as_view(), name='cart_add'),
    path('cart/list/',views.CartListView.as_view(), name='cart-list'),
    path('cart/update/<int:pk>/',views.CartUpdateView.as_view(), name='cart-update'),
    path('cart/delete/<int:pk>/',views.CartDeleteView.as_view(), name='cart-update'),

    path('address/create/',views.AddressCreateView.as_view(),name='address-create'),
    path('address/list/',views.AddresslistView.as_view(),name='address-list'),
    path('address/detail/<int:pk>/',views.AddressDetailView.as_view(),name='address-detail'),
    path('address/update/<int:pk>/',views.AddressUpdateView.as_view(),name='address-update'),
    path('address/delete/<int:pk>/',views.AddressDestroyView.as_view(),name='address-delete'),


    path('profile/create/',views.ProfileCreateView.as_view(),name='profile-create'),
    path('profile/',views.ProfileView.as_view(),name='profile-view'),    
    path('profile/update/<int:pk>/',views.ProfileUpdateView.as_view(),name='profile-update'),
    path('profile/delete/<int:pk>/',views.ProfileDestroyView.as_view(),name='profile-delete'),
    

    path('order/add/',views.OrderCreateView.as_view(), name='order-add'),
    path('order/list/',views.OrderListView.as_view(), name='order-lists'),
    path('order/detail/<int:pk>/',views.OrderDetailView.as_view(), name='order-detail'),
    path('order/now/',views.BuyNowView.as_view(), name='order-now')
    
    
]