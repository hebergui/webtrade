from core.models import *
from django.contrib.auth import login, authenticate
# from django.db.models import Count
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View
from datetime import datetime

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

    def get(self, request):
        companies = Company.objects.all()
        n_companies = companies.count()
        sectors = Company.objects.all().values_list('sector', flat=True).distinct().order_by('sector')
        indices = Company.objects.all().values_list('indice', flat=True).distinct()
        phases =  Indicator.objects.all().values_list('phase', flat=True).distinct().order_by('phase')

        json = {
            'companies': companies,
            'n_companies': n_companies,
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
            company = Company.objects.get(id=oid)
            indicators = Indicator.objects.filter(company_id=oid)
            stocks = [] #[date, low, open, high, close, mm30, phase, force]
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
            self.template = 'hello/index.html'
            #blocks = Block.objects.all().values_list('id', 'name')
            self.json = {'clazz': clazz, 'oid': oid}

        return render(request, self.template, self.json)

