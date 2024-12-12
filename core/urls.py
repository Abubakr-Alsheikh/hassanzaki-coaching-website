from . import views
from django.urls import path

app_name = "coaching"
urlpatterns = [
    path('', views.index, name='index'),
    path('coaching-request/<int:plan_id>/', views.coaching_request_view, name='coaching_request'),
    path('available_times/<str:date>/', views.available_times, name='available_times'),
]