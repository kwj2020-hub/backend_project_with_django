from django.shortcuts import render
from .models import Post

def index(request):
    posts = Post.objects.all().order_by('-pk')
    # all()은 데이터베이스의 데이터를 모두 가져오기 위한 쿼리(query)입니다.

    return render(
        request,
        'blog/index.html',
        {
            'posts': posts,
        }
    )