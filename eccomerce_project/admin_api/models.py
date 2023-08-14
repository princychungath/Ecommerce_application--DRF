from django.db import models

class Category(models.Model):
    category_name = models.CharField(max_length=100)
    created_user= models.ForeignKey('user_api.User', on_delete=models.CASCADE,related_name='created_categories')
    updated_user = models.ForeignKey('user_api.User', on_delete=models.CASCADE,related_name='updated_categories')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 


class Product(models.Model):
    created_user= models.ForeignKey('user_api.User', on_delete=models.CASCADE,related_name='created_created')
    updated_user = models.ForeignKey('user_api.User', on_delete=models.CASCADE,related_name='updated_created')
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='static/Product_images/')
    categories=models.ManyToManyField(Category)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
