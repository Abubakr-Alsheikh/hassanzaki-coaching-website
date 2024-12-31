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
    path('dashboard/requests/hide/<int:request_id>/', views.hide_request, name='hide_request'),
    path('dashboard/requests/delete/<int:request_id>/', views.delete_request, name='delete_request'),

    path('dashboard/plans/', views.plan_list, name='plan_list'),
    path('dashboard/plans/create/', views.plan_create, name='plan_create'),
    path('dashboard/plans/edit/<int:plan_id>/', views.plan_edit, name='plan_edit'),
    path('dashboard/plans/delete/<int:plan_id>/', views.plan_delete, name='plan_delete'),
    path('dashboard/home_content/', views.home_content, name='home_content'),
    # Certifications Dashboard URLs
    path('dashboard/certifications/', views.certification_list, name='certification_list'),
    path('dashboard/certifications/create/', views.certification_create, name='certification_create'),
    path('dashboard/certifications/edit/<int:certification_id>/', views.certification_edit, name='certification_edit'),
    path('dashboard/certifications/delete/<int:certification_id>/', views.certification_delete, name='certification_delete'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
