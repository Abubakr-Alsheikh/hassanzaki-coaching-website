from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

app_name = "coaching"
urlpatterns = [
    path('', views.index, name='index'),
    path('coaching-request/<int:plan_id>/', views.coaching_request_view, name='coaching_request'),
    # dashbaord
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/requests/', views.request_list, name='request_list'),
    path('requests/hide/<int:request_id>/', views.hide_request, name='hide_request'),
    path('requests/delete/<int:request_id>/', views.delete_request, name='delete_request'),
    # path('dashboard/products/create/', views.product_create, name='product_create'),
    # path('dashboard/products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    # path('dashboard/products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
]
