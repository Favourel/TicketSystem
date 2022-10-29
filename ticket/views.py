# Create your views here.
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.hashers import check_password
from .models import *
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.views.generic import ListView, DetailView, FormView
from django.contrib import messages
from .filters import ProductFilter
from django.http import JsonResponse
from .forms import *
from .mixins import AjaxFormMixin

import json


class Cart(View):
    def get(self, request):
        productList = list(request.session.get('cart').keys())
        customer_id = request.session.get('customer')
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            phone = customer.phone
            u_form = OrderForm(instance=customer)
        else:
            u_form = 7575
        if request.GET.get('increase'):
            pId = request.GET.get('increase')
            products = request.session.get('cart')
            products[pId] += 1
            request.session['cart'] = products
            messages.success(request, f'Item quantity has been updated!')
            return redirect('cart')

        if request.GET.get('decrease'):
            pId = request.GET.get('decrease')
            products = request.session.get('cart')
            print(products[pId])
            if products[pId] > 1:
                products[pId] -= 1
                request.session['cart'] = products
                productList = list(request.session.get('cart').keys())
                messages.success(request, f'"Item quantity has been updated!')
                return redirect('cart')
            else:
                del products[pId]
                request.session['cart'] = products
                productList = list(request.session.get('cart').keys())
                messages.success(request, f'"Item has been deleted!')
                return redirect('cart')

        allProduc = Product.getProductById(productList)
        return render(request, 'cart.html', {"allProduct": allProduc, "u_form": u_form})


class Checkout(View):
    def get(self, request):
        return redirect('cart')

    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        cart = request.session.get('cart')
        products = Product.getProductById(list(cart.keys()))
        customer = request.session.get('customer')
        print(address, phone, cart, products, customer)

        for product in products:
            newOrder = Order(
                product=product,
                customer=Customer(id=customer),
                quantity=cart[str(product.id)],
                price=product.price,
                address=address,
                phone=phone,
            )
            newOrder.save()

        request.session['cart'] = {}
        return redirect('order')


def post_review(request):
    customer = request.session.get('customer')
    if request.method == 'POST':
        message = request.POST['message']
        message_subject = request.POST['message_subject']

        user = Review.objects.create(customer_name=Customer(id=customer),
                                     message=message,
                                     message_subject=message_subject)
        user.save()
        return redirect('/')
    return render(request, 'home.html', {})


class Home(View):
    def get(self, request):
        categories = Category.getAllCategory().order_by('-id')
        cart = request.session.get('cart')
        products = Product.getAllProduct().order_by('-id')

        myFilter = ProductFilter(request.GET, queryset=products)
        products = myFilter.qs

        paginator = Paginator(products, 8)
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

        reviews = Review.objects.all().order_by("?")
        paginator = Paginator(reviews, 3)
        page_number = request.GET.get('page')
        reviews = paginator.get_page(page_number)

        name = request.session.get('customer')
        customer_user = Customer.objects.filter()
        customer_name = Customer(id=name)

        reserve = Reservation.objects.all()

        if request.GET.get('id'):
            filterProductById = Product.objects.get(id=int(request.GET.get('id')))
            return render(request, 'productDetail.html', {"product": filterProductById,
                                                          })

        if not cart:
            request.session['cart'] = {}

        if request.GET.get('category_id'):
            filterProduct = Product.getProductByFilter(request.GET['category_id'])
            return render(request, 'home.html', {"products": filterProduct,
                                                 'reviews': reviews,
                                                 "categories": categories,
                                                 })

        return render(request, 'home.html', {"products": products,
                                             'reviews': reviews,
                                             'customer_name': customer_name,
                                             'customer_user': customer_user,
                                             'myFilter': myFilter,
                                             'reserve': reserve,
                                             "categories": categories,
                                             'name': name})

    def post(self, request):

        product = request.POST.get('product')

        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                cart[product] = quantity + 1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        print(cart)
        request.session['cart'] = cart
        messages.success(request, 'Your Cart has been updated!')
        return redirect('cart')


class Login(View):
    return_url = None

    def get(self, request):
        Login.return_url = request.GET.get('return_url')
        return render(request, 'login.html')

    def post(self, request):
        userData = request.POST
        customerEmail = Customer.emailExits(userData["email"])
        print(customerEmail)

        if customerEmail:
            if check_password(userData["password"], customerEmail.password):
                request.session["customer"] = customerEmail.id
                if Login.return_url:
                    print(customerEmail)
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url = None
                    print(customerEmail)
                    return redirect('home')
            else:
                return render(request, 'login.html', {"userData": userData, "error": "Email or password doesn't match"})
        else:
            return render(request, 'login.html', {"userData": userData, "error": "Email or password doesn't match"})


def logout(request):
    request.session.clear()
    return redirect('home')


class OrderView(View):
    def get(self, request):
        customer_id = request.session.get('customer')
        orders = Order.objects.filter(customer=customer_id).order_by("-date").order_by("-id")
        print(orders)
        customer_id = request.session.get('customer')
        orders = Order.objects.filter(customer=customer_id).order_by("-date").order_by("-id")
        for order in orders:
            template = get_template('email_template.html').render({'name': order.customer.name,
                                                                   'order': order.product,
                                                                   'quantity': order.quantity,
                                                                   'price': order.price,
                                                                   'address': order.address})
            email = EmailMessage(
                'THANKS! for purchasing from item7.com',
                template,
                settings.EMAIL_HOST_USER,
                (order.customer.email, 'favourelodimuor16@gmail.com'),
            )
            email.fail_silently = False
            email.content_subtype = 'html'
            email.send()
            return redirect('home')
        return render(request, 'order.html', {"orders": orders})


def orders_view(request):
    try:
        customer_id = request.session.get('customer')
        customer = Customer.objects.get(id=customer_id)
        orders = Order.objects.filter(customer=customer_id).order_by("-date").order_by("-id")
        print(orders)
        return render(request, 'order.html', {"orders": orders, "customer": customer})

    except ObjectDoesNotExist:
        messages.info(request, 'You are not authenticated. Login is required')
        return redirect('home')


class Signup(View):

    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        userData = request.POST
        # validate
        error = self.validateData(userData)
        if error:
            return render(request, 'signup.html', {"error": error, "userData": userData})
        else:
            if Customer.emailExits(userData['email']):
                error["emailExits_error"] = "Email Already Exists"
                return render(request, 'signup.html', {"error": error, "userData": userData})
            else:
                customer = Customer(
                    name=userData['name'],
                    email=userData['email'],
                    phone=userData['phone'],
                    password=make_password(userData['password']),
                )
                customer.save()
                return redirect('login')

    # Validate form method
    def validateData(self, userData):
        error = {}
        if not userData['name'] or not userData['email'] or not userData['phone'] or not userData['password'] or not \
                userData['confirm_password']:
            error["field_error"] = "All field must be required"
        elif len(userData['password']) < 8 and len(userData['confirm_password']) < 8:
            error['minPass_error'] = "Password must be 8 characters"
        elif len(userData['name']) > 30 or len(userData['name']) < 5:
            error["name_error"] = "Name must be 5-30 character"
        elif len(userData['phone']) != 11:
            error["phoneNumber_error"] = "Phone number must be 11 characters."
        elif userData['password'] != userData['confirm_password']:
            error["notMatch_error"] = "Password doesn't match"

        return error


def about_view(request):
    return render(request, 'about.html', {})


def reservation_review(request):
    reservation_queryset = Reservation.objects.all()
    if len(reservation_queryset) > 3:
        if request.method == 'POST':
            name = request.POST['full_name']
            phone = request.POST['phone']
            email = request.POST['email']
            people = request.POST['people']
            date = request.POST['date']
            time = request.POST['time']

            reservation = Reservation.objects.create(full_name=name,
                                                     phone=phone,
                                                     email=email,
                                                     people=people,
                                                     date=date,
                                                     time=time)
            reservation.save()

            # template = get_template('reservation_message.html').render({'name': name})
            # email = EmailMessage(
            #     'SUCCESSFUL RESERVATION PLACEMENT ON ITEM7.COM',
            #     template,
            #     settings.EMAIL_HOST_USER,
            #     [email],
            # )
            # email.fail_silently = False
            # email.content_subtype = 'html'
            # email.send()
            messages.success(request, 'RESERVATION HAS BEEN SUCCESSFULLY PLACED')
            return redirect('/')
        return render(request, 'home.html', {})
    else:
        messages.warning(request, 'Reservation slot has been filled!')
        return redirect('home')


class JoinFormView(AjaxFormMixin, FormView):
    form_class = JoinForm
    template_name = 'home.html'
    success_url = '/home/'

    def form_invalid(self, form):
        response = super(JoinFormView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(JoinFormView, self).form_valid(form)
        if self.request.is_ajax():
            print(form.cleaned_data)
            data = {
                'message': "Successfully submitted form data."
            }
            return JsonResponse(data)
        else:
            return response
