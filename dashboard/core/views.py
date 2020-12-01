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


class Dashboard(LoginRequiredMixin, View):
    template = 'dashboard/index.html'
    login_url = '/login/'

    def weinstein(self, qs):
        obj = None
        attr = "phase"

        if qs.count() < 2:
            return ""

        indicators = qs.order_by('-id')
        pnow = indicators[0].phase[0]
        pbefore = indicators[1].phase[0]
        if pnow not in ['1', '2', '3', '4'] or pbefore not in ['1', '2', '3', '4']:
            return "N/A"

        # phase 1 -> phase 2 : buy sig
        if pbefore == '1' and pnow == '2':
            return "Buy"
        # phase 3 -> phase 4 : sell sig
        if pbefore == '3' and pnow == '4':
            return "Sell"
        # phase x -> phase x : nb
        count = indicators.count()
        if pnow == pbefore:
            i = 2
            while indicators[i].phase[0] == pnow and i < count - 1:
                i += 1
            return f'{i} weeks'

        return "wait"

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
    json = {}

    def get(self, request, clazz=None, oid=None):
        self.json = {'clazz': clazz, 'oid': oid}

        return render(request, self.template, self.json)


class Graph(LoginRequiredMixin, View):
    template = 'graph/index.html'
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

    def get(self, request):
        stocks = Stock.objects.all()
        self.json = {'stocks': stocks}

        return render(request, self.template, self.json)


class StockCreate(LoginRequiredMixin, CreateView):
    model = Stock
    fields = ('name', 'company_fk', 'option', 'pru', 'target', 'stop', 'ticker', 'link')
    template_name = 'stock/form.html'
    success_url = '/stock/'


class StockUpdate(LoginRequiredMixin, UpdateView):
    model = Stock
    fields = ('pru', 'target', 'stop', 'ticker', 'link')
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
    json = {'pk': None}

    if clazz == 'company' and name is not None:
        # Decode escaped characters in URL
        name = urllib.parse.unquote(name)
        company = Company.objects.filter(name=name).first()
        if company:
            json = {'pk': company.pk}

    return JsonResponse(json, safe=False)
