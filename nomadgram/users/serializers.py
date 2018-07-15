from rest_framework import serializers
from . import models
from nomadgram.images import serializers as images_serializers

class UserProfileSerializer(serializers.ModelSerializer):
    images = images_serializers.CountImageSerializer(many=True, read_only=True) 
    #부분적으로 업데이트하지 않을 필드가 있을 때 read_only를 사용한다.
    post_count = serializers.ReadOnlyField()
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField() #ReadOnlyField는 수정하지 않고 읽기만 하겠다고 선언하는 것이다.

    class Meta:
        model = models.User
        fields = (
            'profile_image',
            'username',
            'name',
            'bio',
            'website',
            'post_count',
            'followers_count',
            'following_count',
            'images',
        )

class ListUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            'id',
            'profile_image',
            'username',
            'name'
        )