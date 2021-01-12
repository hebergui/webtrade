from django.db import models
import yfinance as yf


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class Employee(BaseModel):
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=150)
    office = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    start_date = models.DateField()
    salary = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Company(BaseModel):
    name = models.CharField(max_length=50)
    fullname = models.CharField(max_length=100)
    ref = models.CharField(max_length=50)
    indice = models.CharField(max_length=50)
    sector = models.CharField(max_length=150)

    def __str__(self):
        return self.name

    def get_current_force(self):
        return current_force(self.pk)

    def get_current_phase(self,):
        return current_phase(self.pk)

    def get_weinstein(self):
        return weinstein(self.pk)


class Indicator(BaseModel):
    pub_date = models.CharField(max_length=50)
    force = models.FloatField()
    cmin = models.FloatField()
    cmax = models.FloatField()
    copen = models.FloatField()
    cclose = models.FloatField()
    mm30 = models.FloatField()
    phase = models.CharField(max_length=50)
    company_fk = models.ForeignKey(Company, on_delete=models.CASCADE, unique=False)

    def __str__(self):
        return self.pub_date

    def get_current_force(self):
        return current_force(self.company_fk)

    def get_current_phase(self,):
        return current_phase(self.company_fk)

    def get_weinstein(self):
        return weinstein(self.company_fk)


class Stock(BaseModel):
    OPTIONS_CHOICES = [('P', 'PUT'), ('C', 'CALL')]

    name = models.CharField(max_length=150)
    option = models.CharField(max_length=1, choices=OPTIONS_CHOICES)
    pru = models.FloatField()
    target = models.FloatField(blank=True, default=0)
    stop = models.FloatField(blank=True, default=0)
    link = models.CharField(blank=True, max_length=150)
    price = models.FloatField(blank=True, default=0)
    company_fk = models.ForeignKey(Company, on_delete=models.CASCADE, unique=False)

    def __str__(self):
        return self.name

    def update_price(self):
        ticker = Ticker.objects.filter(company_fk=self.company_fk.pk).first()
        df = yf.download(ticker.yf, period="1d")
        if df.size > 0:
            self.price = round(df.tail(1)['Close'].values[0], 2)
            self.save()
            return self.price

    def get_current_force(self):
        return current_force(self.company_fk)

    def get_current_phase(self,):
        return current_phase(self.company_fk)

    def get_weinstein(self):
        return weinstein(self.company_fk)


def current_force(company_id):
    indicators = Indicator.objects.filter(company_fk=company_id).order_by('-id')
    if indicators.count() > 0:
        return indicators[0].force
    else:
        return None


def current_phase(company_id):
    indicators = Indicator.objects.filter(company_fk=company_id).order_by('-id')
    if indicators.count() > 0:
        return indicators[0].phase
    else:
        return "N/C"


def weinstein(company_id):
    indicators = Indicator.objects.filter(company_fk=company_id).order_by('-id')
    if indicators.count() < 2:
        return ""

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


class Ticker(BaseModel):
    name = models.CharField(max_length=50)
    yf = models.CharField(max_length=25, blank=True, default=None)
    isin = models.CharField(max_length=25, blank=True, default=None)
    zb_link = models.CharField(max_length=150, blank=True, default='#')
    yf_link = models.CharField(max_length=150, blank=True, default='#')
    inv_link = models.CharField(max_length=150, blank=True, default='#')
    company_fk = models.ForeignKey(Company, on_delete=models.CASCADE, unique=False)

    def __str__(self):
        return self.name
