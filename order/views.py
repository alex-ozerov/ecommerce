from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.urls import reverse
from product.models import Product
from .models import Order, OrderProduct, ShopCart
from .forms import OrderForm
from product.views import setup_cart


# Create your views here.

def get_cart_items(self):
    cart = self.request.session['cart']
    products = Product.objects.filter(slug__in=cart.keys())
    order_list = [{'product': product, 'quantity': cart[product.slug],
                   'total_price': product.price * cart[product.slug]}
                  for product in products]
    return order_list


class CartAdd(View):
    def get(self, request, *args, **kwargs):
        cart = request.session['cart']
        try:
            cart[self.kwargs['slug']] += self.kwargs['quantity']
        except KeyError:
            cart[self.kwargs['slug']] = 1
        request.session.modified = True

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


class CartRemove(View):
    def get(self, request, *args, **kwargs):
        cart = request.session['cart']
        try:
            cart[self.kwargs['slug']]
        except KeyError:
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

        if self.kwargs['quantity'] < cart[self.kwargs['slug']]:
            cart[self.kwargs['slug']] -= self.kwargs['quantity']
        else:
            del cart[self.kwargs['slug']]
        request.session.modified = True

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


class CartCleanAll(View):
    def get(self, request, *args, **kwargs):
        request.session['cart'] = {}
        request.session.modified = True

        return redirect(reverse('product-list'))


class CartView(ListView):
    template_name = 'cart_page.html'

    def get_queryset(self):
        order_list = self.kwargs['order_list'] = get_cart_items(self)
        return order_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_price'] = sum([item['total_price'] for item in self.kwargs['order_list']])
        context['cart_count'] = sum([order['quantity'] for order in self.kwargs['order_list']])
        return context


@method_decorator(login_required, name='dispatch')
class BuyNowOrderForm(FormView):
    template_name = 'new_order.html'
    form_class = OrderForm

    def get_success_url(self, **kwargs):
        return reverse("product-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['order'] = {'product': product, 'quantity': 1, 'total_price': product.price}
        context['buy_now'] = True
        return setup_cart(self, self.request, context)

    def form_valid(self, form):
        product = Product.objects.get(slug=self.kwargs['slug'])
        cart = ShopCart.objects.create(user=self.request.user)
        order_product = OrderProduct(product=product, cart=cart, quantity=1)
        order_product.save()
        cart.total_price = product.price
        cart.quantity = 1
        cart.save()
        order = Order(**form.cleaned_data, cart=cart, user=self.request.user)
        order.save()
        return super(BuyNowOrderForm, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class OrderFormView(FormView):
    form_class = OrderForm
    template_name = 'new_order.html'

    def get_success_url(self, **kwargs):
        return reverse("cart-clean-all")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = get_cart_items(self)
        context['total_price'] = sum([item['total_price'] for item in context['object_list']])
        context['buy_now'] = False
        return setup_cart(self, self.request, context)

    def form_valid(self, form):
        session_cart = self.request.session['cart']
        product_slug = session_cart.keys()
        products = Product.objects.filter(slug__in=product_slug)
        cart = ShopCart.objects.create(user=self.request.user)
        total_price = 0
        total_quantity = 0
        for product in products:
            order_product = OrderProduct(
                product=product, cart=cart, quantity=session_cart[product.slug]
            )
            total_price += product.price * session_cart[product.slug]
            total_quantity += session_cart[product.slug]
            order_product.save()
        cart.total_price = total_price
        cart.quantity = total_quantity
        cart.save()
        order = Order(**form.cleaned_data, cart=cart, user=self.request.user)
        order.save()
        return super(OrderFormView, self).form_valid(form)

    def form_invalid(self, form):
        return redirect('new-order')
