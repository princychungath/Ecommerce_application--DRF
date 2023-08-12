from django.contrib import admin
from .models import User,CartItem,Order,OrderItem,Address,Profile

admin.site.register(User)
admin.site.register(CartItem)
admin.site.register(Address)
admin.site.register(Profile)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=['id','user','created_at','total_amount','address','status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display=['order','product','quantity','price']