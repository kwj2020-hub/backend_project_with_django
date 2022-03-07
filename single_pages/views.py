from django.shortcuts import render
from blog.models import Post

# URL을 불러오기 위한 함수 정의
def landing(request):
    recent_posts = Post.objects.order_by('-pk')[:3]
    return render(
        request,
        'single_pages/landing.html',
        {
            'recent_posts': recent_posts,
        }
    )

def about_me(request):
    return render(
        request,
        'single_pages/about_me.html'
    )