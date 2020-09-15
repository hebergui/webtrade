from django.db import models

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

