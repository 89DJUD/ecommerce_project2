from django.urls import path
from . import views

urlpatterns = [
    path('', views.products_list, name='product_list'),
    path('<int:id>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
]
