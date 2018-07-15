from django.db import models
from nomadgram.users import models as users_models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class TimeStampedModel(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True) #새로운 모델이 처음으로 생성할때마다 시간이 입력되게끔
    updated_at = models.DateTimeField(auto_now=True) #만들어질때마다(업데이트) 시간이 입력되게끔

    class Meta:
        abstract = True

@python_2_unicode_compatible
class Image(TimeStampedModel):
    
    """ Image Model"""

    file = models.ImageField()
    location = models.CharField(max_length=140)
    caption = models.TextField()
    creator = models.ForeignKey(users_models.User,on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '{} - {}'.format(self.location, self.caption)


@python_2_unicode_compatible
class Comment(TimeStampedModel):
    
    """ Comment Model"""

    message = models.TextField()
    creator = models.ForeignKey(users_models.User,on_delete=models.CASCADE, null=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, related_name='comments')

    def __str__(self):
        return self.message


@python_2_unicode_compatible
class Like(TimeStampedModel):
    
    """ Like Model"""

    creator = models.ForeignKey(users_models.User,on_delete=models.CASCADE, null=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, related_name='likes')

    def __str__(self):
        return 'User : {} - Image Caption : {}'.format(self.creator.username, self.image.caption)
        #로그인 시스템 상 username만 저장되어 있지, 그냥 name은 아직 현 시점의 DB에 저장되어 있지 않다.