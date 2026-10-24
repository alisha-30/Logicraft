from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.home_view, name='dashboard'),
    path('inventory/', views.inventory_catalog_view, name='inventory_catalog'),
    path('track/', views.track_shipment_view, name='track_shipment'),
    path('shipments/dispatch/', views.shipment_dispatch_view, name='shipment_dispatch'),
    path('shipments/new/', views.shipment_dispatch_view, name='shipment_create'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/logout/', views.logout_view, name='logout'),
]
