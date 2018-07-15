from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from nomadgram.users import models as user_models
from nomadgram.images import models as image_models

@python_2_unicode_compatible
class Notification(image_models.TimeStampedModel):
    
    TYPE_CHOICES=(
        ('like','Like'), #첫번째는 데이터베이스, 두번째는 어드민 패널
        ('comment', 'Comment'),
        ('follow', 'Follow'),
    )
    creator = models.ForeignKey(user_models.User, related_name='creator', on_delete=models.CASCADE)
    to = models.ForeignKey(user_models.User, related_name='to', on_delete=models.CASCADE)
    #그냥 같은 foreignkey를 사용하면 에러가 나므fh related_name으로 구분한다.
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)#선택적 요소는 choices 라는 걸 쓰네
    image = models.ForeignKey(image_models.Image, null=True, blank=True, on_delete=models.CASCADE)
    #이미지의 경우, 좋아요 혹은 댓글의 경우 이미지에 적용가능하지만, 이미지 자체를 팔로우 할 수 없으므로
    comment = models.TextField(
        null=True, blank=True) #누군가가 댓글을 달면 댓글을 볼 수 있음. 단 좋아요의 경우 댓글이 없으므로 null=True, blank=True

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return 'From: {} - To:{}'.format(self.creator, self.to)