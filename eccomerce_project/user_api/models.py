from django.db import models
from django.contrib.auth.models import AbstractUser
from admin_api.models import Product

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

class Cart(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    house_name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_choice=[('cash_on_delivery','cash_on_delivery')]
    payment_method = models.CharField(max_length=20,choices=payment_choice,default='cash_on_delivery')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
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
