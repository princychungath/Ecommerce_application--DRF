from django.contrib import admin
from .models import Product,Category




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=['id','product_name','description','price','quantity','image']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=['id','category_name']