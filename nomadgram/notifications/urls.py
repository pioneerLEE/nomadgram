from django.conf.urls import url #url을 만들기 위한 장고의 function
from . import views
app_name = "notifications"
urlpatterns =[
    url(
        regex = r'^$',
        view = views.Notifications.as_view(),
        name = 'notifications'
    ),
    

]
