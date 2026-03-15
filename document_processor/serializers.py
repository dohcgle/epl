from rest_framework import serializers
from .models import (
    Client, LoanApplication, LoanDetails, ContactPerson, FinancialInfo,
    Collateral, AutoCollateral, RealEstateCollateral, GoldCollateral, InsuranceCollateral
)
from django.contrib.auth.models import User
from .utils import parse_date, clean_int, clean_float, clean_str, clean_phone
from django.db import connection
import json

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ContactPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPerson
        fields = ['id', 'fish', 'telefon', 'qarindoshlik']

class LoanDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanDetails
        fields = '__all__'
        extra_kwargs = {'application': {'required': False}}

class FinancialInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialInfo
        fields = '__all__'
        extra_kwargs = {'application': {'required': False}}

class AutoCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoCollateral
        fields = '__all__'
        extra_kwargs = {'collateral': {'required': False}}

class RealEstateCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstateCollateral
        fields = '__all__'
        extra_kwargs = {'collateral': {'required': False}}

class GoldCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldCollateral
        fields = '__all__'
        extra_kwargs = {'collateral': {'required': False}}

class InsuranceCollateralSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceCollateral
        fields = '__all__'
        extra_kwargs = {'collateral': {'required': False}}

class CollateralSerializer(serializers.ModelSerializer):
    auto_detail = AutoCollateralSerializer(required=False)
    real_estate_detail = RealEstateCollateralSerializer(required=False)
    gold_detail = GoldCollateralSerializer(required=False)
    insurance_detail = InsuranceCollateralSerializer(required=False)
    owner_client = ClientSerializer(required=False)

    class Meta:
        model = Collateral
        fields = [
            'id', 'type', 'owner_type', 'owner_client',
            'notarius_fish', 'notarius_address', 'reestr_number', 'reestr_date',
            'auto_detail', 'real_estate_detail', 'gold_detail', 'insurance_detail'
        ]

class LoanApplicationSerializer(serializers.ModelSerializer):
    personal = ClientSerializer(source='client')
    loan = LoanDetailsSerializer(source='details', required=False)
    contacts = ContactPersonSerializer(many=True, required=False)
    financial = FinancialInfoSerializer(source='financial_info', required=False)
    # collateral is special because frontend sends one object with selected_types
    collateral = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = LoanApplication
        fields = [
            'id', 'personal', 'status', 'created_by', 'payload',
            'loan', 'contacts', 'financial', 'collateral'
        ]
        read_only_fields = ['created_by', 'status']

    def create(self, validated_data):
        # Prepare the full payload from validated_data
        # Note: source transformations like 'client' -> 'personal' are already done in the incoming JSON
        # but DRF's validated_data will have them as 'client' because of source='client'
        
        # We'll re-construct the payload structure that the DB expects
        # (similar to what the frontend sends)
        request = self.context.get('request')
        user_id = request.user.id if request and request.user else None
        
        # We need the RAW data for the payload field in DB, but for the SP call
        # we can pass the validated data converted back to the structure the SP expects.
        
        # Extract individual parts
        personal = validated_data.get('client')
        loan = validated_data.get('details')
        contacts = validated_data.get('contacts', [])
        financial = validated_data.get('financial_info')
        collateral = validated_data.get('collateral', {})

        # Construct the payload for the SP
        sp_payload = {
            'personal': ClientSerializer(personal).data if personal else {},
            'loan': LoanDetailsSerializer(loan).data if loan else {},
            'contacts': ContactPersonSerializer(contacts, many=True).data,
            'financial': FinancialInfoSerializer(financial).data if financial else {},
            'collateral': collateral
        }

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT sp_save_loan_application(%s, %s, %s)",
                [json.dumps(sp_payload), user_id, None]
            )
            v_app_id = cursor.fetchone()[0]

        return LoanApplication.objects.get(id=v_app_id)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user_id = request.user.id if request and request.user else None

        # Similar reconstruction for update
        personal = validated_data.get('client')
        loan = validated_data.get('details')
        contacts = validated_data.get('contacts')
        financial = validated_data.get('financial_info')
        collateral = validated_data.get('collateral')

        # Use current data if not provided in validated_data
        sp_payload = {
            'personal': ClientSerializer(personal).data if personal else ClientSerializer(instance.client).data,
            'loan': LoanDetailsSerializer(loan).data if loan else LoanDetailsSerializer(instance.details).data,
            'contacts': ContactPersonSerializer(contacts, many=True).data if contacts is not None else ContactPersonSerializer(instance.contacts.all(), many=True).data,
            'financial': FinancialInfoSerializer(financial).data if financial else FinancialInfoSerializer(instance.financial_info).data,
            'collateral': collateral if collateral is not None else instance.payload.get('collateral', {})
        }

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT sp_save_loan_application(%s, %s, %s)",
                [json.dumps(sp_payload), user_id, instance.id]
            )
            v_app_id = cursor.fetchone()[0]

        instance.refresh_from_db()
        return instance
