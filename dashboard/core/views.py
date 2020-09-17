import asyncio
import html
import time
import httpx
from asgiref.sync import sync_to_async

from core.models import *
from django.contrib.auth import login, authenticate
# from django.db.models import Count
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View


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
    template = 'index.html'
    login_url = '/login/'

    def get(self, request):
        companies = Company.objects.all()
        n_companies = companies.count()

        json = {
            'companies': companies,
            'n_companies': n_companies,
        }
        return render(request, self.template, json)

    def post(self, request):
        pull()

        companies = Company.objects.all()
        n_companies = companies.count()

        json = {
            'companies': companies,
            'n_companies': n_companies,
        }

        render(request, self.template, json)


class Hello(LoginRequiredMixin, View):
    template = 'hello/index.html'
    json = {}

    def get(self, request, clazz=None, oid=None):
        if clazz == 'block':
            block = Block.objects.get(id=oid)
            self.template = 'timelines/block.html'
            self.json = {'clazz': clazz, 'oid': oid, 'oblock': block}

        else:
            self.template = 'hello/index.html'
            #blocks = Block.objects.all().values_list('id', 'name')
            self.json = {'clazz': clazz, 'oid': oid}

        return render(request, self.template, self.json)


def req_sync(request):
    template = 'pull/index.html'

    s = time.perf_counter()
    responses = []
    urls = ["https://screener.blogbourse.net/cours-soitec.html", "https://screener.blogbourse.net/cours-total.html"]

    for url in urls:
        r = httpx.get(url)
        responses.append(r.text)
    elapsed = time.perf_counter() - s
    json = {
        "message": "Hello Sync World!",
        "responses": responses,
        "debug_message": f"fetch executed in {elapsed:0.2f} seconds.",
    }
    return render(request, template, json)


async def req_async(request):
    template = 'pull/index.html'

    s = time.perf_counter()
    responses = []
    urls = ["https://screener.blogbourse.net/cours-soitec.html", "https://screener.blogbourse.net/cours-total.html"]

    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(*[client.get(url) for url in urls])
        responses = [r.text for r in responses]
    elapsed = time.perf_counter() - s
    json = {
        "message": "Hello Async World!",
        "responses": responses,
        "debug_message": f"fetch executed in {elapsed:0.2f} seconds.",
    }
    return render(request, template, json)


async def pull_async(request):
    template = 'pull/index.html'
    json = {}
    n_req, indicator_creation, company_creation = 1, 0, 0
    s = time.perf_counter()

    url = 'https://screener.blogbourse.net/societes.html'
    r = httpx.get(url)
    tree = html.fromstring(r.text)

    # format : [id, name, indice, id, name, indice...]
    tab1 = tree.xpath('(//table)[1]//td//text()')
    # format : [[name, indice], [name, indice], ...]
    companies = [tab1[x + 1:x + 3] for x in range(0, len(tab1), 3)]

    # format : [ref, ref, ...]
    tab2 = tree.xpath('(//table)[1]//td//@href')

    # format : [[name, indice, ref], ...]
    companies = [companies[x] + [str(tab2[x])] for x in range(0, len(tab2))]

    url = "https://screener.blogbourse.net/"
    #companies = [['total', 'cac40', 'cours-total.html'], ['safran', 'cac40', 'cours-safran.html']]

    for name, indice, ref in companies:
        n_req += 1
        client = httpx.AsyncClient()
        response = await asyncio.gather(*[client.get(url + ref)])

        try:
            tree = html.fromstring(response[0].text)
            sector = tree.xpath('/html/body/div/div/main/div[4]/ul/li[4]/a/text()')
            if len(sector) == 0:
                sector = tree.xpath('/html/body/div/div/main/div[4]/ul/li[4]/em/text()')
            sector = sector[0]
            force = float(tree.xpath('/html/body/div/div/main/div[4]/ul/li[5]/text()')[0].split(' : ')[1])
            phase, pub_date = tree.xpath('/html/body/div/div/main/div[4]/ul/li[6]/text()')[0].split(': ')[1].split(' (')
            pub_date = pub_date[:-1]
        except ValueError as err:
            print("ValueError for :", name, err)
            continue

        # company creation only if company does not already exist
        company = None
        companies_in_db = await sync_to_async(Company.objects.filter)(name=name)
        count = await sync_to_async(companies_in_db.count)()
        if count == 1:
            company = await sync_to_async(companies_in_db.first)()
        else:
            company_creation += 1
            company = await sync_to_async(Company.objects.create)(name=name, ref=ref, indice=indice, sector=sector)

        # indicator creation only if indicator does not already exist
        indicator = None
        indicators_in_db = await sync_to_async(company.indicators.filter)(pub_date=pub_date)
        count = await sync_to_async(indicators_in_db.count)()
        if count == 1:
            indicator = await sync_to_async(indicators_in_db.first)()
        else:
            indicator_creation += 1
            indicator = await sync_to_async(Indicator.objects.create)(pub_date=pub_date, force=force, phase=phase, company=company)

        elapsed = time.perf_counter() - s
        json = {
            "message": "Hello Async World!",
            "n_req": n_req,
            "company_creation": company_creation,
            "indicator_creation": indicator_creation,
            "debug_message": f"fetch executed in {elapsed:0.2f} seconds.",
        }

    return render(request, template, json)
