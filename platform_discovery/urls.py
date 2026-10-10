from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('categories/', views.categories, name='categories'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('business/<slug:slug>/', views.business_detail, name='business_detail'),
    path('search/', views.search_results, name='search_results'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('register-business/', views.register_business, name='register_business'),
    path('business-portal/', views.business_portal, name='business_portal'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('student-affairs/', views.student_affairs_dashboard, name='student_affairs_dashboard'),
    path('dashboard/business/', views.business_dashboard, name='business_dashboard'),
    path('dashboard/business/add-product/', views.create_product, name='create_product'),
    path('dashboard/business/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
]
