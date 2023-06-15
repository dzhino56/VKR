import os

from rest_framework import serializers

from apps.segyviewer.models import File


class GetFilesSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = File
        fields = ('id', 'name', 'user')
