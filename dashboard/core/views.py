from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import View
import urllib.parse

from .models import *
from .forms import *


class Login(View):
    template = 'login.html'

    def get(self, request):
        form = AuthenticationForm()
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return render(request, self.template, {'form': form})


class Index(LoginRequiredMixin, View):
    template = 'index/index.html'
    login_url = '/login/'
    json = {}

    def get(self, request, clazz=None, oid=None):
        return render(request, self.template, self.json)


class Dashboard(LoginRequiredMixin, View):
    template = 'dashboard/index.html'
    login_url = '/login/'

    def get(self, request):
        companies = Company.objects.all()
        sectors = Company.objects.all().values_list('sector', flat=True).distinct().order_by('sector')
        indices = Company.objects.all().values_list('indice', flat=True).distinct()
        phases = Indicator.objects.all().values_list('phase', flat=True).distinct().order_by('phase')

        json = {
            'companies': companies,
            'sectors': sectors,
            'indices': indices,
            'phases': phases,
        }
        return render(request, self.template, json)


class Hello(LoginRequiredMixin, View):
    template = 'hello/index.html'
    login_url = '/login/' 
    json = {}

    def get(self, request, clazz=None, oid=None):
        self.json = {'clazz': clazz, 'oid': oid}

        return render(request, self.template, self.json)


class Scraper(LoginRequiredMixin, View):
    template = 'scraper/index.html'
    json = {}

    def get(self, request, room_name='scraper'):
        self.json = {'room_name': room_name}

        return render(request, self.template, self.json)


class Graph(LoginRequiredMixin, View):
    template = 'graph/index.html'
    login_url = '/login/' 
    json = {}

    def get(self, request, clazz=None, oid=None):
        if clazz == 'company':
            company = get_object_or_404(Company, id=oid)
            indicators = Indicator.objects.filter(company_fk=company.pk)
            stocks = []  # [date, low, open, high, close, mm30, phase, force]
            for i in indicators:
                if i.phase[0] in ['1', '2', '3', '4']:
                    p = int(i.phase[0])
                else:
                    p = 0
                stocks.append(
                    [i.pub_date, i.cmin, i.copen, i.cclose, i.cmax, i.mm30, p, i.force]
                )

            self.template = 'graph/index.html'
            self.json = {'clazz': clazz, 'oid': oid, 'company': company, 'data4stocks': stocks}

        else:
            self.template = 'graph/selector.html'
            companies = Company.objects.all().values_list('id', 'name').order_by('name')
            self.json = {'companies': companies}

        return render(request, self.template, self.json)


class StockView(LoginRequiredMixin, View):
    template = 'stock/index.html'
    json = {}

    def get(self, request, refresh=None):
        stocks = Stock.objects.all()

        if refresh == "refresh":
            for s in stocks:
                s.update_price()

        self.json = {'stocks': stocks}

        return render(request, self.template, self.json)


class StockRefresh(LoginRequiredMixin, View):
    template = 'stock/index.html'
    json = {}

    def get(self, request):
        stocks = Stock.objects.all()

        for s in stocks:
            s.update_price()

        self.json = {'stocks': stocks}

        return render(request, self.template, self.json)


class StockCreate(LoginRequiredMixin, CreateView):
    model = Stock
    fields = ('name', 'company_fk', 'option', 'pru', 'target', 'stop', 'link', 'price')
    template_name = 'stock/form.html'
    success_url = '/stock/'


class StockUpdate(LoginRequiredMixin, UpdateView):
    model = Stock
    fields = ('name', 'pru', 'target', 'stop', 'link')
    template_name = 'stock/form.html'
    success_url = '/stock/'


class StockDelete(LoginRequiredMixin, DeleteView):
    model = Stock
    template_name = 'stock/delete.html'
    success_url = '/stock/'


class EmployeeView(LoginRequiredMixin, View):
    template = 'employee/index.html'
    json = {}

    def get(self, request):
        employees = Employee.objects.all()
        self.json = {'employees': employees}

        return render(request, self.template, self.json)


class EmployeeCreate(LoginRequiredMixin, CreateView):
    model = Employee
    fields = ('name', 'position', 'office', 'age', 'start_date', 'salary')
    template_name = 'employee/form.html'
    success_url = '/employee/'


class EmployeeUpdate(LoginRequiredMixin, UpdateView):
    model = Employee
    fields = ('name', 'position', 'office', 'age', 'start_date', 'salary')
    template_name = 'employee/form.html'


class EmployeeDelete(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employee/delete.html'
    success_url = '/employee/'


def get_pk(request, clazz=None, name=None):
    json = {'pk': None, 'dates': []}

    if clazz == 'company' and name is not None:
        # Decode escaped characters in URL
        name = urllib.parse.unquote(name)
        company = Company.objects.filter(name=name).first()
        ticker = Ticker()
        if company:
            dates = Indicator.objects.filter(company_fk=company.pk).values_list('pub_date', flat=True)
            json = {
                'pk': company.pk,
                'dates': list(dates)
            }

    return JsonResponse(json, safe=False)
