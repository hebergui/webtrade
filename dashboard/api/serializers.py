from rest_framework import serializers
from core.models import *
# from ..core.models import *


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        # fields = '__all__'
        fields = ['url', 'name', 'position', 'office', 'age', 'start_date', 'salary']


class TickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticker
        # fields = '__all__'
        fields = ['url', 'name', 'zb', 'yf', 'inv', 'company_fk']


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        # fields = '__all__'
        fields = ['url', 'name', 'option', 'pru', 'target', 'stop', 'company_fk']


class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicator
        # fields = '__all__'
        fields = ['url', 'pub_date', 'force', 'cmin', 'cmax', 'copen', 'cclose', 'mm30', 'phase', 'company_fk']

    def create(self, validated_data):
        # indicator creation only if not already exist
        indicators_in_db = Indicator.objects.filter(pub_date=validated_data['pub_date'], company_fk=validated_data['company_fk'])
        if indicators_in_db.first() is not None:
            return indicators_in_db.first()
        else:
            return Indicator.objects.create(**validated_data)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        # fields = '__all__'
        fields = ['url', 'name', 'fullname', 'ref', 'indice', 'sector']

    def create(self, validated_data):
        # company creation only if not already exist
        companies_in_db = Company.objects.filter(name=validated_data['name'])
        if companies_in_db.first() is not None:
            return companies_in_db.first()
        else:
            return Company.objects.create(**validated_data)
