from django.urls import path
from .views import product_detail
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('update_quantity/', views.update_quantity, name='update_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout_page/', views.checkoutPage, name='checkout_page'),
    path('logout/', views.logoutUser, name="logout"),
    path('cart/', views.cartList, name="cart"),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('', views.home, name="home"),
    path('list-product/', views.produk_list, name="product-list"),
    path('list-product/<slug>', product_detail.as_view(), name='product-detail'),
]
