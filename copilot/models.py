from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Content(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    SAFETY_STATUS_CHOICES = [
        ('safe', 'Ваш контент прошел проверку на безопасность :)'),
        ('potentially_unsafe', 'В вашем контенте могут содержаться опасные материалы :O'),
        ('unsafe', 'Ваш контент содержит опасные материалы :('),
    ]

    file = models.FileField(upload_to='content/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    safety_status = models.CharField(max_length=20, choices=SAFETY_STATUS_CHOICES, default='safe')
    # user = models.ForeignKey(User, on_delete=models.CASCADE) # Uncomment when user model is implemented

    def __str__(self):
        return f'{self.file_type} - {self.file.name}'

class ModerationResult(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE, related_name='moderation_result')
    analyzed_at = models.DateTimeField(auto_now_add=True)
    detected_tags = models.ManyToManyField(Tag, blank=True)
    ai_analysis_raw = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Result for {self.content.file.name} - {self.content.safety_status}'


