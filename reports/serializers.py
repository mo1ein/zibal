# reports/serializers.py
from rest_framework import serializers


class ReportRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=[("amount", "amount"), ("count", "count")])
    mode = serializers.ChoiceField(choices=[("daily", "daily"), ("weekly", "weekly"), ("monthly", "monthly")])
    merchantId = serializers.CharField(required=False, allow_null=True, allow_blank=True)
