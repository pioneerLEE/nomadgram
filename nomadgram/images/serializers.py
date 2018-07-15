from rest_framework import serializers
from . import models
from nomadgram.users import models as user_models
from taggit_serializer.serializers import (TagListSerializerField,TaggitSerializer)


class SmallImageSerializer(serializers.ModelSerializer):
    """ Used for notifications """
    class Meta:
        model=models.Image
        fields = (
            'file',
        )

class CountImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=models.Image
        fields = (
            'file',
            'comment_count',
            'like_count',
        )

class FeedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.User
        fields = (
            'username',
            'profile_image'
        )
class CommentSerializer(serializers.ModelSerializer):
    creator = FeedUserSerializer(read_only=True)
    class Meta:
        model = models.Comment
        fields = (
            'message',
            'id',
            'creator',
            'image'
        )

class ImageSerializer(TaggitSerializer, serializers.ModelSerializer):
    comments= CommentSerializer(many=True)
    creator = FeedUserSerializer()
    tags = TagListSerializerField()
    class Meta:
        model = models.Image
        fields = (
            'id',
            'file',
            'location',
            'caption',
            'comments',
            'like_count',
            'creator',
            'tags',
            'created_at',
        )
class LikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Like
        fields = (
            'creator',
        )


class InputImageSerializer(serializers.ModelSerializer):
    # 모두다 필수 값이다. 그러므로 만약 'location'만 저장(put으로 인한 수정) 할려고 할 때 오류가 난다.
    # file = serializer.FileField(required=False) ---> file은 필수적인 입력값이 되지 않게 됨
    class Meta:
        model = models.Image
        fields = (
            'file',
            'location',
            'caption',
        )

