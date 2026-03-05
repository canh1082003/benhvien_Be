from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'assets', views.AssetViewSet, basename='asset')
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'categories', views.AssetCategoryViewSet, basename='category')
router.register(r'manufacturers', views.ManufacturerViewSet, basename='manufacturer')
router.register(r'vendors', views.VendorViewSet, basename='vendor')

urlpatterns = [
    path('', include(router.urls)),
    path('admin-bridge/', views.admin_bridge_view, name='admin-bridge'),
]
