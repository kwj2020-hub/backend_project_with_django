from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
import os # get_file_name() 함수를 위한 os 모듈 불러오기

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'   # Category 모델에 고유 URL을 만드는 법을 정의

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'   # Category 모델에 고유 URL을 만드는 법을 정의

    class Meta:
        verbose_name_plural = 'Categories'

class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = MarkdownxField()
    # 주의사항: django 4.0이 url 함수를 삭제한 탓에 markdownx가 django 4.0을 지원하지 못하는 관계로 django 버전을 3.2로 다운그레이드하여 문제를 해결한 상태

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)   # blank=True는 해당 필드는 필수항목은 아니라는 뜻
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]
    # 모델의 레코드별 URL 생성 규칙을 정의하는 함수: URL은 도매인 뒤에 /blog/레코드의 pk/

    def get_content_markdown(self):
        return markdown(self.content)

class Comment(models.Model):    # 댓글 기능을 위한 모델
    post = models.ForeignKey(Post, on_delete=models.CASCADE)    # 어떤 포스트에 담을 댓글인지를 저장하는 필드
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 작성자를 저장하는 필드
    content = models.TextField()    # 댓글 내용을 담는 필드
    created_at = models.DateTimeField(auto_now_add=True)    # 작성일시를 담는 필드
    modified_at = models.DateTimeField(auto_now=True)   # 수정일시를 담는 필드

    def __str__(self):  # 작성자명과 댓글 내용을 출력하는 함수
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'