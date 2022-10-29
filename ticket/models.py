from django.db import models
from django.utils import timezone
import datetime
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name

    @staticmethod
    def emailExits(userEmail):
        try:
            email = Customer.objects.get(email=userEmail)
            return email
        except:
            return False

    @staticmethod
    def getCustomer(userEmail):
        try:
            name = Customer.objects.filter(name=userEmail)
            return name
        except:
            return False


class Category(models.Model):
    name = models.CharField(max_length=70, null=True, blank=True, default=1)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @staticmethod
    def getAllCategory():
        return Category.objects.all()


class Product(models.Model):
    name = models.CharField(max_length=220, null=True, blank=True)
    price = models.FloatField(default=0, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=2)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='upload/products', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name

    # All Product get
    @staticmethod
    def getAllProduct():
        return Product.objects.all()

    # Filter Product By Category
    @staticmethod
    def getProductByFilter(category_id):
        if category_id:
            return Product.objects.filter(category=category_id)
        else:
            return Product.getAllProduct()

    @staticmethod
    def getProductById(productList):
        return Product.objects.filter(id__in=productList)


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=1, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    completed = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return str(self.customer)


class Review(models.Model):
    customer_name = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    message_subject = models.CharField(max_length=255, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class Reservation(models.Model):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    people = models.CharField(max_length=255, blank=True, null=True)
    date = models.CharField(max_length=15, blank=True, null=True)
    time = models.CharField(max_length=15, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=True)


    @staticmethod
    def timeExits(reservationTime):
        try:
            time = Reservation.objects.get(time=reservationTime)
            return time
        except:
            return False

