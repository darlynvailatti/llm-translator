
from rest_framework import serializers
from .models import TranslationEndpoint, TranslationSpec


class TranslationEndpointAnalyticsSerializer(serializers.ModelSerializer):
    
    total_success = serializers.SerializerMethodField()
    total_failure = serializers.SerializerMethodField()

    class Meta:
        model = TranslationEndpoint
        fields = ['total_success', 'total_failure']

    def get_total_success(self, obj) -> int:
        return obj.total_success

    def get_total_failure(self, obj) -> int:
        return obj.total_failure

class TranslationEndpointListSerializer(TranslationEndpointAnalyticsSerializer):

    class Meta:
        model = TranslationEndpoint
        exclude = ['definition']
    
class TranslationEndpointDetailSerializer(TranslationEndpointAnalyticsSerializer):
    class Meta:
        model = TranslationEndpoint
        exclude = ['owner']
    
class TranslationSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationSpec
        fields = '__all__'