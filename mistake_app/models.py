# mistake_app/models.py
from django.db import models
from django.core.validators import FileExtensionValidator, MaxValueValidator
class Mistake(models.Model):
    SUBJECT_CHOICES = [
        ('chinese', '语文'),
        ('math', '数学'),
        ('english', '英语'),
        ('physics', '物理'),
        ('chemistry', '化学'),
        ('biology', '生物'),
        ('history', '历史'),
        ('geography', '地理'),
        ('politics', '政治'),
    ]
    
    question = models.TextField("题目内容")
    wrong_answer = models.TextField("错误答案")
    right_answer = models.TextField("正确答案")
    subject = models.CharField("科目", max_length=20, choices=SUBJECT_CHOICES)
    error_count = models.IntegerField("错误次数", default=1)
    add_date = models.DateTimeField("添加时间", auto_now_add=True)

    question_image = models.ImageField(
        "题目图片",
        upload_to='mistakes/',  # 图片存储在media/mistakes目录
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),  # 限制文件类型 # type: ignore
            MaxValueValidator(2*1024*1024)  # 最大2MB
        ]
    )

    def __str__(self):
        return f"{self.get_subject_display()} - {self.question[:20]}"

    class Meta:
        ordering = ['-add_date']
        verbose_name = "错题记录"
        verbose_name_plural = "错题记录"
