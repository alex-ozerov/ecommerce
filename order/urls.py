from django.urls import path, include


from . import views

urlpatterns = [
    path('cart_add/<slug:slug>/<int:quantity>/', views.CartAdd.as_view(), name='cart-add'),
    path('cart_delete/<slug:slug>/<int:quantity>', views.CartRemove.as_view(), name='cart-remove'),
    path('cart_clean_all/', views.CartCleanAll.as_view(), name='cart-clean-all'),
    path('cart/', views.CartView.as_view(), name='cart-view'),
    path('new-order/<int:buy_now>/', views.OrderFormView.as_view(), name='new-order'),
    path('buy-now/<slug:slug>/', views.BuyNowOrderForm.as_view(), name='buy-now')
]
