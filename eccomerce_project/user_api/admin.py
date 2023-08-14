from django.contrib import admin
from .models import User,CartItem,Order,OrderItem,Address,Profile

admin.site.register(User)
admin.site.register(CartItem)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=['id','user','created_at','total_amount','address','status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display=['order','product','quantity','price']

@admin.register(Address)
class OrderAdmin(admin.ModelAdmin):
    list_display=['id','user','house_name','place','pin','mobile_number','address_is_default']

@admin.register(Profile)
class OrderAdmin(admin.ModelAdmin):
    list_display=['id','user','profile_picture','mobile_number','created_at']

