from django.conf.urls import url #url을 만들기 위한 장고의 function
from . import views
app_name = "images"
urlpatterns =[
    url(
        regex = '^all/$',
        view = views.ListAllImage.as_view(),
        name = 'all_images'
    ),url(
        regex = '^comments/$',
        view = views.ListAllComments.as_view(),
        name = 'all_Comments'
    ),url(
        regex = '^likes/$',
        view = views.ListAllLikes.as_view(),
        name = 'all_Likes'
    )

]