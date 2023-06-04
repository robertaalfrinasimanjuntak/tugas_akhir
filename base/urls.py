from django.urls import path
from .views import product_detail
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('logout/', views.logoutUser, name="logout"),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('', views.home, name="home"),
    path('list-product/', views.produk_list, name="product-list"),
    path('list-product/<slug>', product_detail.as_view(), name='product-detail'),
]
