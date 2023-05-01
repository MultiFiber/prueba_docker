from .models import  UserApp
from rest_framework import serializers
from utils.serializers import BaseModelSerializer


class UserAppSerializer(BaseModelSerializer):

    status = serializers.IntegerField(write_only=True, required=False)

    def create(self, validated_data):
        password = validated_data.get('password', None)
        groups = validated_data.get('groups', None)
        status = validated_data.pop('status')
        user = super().create(validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        if groups:
            for group in groups:
                user.groups.add(group)

        if status:
            if status == 0:
                user.is_active = True
            elif status == 1:
                user.is_active = False
            user.save()
        return user

    def update(self, user, validated_data):
        password = validated_data.get('password',None)
        if password:
            user.set_password(password)
            user.save()

        return super().update(user,validated_data)


    class Meta:
        writeonly_fields = ['password']
        model = UserApp
        fields = '__all__'
