from rest_framework.views import APIView
from rest_framework.response import Response
from . import models, serializers
from rest_framework import status
from nomadgram.notifications import views as notification_views
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView

class ExploreUsers(APIView):
    def get(self, request, format = None):
        
        last_five = models.User.objects.all().order_by('-date_joined')[:5]

        serializer = serializers.ListUserSerializer(last_five, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)
        
class FolloewUser(APIView):
    def post(self, request, user_id, format=None):
        
        user = request.user
        
        
        try: 
            user_to_follow = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user.following.add(user_to_follow)
        user.save()
        #누군가가 자신을 팔로우하면 follow notification
        notification_views.create_notification(user,user_to_follow,'follow')
        return Response(status=status.HTTP_200_OK)

class UnFolloewUser(APIView):
    def post(self, request, user_id, format=None):
        
        user = request.user
        try: 
            user_to_follow = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user.following.remove(user_to_follow)
        user.save()
        return Response(status=status.HTTP_200_OK)

class UserProfile(APIView):
    def get_user(self,username):
        try:
            found_user = models.User.objects.get(username=username)
            return found_user
        except models.User.DoesNotExist:
            return None
    def get(self, request, username, format=None):
        found_user=self.get_user(username)

        if found_user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.UserProfileSerializer(found_user)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, username, format=None):
        user = request.user

        found_user = self.get_user(username)
        
        if found_user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif found_user.username != user.username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = serializers.UserProfileSerializer(
                found_user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #주의가 있다면 website에 넣는 인풋값은 http:/ilovemymom.com 같이 형식을 맞춰어야한다.

class UserFollowers(APIView):
    
    def get(self, request, username, format=None):
   
        try:
            found_user = models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_followers = found_user.followers.all()

        serializer = serializers.ListUserSerializer(user_followers, many = True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class UserFollowing(APIView):
    
    def get(self, request, username, format=None):
        
        try:
            found_user = models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_following = found_user.following.all()

        serializer = serializers.ListUserSerializer(user_following, many = True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class Search(APIView):
    def get(self, request, format=None):

        username = request.query_params.get('username', None) 

        if username is not None:

            users = models.User.objects.filter(username__istartswith=username)
            #icontains 으로 하면 너무 많은 경우가 나오기 때문에 istartswith(~로 시작하는 데이터)

            serializer = serializers.ListUserSerializer(users, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ChangePassword(APIView):

    def put(self, request, username, format=None):
        #https://docs.djangoproject.com/en/1.11/ref/contrib/auth/#django.contrib.auth.models.User.check_password
        #check Password Documentation 
        #Returns True if the given raw string is the correct password for the user.

        user = request.user

        current_password = request.data.get('current_password', None)

        if current_password is not None:
            
            passwords_match = user.check_password(current_password)

            if passwords_match:
                
                new_password = request.data.get('new_password', None)

                if new_password is not None:
                    
                    user.set_password(new_password)

                    user.save()
                    return Response(status=status.HTTP_200_OK)
                
                else :
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            else :
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else :
            return Response(status=status.HTTP_400_BAD_REQUEST)

class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter