from django.db import transaction
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status

from ..models import Order, ShippingAddress, OrderItem
from ..serializers import OrderSerializer, OrderItemSerializer, OrderReadSerializer, UserSerializer, ShippingSerializer

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
@authentication_classes([JWTAuthentication])
def order_list_create(request):
    user = request.user
    user_serializer = UserSerializer(user, many=False)
    if request.method == "GET":
        order_records = Order.objects.filter(user=user_serializer.data.get("id"))
        response = [OrderReadSerializer(rec).data for rec in order_records]
        return Response(response, status=status.HTTP_200_OK)
    elif request.method == "POST":
        with transaction.atomic():
            try:
                order_data = request.data
                order_data['user'] = user_serializer.data.get("id")
                order_serializer = OrderSerializer(data=order_data)
                if order_serializer.is_valid():
                    order = order_serializer.save()
                    print(f"Successfully create new order with id {order.id}")

                order_items_payload = request.data.get("orderItems")
                for item in order_items_payload:
                    item['order'] = order.id
                    order_item_serializer = OrderItemSerializer(data=item)
                    if order_item_serializer.is_valid():
                        order_item = order_item_serializer.save()
                        print(f"Successfully create new order item with id {order_item._id}")
                
                shipping_address_payload = request.data.get("shippingAddress")
                shipping_address_payload["shippingPrice"] = request.data.get("shippingPrice")
                shipping_address_payload['order'] = order.id
                shipping_address_serializer = ShippingSerializer(data=shipping_address_payload)
                if shipping_address_serializer.is_valid():
                    shipping_address = shipping_address_serializer.save()
                    print(f"Successfully create shipping item with id {shipping_address._id}")
                
                return Response(OrderReadSerializer(order).data, status.HTTP_201_CREATED)
            except Exception as e:
                print(e)
                transaction.rollback()
                return Response("Saving order internal server error!", status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_details(request, pk: int):
    try:
        order_rec = Order.objects.get(id=pk)
        shipping_rec = ShippingAddress.objects.get(order_id=order_rec.id)
        order_data = OrderReadSerializer(order_rec).data
        shipping_data = ShippingSerializer(shipping_rec).data
        order_item_recs = OrderItem.objects.filter(order_id=order_rec.id)
        order_item_data = [OrderItemSerializer(item).data for item in order_item_recs]
        response = {
            **order_data,
            **shipping_data,
            "order_items": order_item_data
        }
        return Response(response, status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response(f"Error fetching order with id {pk}", status.HTTP_500_INTERNAL_SERVER_ERROR)
