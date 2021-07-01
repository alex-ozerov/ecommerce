from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.urls import reverse
from elasticsearch_dsl import Q
from django.core.exceptions import ObjectDoesNotExist

from product.models import Product, Category, Comment
from product.forms import CommentForm
from product.documents import ProductDocument

# Create your views here.


def setup_cart(self, request, context):
    try:
        context['cart'] = self.request.session['cart']
        context['cart_count'] = sum(context['cart'].values())
    except KeyError:
        context['cart'] = self.request.session['cart'] = {}
        context['cart_count'] = 0
    return context


class CategoryListView(ListView):
    template_name = 'category_product_list.html'
    paginate_by = 3

    def get_queryset(self):
        products = Product.objects.filter(category__slug=self.kwargs['category'], status=True)
        self.kwargs['count'] = products.count()
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(slug=self.kwargs['category'])
        context['categories_list'] = Category.objects.all().exclude(slug=context['category'].slug)
        context['product_count'] = self.kwargs['count']
        return setup_cart(self, self.request, context)


class ProductListView(ListView):
    template_name = 'all_product_list.html'
    model = Product
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories_list'] = Category.objects.filter()

        return setup_cart(self, self.request, context)


class ProductDetailView(FormMixin, DetailView):
    model = Product
    form_class = CommentForm
    template_name = 'product_detail.html'

    def get_success_url(self, **kwargs):
        return reverse("product-detail", kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments_list'] = Comment.objects.filter(product=self.object)
        context['categories_list'] = Category.objects.all()
        context['form'] = self.form_class()
        return setup_cart(self, self.request, context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, initial={
            'product': self.object,
            'user': self.request.user
        })

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        new_comment = Comment(user=form.initial['user'],
                              product=form.initial['product'],
                              **form.cleaned_data)
        new_comment.save()
        return super(ProductDetailView, self).form_valid(form)

    def form_invalid(self, form):
        return super(ProductDetailView, self).form_invalid(form)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('product-list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


class Search(ListView):
    template_name = 'search_results.html'

    def get_queryset(self):
        search_text = self.request.GET.get("search_box", None)
        results = ProductDocument.search().query(
            "multi_match", query=search_text,
            type='phrase', fields=["title", "description"]).to_queryset()

        self.kwargs['search_count'] = results.count()
        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get("search_box", None)
        context['search_count'] = self.kwargs['search_count']
        return setup_cart(self, self.request, context)
