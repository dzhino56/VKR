import os

from rest_framework import serializers
from rest_framework.fields import empty

from apps.segyviewer.models import File
from vkr.settings import BASE_DIR


class GetFilesSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = File
        fields = ('id', 'name', 'user')


class PostFilesSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = File
        fields = ('id', 'user')

    def save(self):
        file_path = self.create_file_path()
        file = File(
            name=self.file.name,
            user_file_path=file_path,
            real_file_path=file_path
        )
        self.create_file(file_path)
        file.save()
        return file

    def __init__(self, file, user, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.file = file
        self.current_user = user


