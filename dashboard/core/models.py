from django.db import models
from lxml import html
import requests

#########
#EMPLOYEE
#########


class Employee(models.Model):
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=150)
    office = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    start_date = models.DateField()
    salary = models.PositiveIntegerField()

    def __str__(self):
        return self.name


#########
# COMPANY
#########

class Company(models.Model):
    #############################
    # Company :                 #
    # - name           : string #
    # - ref            : string #
    # - indice         : string #
    # - sector         : string #
    # - indicators     : fk     #
    #############################
    name = models.CharField(max_length=50)
    ref = models.CharField(max_length=50)
    indice = models.CharField(max_length=50)
    sector = models.CharField(max_length=150)

###########
# INDICATOR
###########

class Indicator(models.Model):
    #############################
    # Indicator :               #
    # - pub_date       : string #
    # - force          : float  #
    # - phase          : string #
    #############################
    pub_date = models.CharField(max_length=50)
    force = models.FloatField()
    phase = models.CharField(max_length=50)
    # company_fk
    company = models.ForeignKey(Company, related_name='indicators', on_delete=models.CASCADE, null=True)

######
#BLOCK
######


class Block(models.Model):
    #############################
    # Block :                   #
    # - name           : string #
    # - instance_id    : int    #
    # - headers        : fk     #
    # - transactions   : fk     #
    # - messages       : fk     #
    #############################
    name = models.CharField(max_length=50)
    instance_id = models.PositiveIntegerField()


class Header(models.Model):
    #########################################
    # Header :                              #
    # - seeds                 : array str   #
    # - prev_block_hash       : hexa string #
    # - index                 : int         #
    # - merkle_root_tx_hash   : hexa string #
    #########################################
    seeds = models.TextField()
    prev_block_hash = models.CharField(max_length=100)
    index = models.PositiveIntegerField()
    merkle_root_tx_hash = models.CharField(max_length=100)
    #block_fk
    block = models.ForeignKey(Block, related_name='headers', on_delete=models.CASCADE, null=True)

##############################################
### HELPERS FUNCTIONS ########################
async def pull():
    url = 'https://screener.blogbourse.net/societes.html'
    page = requests.get(url)
    tree = html.fromstring(page.content)

    # format : [id, name, indice, id, name, indice...]
    tab1 = tree.xpath('(//table)[1]//td//text()')
    # format : [[name, indice], [name, indice], ...]
    companies = [tab1[x + 1:x + 3] for x in range(0, len(tab1), 3)]

    # format : [ref, ref, ...]
    tab2 = tree.xpath('(//table)[1]//td//@href')

    # format : [[name, indice, ref], ...]
    companies = [companies[x] + [str(tab2[x])] for x in range(0, len(tab2))]

    for name, indice, ref in companies:
        url = 'https://screener.blogbourse.net/' + ref
        page = requests.get(url)
        tree = html.fromstring(page.content)
        sector = tree.xpath('/html/body/div/div/main/div[4]/ul/li[4]/a/text()')
        if len(sector) == 0:
            sector = tree.xpath('/html/body/div/div/main/div[4]/ul/li[4]/em/text()')
        sector = sector[0]
        force = float(tree.xpath('/html/body/div/div/main/div[4]/ul/li[5]/text()')[0].split(' : ')[1])
        phase, pub_date = tree.xpath('/html/body/div/div/main/div[4]/ul/li[6]/text()')[0].split(': ')[1].split(' (')
        pub_date = pub_date[:-1]

        # company creation only if company does not already exist
        company = None
        companies_in_db = Company.objects.filter(name=name)
        if len(companies_in_db) == 1:
            company = companies_in_db[0]
        else:
            company = Company.objects.create(name=name, ref=ref, indice=indice, sector=sector)

        # indicator creation only if indicator does not already exist
        indicator = None
        indicators_in_db = company.indicators.filter(pub_date=pub_date)
        if len(indicators_in_db) == 1:
            indicator = indicators_in_db[0]
        else:
            indicator = Indicator.objects.create(pub_date=pub_date, force=force, phase=phase, company=company)

    return 'ok'
