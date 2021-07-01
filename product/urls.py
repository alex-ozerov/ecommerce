from django.urls import path, include


from . import views

urlpatterns = [
    path('products/<slug:category>/', views.CategoryListView.as_view(), name='category-list'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('search/product/', views.Search.as_view(), name='search-product'),
]
