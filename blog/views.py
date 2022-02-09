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

def single_post_page(request, pk):  # blog/urls.py에서 불러올 함수
    post = Post.objects.get(pk=pk)  # pk는 primary key의 약자로
    # 해당 함수의 매개변수로 지정하여 Post 모델의 pk 필드 값이 매개변수로 받은 pk와 같은 레코드를 가져오라는 의미
    
    return render(
        request,
        'blog/single_post_page.html',
        {
            'post' : post,
        }
    )