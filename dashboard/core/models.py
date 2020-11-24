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


class Indicator(BaseModel):
    #############################
    # Indicator :               #
    # - pub_date       : string #
    # - force          : float  #
    # - cmin           : float  #
    # - cmax           : float  #
    # - copen          : float  #
    # - cclose         : float  #
    # - mm30           : float  #
    # - phase          : string #
    #############################
    pub_date = models.CharField(max_length=50)
    force = models.FloatField()
    cmin = models.FloatField()
    cmax = models.FloatField()
    copen = models.FloatField()
    cclose = models.FloatField()
    mm30 = models.FloatField()
    phase = models.CharField(max_length=50)
    # company_fk
    company = models.ForeignKey(Company, related_name='indicators', on_delete=models.CASCADE, null=True)

