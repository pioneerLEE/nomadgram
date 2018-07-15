from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from nomadgram.users import models as users_models
from taggit.managers import TaggableManager

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
    creator = models.ForeignKey(users_models.User,on_delete=models.CASCADE, null=True, related_name='images')
    tags = TaggableManager()

    @property
    def like_count(self):
        return self.likes.all().count()

    @property
    def comment_count(self):
        return self.comments.all().count()

    def __str__(self):
        return '{} - {}'.format(self.location, self.caption)

    class Meta:
        ordering = ['-created_at'] #생성된 시간 순으로(최근 순으로) 정렬할 수 있게끔 하는 메타이다
        #메타 클래스는 이처럼 모델의 설정을 위해서 사용함


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