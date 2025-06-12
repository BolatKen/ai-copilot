from rest_framework import serializers
from .models import Content, Tag, ModerationResult


class AskRequestSerializer(serializers.Serializer):
    context = serializers.CharField()
    question = serializers.CharField()

class AskResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['id', 'file', 'file_type', 'uploaded_at', 'safety_status']
        read_only_fields = ['id', 'uploaded_at', 'safety_status']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ModerationResultSerializer(serializers.ModelSerializer):
    detected_tags = TagSerializer(many=True, read_only=True)
    content = ContentSerializer(read_only=True)
    
    class Meta:
        model = ModerationResult
        fields = '__all__'

