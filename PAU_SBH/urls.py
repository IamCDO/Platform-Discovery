"""
URL configuration for PAU_SBH project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from platform_discovery import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('platform_discovery.urls')),
    path('profile/', views.profile, name='profile'),
    path('accounts/login/', views.profile, {'default_mode': 'login'}, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/signup/', views.profile, {'default_mode': 'signup'}, name='signup'),
]
