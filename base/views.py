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

def update_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        quantity = int(request.POST.get('quantity'))

        if action == 'increase':
            quantity += 1
        elif action == 'decrease':
            quantity -= 1
            
        product = OrderProdukItem.objects.get(id=product_id)
        product.quantity = quantity
        product.save()

        # Lakukan logika penyimpanan ke database sesuai kebutuhan

        return redirect('/cart', product_id=product_id)

    return redirect('/cart')

def checkout(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        alamat = request.POST.get('alamat')
        negara = request.POST.get('negara')
        kode_pos = request.POST.get('kode_pos')
        payment = request.POST.get('payment')
            
        order = Order.objects.get(id=order_id)
        order_item = OrderProdukItem.objects.get(user=request.user)
        order.alamat = alamat
        order.negara = negara
        order.kode_pos = kode_pos
        order.payment = payment
        order.ordered = True
        order_item.ordered = True
        order.save()
        order_item.save()

        # Lakukan logika penyimpanan ke database sesuai kebutuhan

        return redirect('/checkout_page', order_id=order_id)

    return redirect('/checkout_page')

def checkoutPage(request):
    order_status = Order.objects.filter(user=request.user, ordered=False)
    order_item = OrderProdukItem.objects.filter(user=request.user, ordered=False)
    order_count = order_item.count()
    total_belanja = 0
    for order in order_item:
        total_belanja += order.quantity * (order.produk_item.price - ((order.produk_item.diskon / 100) * order.produk_item.price))
    total_belanja_dipotong_ppn = total_belanja - (total_belanja * (10 / 100))
    context = {'order_status': order_status, 'order_item' : order_item, 'total_belanja': total_belanja, 'total_belanja_dipotong_ppn' : total_belanja_dipotong_ppn, 'order_count' : order_count}
    if order_status.ordered == True:
        return redirect('cart')   
    return render(request, 'base/checkout.html', context)

def cartList(request):
    order_item = OrderProdukItem.objects.filter(user=request.user, ordered=False)
    total_belanja = 0
    for order in order_item:
        total_belanja += order.quantity * (order.produk_item.price - ((order.produk_item.diskon / 100) * order.produk_item.price))
    total_belanja_dipotong_ppn = total_belanja - (total_belanja * (10 / 100))
    context = {'order_item' : order_item, 'total_belanja': total_belanja, 'total_belanja_dipotong_ppn' : total_belanja_dipotong_ppn}
    return render(request, 'base/cart.html', context)

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