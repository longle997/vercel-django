from django.urls import path
from base.views import order_views

urlpatterns = [
    path('', order_views.order_list_create, name="order_list"),
    path('<pk>', order_views.order_details, name="order_details")
]