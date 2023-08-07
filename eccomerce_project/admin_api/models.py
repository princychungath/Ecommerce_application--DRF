from django.db import models

class Category(models.Model):
    category_name = models.CharField(max_length=100)  


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='static/images/')
    categories = models.ManyToManyField(Category)


