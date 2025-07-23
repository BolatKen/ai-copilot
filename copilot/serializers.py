
from rest_framework import serializers

class ImageModerationRequestSerializer(serializers.Serializer):
    file = serializers.ImageField()

class ImageModerationResponseSerializer(serializers.Serializer):
    verdict = serializers.CharField()
    explanation = serializers.CharField()

class AskRequestSerializer(serializers.Serializer):
    context = serializers.CharField()
    question = serializers.CharField()

class AskResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()

