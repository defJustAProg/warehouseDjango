from django.urls import path
from server import views

urlpatterns = [
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('', views.get_start_page, name='start_page'),
    path('addRoll/', views.add_roll, name='add_roll'),
    path('get/', views.get_rolls, name='get_rolls'),
    path('delete/', views.delete_roll, name='delete_roll'),
    path('statistics/', views.get_statistics, name='get_statistics'),
]