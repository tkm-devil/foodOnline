from django.urls import path
from . import views

urlpatterns = [
    path('registerUser/', views.registerUser, name='registerUser'),
    path('registerVendor/', views.registerVendor, name='registerVendor'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('customer-dashboard/', views.customerDashboard, name='customerDashboard'),
    path('vendor-dashboard/', views.vendorDashboard, name='vendorDashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Email Verification Endpoints
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
]
