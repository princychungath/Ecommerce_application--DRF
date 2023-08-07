from django.contrib import admin
from .models import User,CartItem,Order,OrderItem,Profile,Cart

admin.site.register(User)
admin.site.register(CartItem)
admin.site.register(Profile)
admin.site.register(Cart)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=['user','created_at','total_amount','status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display=['order','product','quantity','price']