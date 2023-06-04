from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import product, categories, OrderProdukItem, Order
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exists')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else :
            messages.error(request, 'Username Or Password does not exists')
    context = {}
    return render(request, 'base/login.html', context)

def registerPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            # Membuat pengguna baru
            user = User.objects.create_user(username=username, password=password)
            
            # Lakukan sesuatu setelah pendaftaran berhasil
            return redirect('login')  # atau redirect ke halaman lain
            
        else:
            error_message = 'Password tidak cocok'
            return render(request, 'base/register.html', {'error_message': error_message})
            
    return render(request, 'base/register.html')

def logoutUser(request):
    logout(request)
    return redirect('home')

@login_required
def home(request):
    product_all = product.objects.all()
    categories_all = categories.objects.all()
    context = {'product_all' : product_all, 'categories_all' : categories_all}
    return render(request, 'base/home.html', context)

def produk_list(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' 
    product_all = product.objects.filter(Q(categories__categories__contains = q) | Q(name_product__icontains = q))
    categories_all = categories.objects.all()
    context = {'product_all' : product_all, 'categories_all' : categories_all}
    return render(request, 'base/produk_list.html', context)

class product_detail(DetailView):
    model = product
    context_object_name = 'product'
    template_name = 'base/product_detail.html'

def add_to_cart(request, slug):
    if request.user.is_authenticated:
        produk_item = get_object_or_404(product, slug=slug)
        order_produk_item, _ = OrderProdukItem.objects.get_or_create(
            produk_item=produk_item,
            user=request.user,
            ordered=False
        )
        order_query = Order.objects.filter(user=request.user, ordered=False)
        if order_query.exists():
            order = order_query[0]
            if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
                order_produk_item.quantity += 1
                order_produk_item.save()
                pesan = f"ProdukItem sudah diupdate menjadi: { order_produk_item.quantity }"
                messages.info(request, pesan)
                return redirect('product-detail', slug = slug)
            else:
                order.produk_items.add(order_produk_item)
                messages.info(request, 'ProdukItem pilihanmu sudah ditambahkan')
                return redirect('product-detail', slug = slug)
        else:
            tanggal_order = timezone.now()
            order = Order.objects.create(user=request.user, tanggal_order=tanggal_order)
            order.produk_items.add(order_produk_item)
            messages.info(request, 'ProdukItem pilihanmu sudah ditambahkan')
            return redirect('product-detail', slug = slug)
    else:
        return redirect('/login')