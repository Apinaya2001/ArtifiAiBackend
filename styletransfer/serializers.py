from rest_framework import serializers

class StyleTransferSerializer(serializers.Serializer):
    image = serializers.ImageField()
    style = serializers.CharField()
