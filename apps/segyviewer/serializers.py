from rest_framework import serializers

from apps.segyviewer.models import File


class FilesSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = File
        fields = ('id', 'name', 'user')
