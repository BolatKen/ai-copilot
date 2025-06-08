from rest_framework import serializers

class AskRequestSerializer(serializers.Serializer):
    context = serializers.CharField()
    question = serializers.CharField()

class AskResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
