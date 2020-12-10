from django.contrib import admin
from django.urls import path, include
from core.views import *
#from ..core.views import *

urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),

    path('login/', Login.as_view(), name='login'),

    path('hello/', Hello.as_view(), name='hello'),
    path('hello/<str:clazz>/<int:oid>', Hello.as_view(), name='hello'),

    path('graph/', Graph.as_view(), name='graph'),
    path('graph/<str:clazz>/<int:oid>', Graph.as_view(), name='graph'),

    path('stock/', StockView.as_view(), name='stock'),
    path('stock/<str:refresh>', StockView.as_view(), name='stock-refresh'),
    path('stock/add/', StockCreate.as_view(), name='stock-add'),
    path('stock/<int:pk>/', StockUpdate.as_view(), name='stock-update'),
    path('stock/<int:pk>/delete/', StockDelete.as_view(), name='stock-delete'),

    path('employee/', EmployeeView.as_view(), name='employee'),
    path('employee/add/', EmployeeCreate.as_view(), name='employee-add'),
    path('employee/<int:pk>/', EmployeeUpdate.as_view(), name='employee-update'),
    path('employee/<int:pk>/delete/', EmployeeDelete.as_view(), name='employee-delete'),

    path('get_pk/<str:clazz>/<str:name>/', get_pk, name='get_pk'),

    path('scraper/', Scraper.as_view(), name='scraper'),

    path('admin/', admin.site.urls, name='admin'),
    path('api/', include('api.urls'), name='api'),
    path('live/', include('live.urls'), name='live'),
]

