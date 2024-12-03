from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('coaching-request/<int:plan_id>/', views.coaching_request_view, name='coaching_request'),
]