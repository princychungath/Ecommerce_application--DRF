from django.contrib import admin
from .models import User,Cart,Order,OrderItem,Profile

admin.site.register(User)
admin.site.register(Cart)
admin.site.register(Profile)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=['user','created_at','total_amount','status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display=['order','product','quantity','price']