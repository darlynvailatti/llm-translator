
from rest_framework import serializers
from .models import TranslationEndpoint, TranslationSpec, TranslationEvent, TranslationEventStatus


class TranslationEndpointAnalyticsSerializer(serializers.ModelSerializer):
    
    total_success = serializers.SerializerMethodField()
    total_failure = serializers.SerializerMethodField()
    traffic = serializers.SerializerMethodField()

    class Meta:
        model = TranslationEndpoint
        fields = ['total_success', 'total_failure']

    def get_total_success(self, obj) -> int:
        return obj.total_success

    def get_total_failure(self, obj) -> int:
        return obj.total_failure
    
    def get_traffic(self, obj) -> dict:

        # Group events by minute
        events = TranslationEvent.objects.filter(endpoint=obj)
        traffic_dict = {}
        for event in events:

            # Get unix timestamp for the minute
            minute = event.created_at.replace(second=0, microsecond=0).timestamp()
            status_group = event.status

            if status_group not in traffic_dict:
                traffic_dict[status_group] = {}

            if minute not in traffic_dict[status_group]:
                traffic_dict[status_group][minute] = 0
            traffic_dict[status_group][minute] += 1

        traffic = {}
        for status, v in traffic_dict.items():
            for minute, count in v.items():
                if status not in traffic:
                    traffic[status] = []
                traffic[status].append((minute, count))

        return traffic

class TranslationEndpointListSerializer(TranslationEndpointAnalyticsSerializer):

    class Meta:
        model = TranslationEndpoint
        exclude = ['definition']
    
class TranslationEndpointDetailSerializer(TranslationEndpointAnalyticsSerializer):
    class Meta:
        model = TranslationEndpoint
        exclude = ['owner']
    
class TranslationSpecListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationSpec
        exclude = ["definition"]

class TranslationSpecDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationSpec
        exclude = ['endpoint']