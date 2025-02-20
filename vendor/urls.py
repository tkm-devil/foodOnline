from django.urls import path
from . import views  # Import views from vendor app

urlpatterns = [
    # path("dashboard/", views.vendorDashboard, name="vendorDashboard"),
    path("profile/", views.vendor_profile, name="vendor_profile"),
    path("menu-builder/", views.menu_builder, name="menu_builder"),
    path("orders/", views.vendor_orders, name="vendor_orders"),
    path("earnings/", views.vendor_earnings, name="vendor_earnings"),
    path("statements/", views.vendor_statements, name="vendor_statements"),
    path("change-password/", views.change_password, name="change_password"),
]