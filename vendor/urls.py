from django.urls import path
from . import views  # Import views from vendor app

urlpatterns = [
    path("profile/", views.vendor_profile, name="vendor_profile"),
    path("earnings/", views.vendor_earnings, name="vendor_earnings"),
    path("statements/", views.vendor_statements, name="vendor_statements"),
    path("change-password/", views.change_password, name="change_password"),

    path("menu-builder/", views.menu_builder, name="menu_builder"),
    path('menu-builder/add/', views.add_menu_item, name='add_menu_item'),
    path('menu-builder/edit/<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),
    path('menu-builder/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),

    path("orders/", views.vendor_orders, name="vendor_orders"),
    path("orders/<int:order_id>/", views.order_details, name="order_details"),
    path("orders/<int:order_id>/update/<str:new_status>/", views.update_order_status, name="update_order_status"),
]