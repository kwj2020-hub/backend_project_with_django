from django.shortcuts import render     # render를 임포트해야 FBV 사용 가능
from django.views.generic import ListView, DetailView   # ListView와 DetailView 클래스를 임포트하여 CBV 사용 준비 완료!
from .models import Post, Category, Tag

class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list' : post_list,   # 포스트 중에서 Category.objects.get(slug=slug) 로 필터링한 카테고리만 가져오기
            'categories' : Category.objects.all(),  # 페이지의 오른쪽에 위치한 카테고리 카드를 정의
            'no_category_post_count' : Post.objects.filter(category=None).count(),  # 카테고리 가트 맨 아래에 미분류 포스트와 그 개수를 알려주기
            'category' : category,  # 페이지 타이틀 옆에 카테고리 이름을 알려주기
        }
    )

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'tag': tag,
            'categories': Category.objects.all(),
            'no_category_post_count' : Post.objects.filter(category=None).count(),
        }
    )

# 기존 FBV 스타일의 함수는 주석 처리
# def index(request):
#     posts = Post.objects.all().order_by('-pk')
#     # all()은 데이터베이스의 데이터를 모두 가져오기 위한 쿼리(query)입니다.
#
#     return render(
#         request,
#         'blog/post_list.html',
#         {
#             'posts': posts,
#         }
#     )

# def single_post_page(request, pk):  # blog/urls.py에서 불러올 함수
#     post = Post.objects.get(pk=pk)  # pk는 primary key의 약자로
#     # 해당 함수의 매개변수로 지정하여 Post 모델의 pk 필드 값이 매개변수로 받은 pk와 같은 레코드를 가져오라는 의미
#
#     return render(
#         request,
#         'blog/post_detail.html',
#         {
#             'post' : post,
#         }
#     )