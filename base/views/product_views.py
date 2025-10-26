from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from ..models import Product
from ..serializers import ProductSerializer, ProductUpdateSerializer
from ..signals import seed_products_if_empty


# Helper: small paginator you can reuse
class SmallPaginator(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])   # Anyone can read; auth required to POST
def product_list_create(request):
    """
    GET  /api/products/?q=airpods&brand=Apple&category=Electronics&ordering=price
    POST /api/products/
    """
    if request.method == 'GET':
        qs = Product.objects.all()

        # ---- optional filters/search ----
        q = request.query_params.get('q')
        brand = request.query_params.get('brand')
        category = request.query_params.get('category')
        ordering = request.query_params.get('ordering')  # e.g. "price" or "-price"

        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q) |
                Q(brand__icontains=q) |
                Q(category__icontains=q)
            )
        if brand:
            qs = qs.filter(brand__iexact=brand)
        if category:
            qs = qs.filter(category__iexact=category)
        if ordering:
            qs = qs.order_by(ordering)

        # ---- pagination ----
        paginator = SmallPaginator()
        page = paginator.paginate_queryset(qs, request)
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # POST
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])   # tighten as needed (e.g., IsAdminUser for writes)
def product_detail(request, pk: int):
    """
    GET    /api/products/<pk>/
    PUT    /api/products/<pk>/
    PATCH  /api/products/<pk>/
    DELETE /api/products/<pk>/
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'GET':
        return Response(ProductSerializer(product).data)

    if request.method == 'PUT':
        serializer = ProductUpdateSerializer(product, data=request.data)  # full update
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductUpdateSerializer(product).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_update_stock(request, pk: int):
    """
    PATCH /api/products/<pk>/stock/
    Body: { "countInStock": 7 }
    """
    product = get_object_or_404(Product, pk=pk)
    count = request.data.get('countInStock', None)
    if count is None:
        return Response({"detail": "countInStock is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        count = int(count)
    except (TypeError, ValueError):
        return Response({"detail": "countInStock must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

    if count < 0:
        return Response({"detail": "countInStock must be ≥ 0."}, status=status.HTTP_400_BAD_REQUEST)

    product.countInStock = count
    product.save(update_fields=['countInStock'])
    return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])  # tighten to IsAdminUser if only admins can upload
@parser_classes([MultiPartParser, FormParser])  # enables request.FILES
def upload_product_image(request, pk):
    """
    Upload/replace the image for a product.
    POST /api/products/<pk>/upload-image/
    Body: multipart/form-data with field 'image'
    """
    data = request.data
    product = get_object_or_404(Product, pk=pk)

    file_obj = request.FILES.get("image")
    if not file_obj:
        return Response({"detail": "No file provided. Use field name 'image'."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Optionally: delete old file if replacing (uncomment if desired)
    # if product.image and product.image.name:
    #     product.image.delete(save=False)

    # Save the new file to the ImageField
    product.image.save(file_obj.name, file_obj, save=True)

    return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def insert_sample_products(request):
    seed_products_if_empty()
    qs = Product.objects.all()
    paginator = SmallPaginator()
    page = paginator.paginate_queryset(qs, request)
    serializer = ProductSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)
