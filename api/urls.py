from django.contrib import admin
from django.urls import path, include
from base.views.product_views import product_list_create, product_detail, product_update_stock, upload_product_image, insert_sample_products
from .settings import MEDIA_ROOT, MEDIA_URL
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from base.views.image_views import images_in_folder

urlpatterns = [
    path('admin/', admin.site.urls),

    # Products (function-based)
    path('api/products/', product_list_create, name='product-list-create'),
    path('api/products/<int:pk>/', product_detail, name='product-detail'),
    path('api/products/<int:pk>/stock/', product_update_stock, name='product-update-stock'),
    path('api/products/<int:pk>/image/', upload_product_image, name='product-upload-image'),
    path('api/products/insert-sample-products/', insert_sample_products, name='insert-sample-products'),

    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('base.urls.user_urls')),
    path('api/orders/', include('base.urls.order_urls')),
    path("api/images/", images_in_folder, name="list-folder-images"),
]


urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
