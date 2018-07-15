from rest_framework.views import APIView
from rest_framework.response import Response
from . import models, serializers

class ListAllImage(APIView):

    def get(self, request, format=None):

        all_images = models.Image.objects.all() #Image의 모든 이미지 오브젝트를 가지고 온다.

        serializer = serializers.ImageSerializer(all_images, many=True) #  python object -> JSON 으로 번역
        #ImageSerializer은 복수 이므로 인자값에 many=True를 넘겨주어서 여러개를 처리하게 끔 한다

        return Response(data = serializer.data) #클래스인 serializer의 data 값은 보내줌 
class ListAllComments(APIView):
    
    def get(self, request, format=None):
        all_comments = models.Comment.objects.all()
        serializer = serializers.CommentSerializer(all_comments, many=True)
        return Response(data = serializer.data)
    
class ListAllLikes(APIView):
    
    def get(self, request, format=None):
        all_likes = models.Like.objects.all()
        serializer = serializers.LikeSerializer(all_likes,many = True)
        return Response(data = serializer.data)
