from django.db import models


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
    ref = models.CharField(max_length=50)
    indice = models.CharField(max_length=50)
    sector = models.CharField(max_length=150)

    def __str__(self):
        return self.name


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


class Stock(BaseModel):
    OPTIONS_CHOICES = [('P', 'PUT'), ('C', 'CALL')]

    name = models.CharField(max_length=150)
    option = models.CharField(max_length=1, choices=OPTIONS_CHOICES)
    pru = models.FloatField()
    target = models.FloatField()
    stop = models.FloatField()
    company_fk = models.ForeignKey(Company, on_delete=models.CASCADE, unique=False)

    def __str__(self):
        return self.name
