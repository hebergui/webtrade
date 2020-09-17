"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from core import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Index.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('index/', views.Index.as_view(), name='index'),
    path('hello/', views.Hello.as_view(), name='hello'),
    path('hello/<str:clazz>/<int:oid>', views.Hello.as_view(), name='hello'),
    path('reqsync/', views.req_sync, name='req_sync'),
    path('reqasync/', views.req_async, name='req_async'),
    path('pullasync/', views.pull_async, name='pull_async'),
    path('api/', include('api.urls')),
]
