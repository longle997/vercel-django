from django.contrib import admin

# Register your models here.
from base.models import *


admin.site.register(Product)
admin.site.register(Review)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(ShippingAddress)
