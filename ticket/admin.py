from django.contrib import admin

from django.contrib import admin
from .models import Product
from .models import Reservation
from .models import Customer
from .models import Order
from .models import Review
from .models import Category


class AdminCustomer(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'date_added']


class AdminProduct(admin.ModelAdmin):
    list_display = ['name', 'price', 'date']


class AdminReservation(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'people', 'date', 'time', 'date_added']


class AdminOrder(admin.ModelAdmin):
    list_display = ['customer', 'product', 'quantity', 'price', 'date_added', 'address', 'phone']


class AdminReview(admin.ModelAdmin):
    list_display = ['customer_name', 'message', 'message_subject', 'date_added']


admin.site.register(Product, AdminProduct)
admin.site.register(Category)
admin.site.register(Reservation, AdminReservation)
admin.site.register(Customer, AdminCustomer)
admin.site.register(Order, AdminOrder)
admin.site.register(Review, AdminReview)