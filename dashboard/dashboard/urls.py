from django.contrib import admin
from django.urls import path, include
from core import views
# from ..core import views

urlpatterns = [
    path('', views.Dashboard.as_view(), name='dashboard'),
    path('admin/', admin.site.urls),
    path('login/', views.Login.as_view(), name='login'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('hello/', views.Hello.as_view(), name='hello'),
    path('hello/<str:clazz>/<int:oid>', views.Hello.as_view(), name='hello'),
    path('graph/', views.Graph.as_view(), name='graph'),
    path('graph/<str:clazz>/<int:oid>', views.Graph.as_view(), name='graph'),
    path('api/', include('api.urls')),
]

