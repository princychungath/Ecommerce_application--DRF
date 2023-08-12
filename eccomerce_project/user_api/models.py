from django.db import models
from django.contrib.auth.models import AbstractUser
from admin_api.models import Product


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)



class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    house_name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)
    address_is_default = models.BooleanField(default=True)



class Order(models.Model):
    user =models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_choice=[
        ('cash_on_delivery', 'Cash on Delivery'),
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
    ]

    payment_method = models.CharField(max_length=20,choices=payment_choice)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    status_choices = [
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='processing')



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price= models.DecimalField(max_digits=10, decimal_places=2)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='static/profile_images/')
    mobile_number = models.CharField(max_length=15)
    created_at=models.DateTimeField(auto_now_add=True)