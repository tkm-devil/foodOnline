from django.urls import path
from . import views

urlpatterns = [
    path('registerUser/', views.registerUser, name='registerUser'),
    # path('registerRestaurant/', views.registerRestaurant, name='registerRestaurant'),
    path('login/', views.login_view, name='login_view'),
    # path('logoutUser/', views.logoutUser, name='logoutUser'),
]
