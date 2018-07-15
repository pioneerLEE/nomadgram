from rest_framework.views import APIView
from rest_framework.response import Response
from . import models, serializers
from rest_framework import status
from nomadgram.notifications import views as notification_views
from nomadgram.users import serializers as user_serializers
from nomadgram.users import models as user_models

class Images(APIView):
    
    def get(self, request, format=None):

        user = request.user
        

        following_users = user.following.all()
        print(user, following_users)
        image_list = []
        for following_users in following_users: #이 부분의 문제가 있다면 자기자신의 게시물은 보이지 않는것이다. 문제는 나는 내 스스로를 팔로잉 해버림.
            user_images=following_users.images.all()
            #following_users.images.all()[:3]   ->   예를 들어 최신의 것 3개만 보고싶다는 것이다
            for image in user_images:
                image_list.append(image) #파이썬 반복문의 for (A) in (array) 에서 A는 그냥 인자이므로 딱히 의미 없다(?)
        
        my_images = user.images.all()[:2]

        for image in my_images:  
            image_list.append(image)
        
        sorted_list=sorted(image_list,key=lambda image:image.created_at, reverse=True)
        #sorted(무엇을, 어떻게,역순(reverse=True)으로 할지 정순(reverse=False)으로 할지)
        serializer = serializers.ImageSerializer(sorted_list, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        
        user = request.user

        serializer = serializers.InputImageSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(creator = user) #생성자가 유저와 동일하다면~

            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        
        else: 
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikeImage(APIView):
    
    #기능을 추가해서 확장한다??!!

    def get(self, request, image_id, format=None):
        
        likes = models.Like.objects.filter(image__id=image_id) 
        # __는 여기서 like의 id가 아닌 image 오브젝트 안에 있다는 것을 의미함
        # 그냥 image_id의 _는 그냥 변수 이름의 일부이다. 우리 개발자가 임의로 작성한
        # 여기까지는  그냥 좋아요 리스트를 알 수 있다. 그리고 like.values()로 id를 포함한 내부 정보를 추출할 수 있다.
        like_creators_ids = likes.values('creator_id')
        users=user_models.User.objects.filter(id__in=like_creators_ids)
        # __in은 "__in=array"이란 형태에서 array의 요소를 하나하나 '='(같은지) 체크해준다. 일종의 반복문으로 길게 쓸것을 줄이는 개념이다.
        # 즉 여기서는 id 하나와 여러개의 id를 가진 array인 like_creators_ids를 각각 비교해준다,.
        serializer = user_serializers.ListUserSerializer(users, many=True)
        return Response(data=serializer.data, status = status.HTTP_200_OK)

    def post(self, request, image_id, format=None):
        user = request.user
        try:
            found_image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            preexisiting_like = models.Like.objects.get(
                creator = user,
                image = found_image
            )
            return Response(status = status.HTTP_304_NOT_MODIFIED)
        except models.Like.DoesNotExist:
            new_like = models.Like.objects.create(
            creator = user,
            image = found_image
            )
            new_like.save()
            # create notification
            notification_views.create_notification(
                user, found_image.creator, 'like', found_image)

            return Response(status=status.HTTP_201_CREATED)

class UnLikeImage(APIView):
    def delete(self, request,image_id, format=None):
        user = request.user
        try:
            found_image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            preexisiting_like = models.Like.objects.get(
                creator = user,
                image = found_image
            )
            preexisiting_like.delete()
            return Response(status = status.HTTP_204_NO_CONTENT)
        except models.Like.DoesNotExist:
            return Response(status = status.HTTP_304_NOT_MODIFIED)
        


class CommentOnImage(APIView):
    
    def post(self, request, image_id, format=None):
        user = request.user
        try:
            found_image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.CommentSerializer(data=request.data) #put과 달리 입력한 데이트만 넘겨준다.
        if serializer.is_valid():
            serializer.save(creator = user, image=found_image)
            #Comment notification
            notification_views.create_notification(
                user, found_image.creator, 'comment', found_image,serializer.data['message'])
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Comment(APIView):
    def delete(self, request, comment_id, format=None):
        user = request.user
        try:
            comment = models.Comment.objects.get(id=comment_id, creator=user)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class Search(APIView):
    def get(self, request, format=None):
        # 주소창에 127.0.0.1:8000/images/search/?hashtags=cheap,hot girls 이라고 입력 후 반응을 체크할 것이다.
        # print(request.query_params) #request 할때마다 무슨 일이 일어나는지 볼 수 있음 --> <QueryDict: {'hashtags': ['cheap,hot girls']}>
        hashtags = request.query_params.get('hashtags', None) #hashtags 자료인것만 고르기
        print(hashtags) #cheap,hot girls
        if hashtags is not None:
            hashtags = hashtags.split(",")
            images = models.Image.objects.filter(tags__name__in=hashtags).distinct()# distinct()는 구분되기 떄문에 두번 검색되지 않음
        
        # tags__name__in의 뜻은 tags의 name으로 우선 필터링,
        # 나아가 name__in은 hashtags에 ['cheap','hot girls']이 있으면 cheep 혹은 hot girls 를 찾는다 
        # 즉 __in은 "__in=array"이란 형태에서 array의 요소를 하나하나 '='(같은지) 체크해준다. 일종의 반복문으로 길게 쓸것을 줄이는 개념이다.
            print(images)
        #title: 'hello',
        #location: 'bogota'
        #creator: (User:
        #    id:1
        #    username:'nomadmin'        
        #)
        #deep relationship
        # 우선 단순히 이미지 필터링을 지역이 'bogota'인 것으로 하고 싶으면 --> models.Image.objects.filter(location='bogota')
        # 이미지 필터링을 작성자 'nomadin'인 것으로 하고 싶으면 --> models.Image.objects.filter(creator__username='nomadmin')
        #  
        #models.Image.objects.filter(creator__username__contains='noma') #contain은 대소문자 구분 icontain  구분 안함
        #exact 정확히 단어별로 대소문자 구분 ,iexact 구분 안함
            serializer = serializers.CountImageSerializer(images, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
class ModerateComments(APIView):
    #본인의 이미지에 작성된 타인의 댓글 삭제 기능
    
    def delete(self, request, image_id, comment_id, format=None):
        user=request.user

        try:
            comment_to_delete = models.Comment.objects.get(
                id=comment_id, image__id=image_id, image__creator=user) #더블 언더바?
            #삭제하고자하는 댓글이 있고, 그 댓글의 이미지가 현재 사용자가 보고있는 이미지인지 확인하고, 그 사용자가 이미지의 생성자인지 찾으면 된다.
            #foreign key
            comment_to_delete.delete()
        except models.Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageDetail(APIView):
    def find_own_image(self, image_id, user): #같은 클래스에 있기 때문에 self는 필수
        try:    
            image = models.Image.objects.get(id=image_id, creator=user) #하지만 편집은 내 이미지만 가능해야함
            return image
        except models.Image.DoesNotExist:
            return None
            
    def get(self, request, image_id, format=None):
        
        user = request.user
        try:
            image = models.Image.objects.get(id=image_id) #내 이미지뿐만 아니라 다른 사람 이미지도 보임.
        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ImageSerializer(image)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, image_id, format=None):
        #put은 내용을 업데이트할 때 쓰인다. 사진 편집에 관한 함수이다.
        user=request.user
        image=self.find_own_image(image_id, user)

        if image is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED) #권한 없음

        serializer = serializers.InputImageSerializer(
            image, data=request.data, partial=True) 
        #업데이트(put)을 할 때 두가지를 살려본다. 1.대상이 될 오브젝트(ex. image) 2.넘겨받는 데이터(ex. data=request.data)
        #partial은 업데이트가 완성되지 않았을때 시리얼라이즈를 저장시키는 방법이다.
        if serializer.is_valid():
            serializer.save(creator=user) #사용자가 무조건 user일 때 저장시키기위해.
            return Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, image_id, format=None):
        user=request.user
        image=self.find_own_image(image_id, user)

        if image is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED) #권한 없음

        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)