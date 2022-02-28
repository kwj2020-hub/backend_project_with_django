from django.shortcuts import render, redirect     # render를 임포트해야 FBV 사용 가능
from django.views.generic import ListView, DetailView, CreateView   # ListView와 DetailView 클래스를 임포트하여 CBV 사용 준비 완료!
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):   # 장고가 제공하는 CreateView를 상속받는 PostCreate 클래스...인데, LoginRequiredMixin 클래스를 또 상속받을 수 있는 이유는 Mixin이라는 개념을 사용했기 때문.
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category'] # Post 모델에 사용할 필드명을 리스트로 작성

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user    # 웹 사이트의 방문자를 의미
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):   # 웹 사이트의 방문자가 (슈퍼유저 또는 스태프로) 로그인한 상태인지 아닌지를 확인(is_authenticated)
            form.instance.author = current_user # form에서 생성한 instance의 author 필드에 current_userfmf ekadma
            return super(PostCreate, self).form_valid(form) # CreateView의 form_valid() 함수에 현재 form을 인자로 보내 처리
        else:
            return redirect('/blog/') # redirect 함수를 통해 블로그로 돌아감

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