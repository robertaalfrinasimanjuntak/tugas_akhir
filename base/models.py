from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from djmoney.models.fields import MoneyField
from django.urls import reverse

PILIHAN_PEMBAYARAN = (
    ('P', 'Paypal'),
    ('S', 'Stripe'),
)

class categories(models.Model):
    categories = models.TextField(max_length=200)
    image = models.ImageField(upload_to='images/', null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.categories
    
def maxValueDiskon(value):
    if(value > 100 ):
        raise ValidationError("Diskon harus dibawah 100%")

class product(models.Model):
    name_product = models.CharField(max_length=200)
    categories = models.ForeignKey(categories, on_delete=models.SET_NULL, null=True)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='IDR')
    quantity = models.IntegerField()
    slug = models.SlugField(unique=True, null=True)
    diskon = models.IntegerField(validators=[maxValueDiskon], null=True);
    image = models.ImageField(upload_to='images/', null=True)
    description = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_product
    
    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={
            "slug": self.slug
            })
    
    def total_diskon_harga(self):
        return  self.price - ((self.diskon / 100) * self.price)
    
class checkout(models.Model):
    product = models.ForeignKey(product, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

class OrderProdukItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    produk_item = models.ForeignKey(product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.produk_item.nama_produk}"

    def get_total_harga_item(self):
        return self.quantity * self.produk_item.harga
    
    def get_total_harga_diskon_item(self):
        return self.quantity * self.produk_item.harga_diskon

    def get_total_hemat_item(self):
        return self.get_total_harga_item() - self.get_total_harga_diskon_item()
    
    def get_total_item_keseluruan(self):
        if self.produk_item.harga_diskon:
            return self.get_total_harga_diskon_item()
        return self.get_total_harga_item()
    
    def get_total_hemat_keseluruhan(self):
        if self.produk_item.harga_diskon:
            return self.get_total_hemat_item()
        return 0

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    produk_items = models.ManyToManyField(OrderProdukItem)
    tanggal_mulai = models.DateTimeField(auto_now_add=True)
    tanggal_order = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    alamat_pengiriman = models.ForeignKey('AlamatPengiriman', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

     
    def get_total_harga_order(self):
        total = 0
        for order_produk_item in self.produk_items.all():
            total += order_produk_item.get_total_item_keseluruan()
        return total
    
    def get_total_hemat_order(self):
        total = 0
        for order_produk_item in self.produk_items.all():
            total += order_produk_item.get_total_hemat_keseluruhan()
        return total

class AlamatPengiriman(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alamat_1 = models.CharField(max_length=100)
    alamat_2 = models.CharField(max_length=100)
    negara = models.CharField(max_length=100)
    kode_pos = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.alamat_1}"

    class Meta:
        verbose_name_plural = 'AlamatPengiriman'

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_option = models.CharField(choices=PILIHAN_PEMBAYARAN, max_length=1)
    charge_id = models.CharField(max_length=50)

    def __self__(self):
        return self.user.username
    
    def __str__(self):
        return f"{self.user.username} - {self.payment_option} - {self.amount}"
    
    class Meta:
        verbose_name_plural = 'Payment'