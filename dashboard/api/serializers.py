from rest_framework import serializers

from core.models import *

###########
# INDICATOR in COMPANY
###########

class IndicatorSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Indicator
        #fields = '__all__'
        fields = ['url', 'pub_date', 'force', 'cmin', 'cmax', 'copen', 'cclose', 'mm30', 'phase']


#########
# COMPANY
#########

class CompanySerializer(serializers.ModelSerializer):
    #############################
    # Company :                 #
    # - name           : string #
    # - ref            : string #
    # - indice         : string #
    # - sector         : string #
    # - indicators     : fk     #
    #############################
    indicators = IndicatorSerializer(many=True)

    class Meta:
        model = Company
        # fields = '__all__'
        fields = ['url', 'name', 'ref', 'indice', 'sector', 'indicators']

    def create(self, validated_data):
        # fk
        # indicator_fk
        indicators_data = validated_data.pop('indicators')

        # company creation only if company does not already exist
        company = None
        companies_in_db = Company.objects.filter(name=validated_data['name'])
        if len(companies_in_db) == 1:
            company = companies_in_db[0]
        else:
            company = Company.objects.create(**validated_data)

        # children creation : indicator creation only if indicator does not already exist
        for indicator_data in indicators_data:
            indicator = None
            indicators_in_db = company.indicators.filter(pub_date=indicator_data['pub_date'])
            if len(indicators_in_db) == 1:
                indicator = indicators_in_db[0]
            else:
                indicator = Indicator.objects.create(company=company, **indicator_data)

        return company

########
# HEADER in BLOCK
########

class HeaderSerializer(serializers.ModelSerializer):
    #########################################
    # Header :                              #
    # - seeds                 : array str   #
    # - prev_block_hash       : hexa string #
    # - index                 : int         #
    # - merkle_root_tx_hash   : hexa string #
    #########################################
    class Meta:
        model = Header
        #fields = '__all__'
        fields = ['url', 'seeds', 'prev_block_hash', 'index', 'merkle_root_tx_hash']

#######
# BLOCK
#######

class BlockSerializer(serializers.ModelSerializer):
    #############################
    # Block :                   #
    # - name           : string #
    # - instance_id    : int    #
    # - headers        : fk     #
    # - transactions   : fk     #
    # - messages       : fk     #
    #############################
    headers = HeaderSerializer(many=True)

    class Meta:
        model = Block
        #fields = '__all__'
        fields = ['url', 'name', 'instance_id', 'headers']

    def create(self, validated_data):
        #fk
        # header_fk
        headers_data = validated_data.pop('headers')

        #block creation only if block does not already exist
        block_in_db = Block.objects.filter(name=validated_data['name'])
        if len(block_in_db) == 1:
            return block_in_db[0]

        block = Block.objects.create(**validated_data)

        #children creation : headers
        for header_data in headers_data:
            Header.objects.create(block=block, **header_data)

        return block
