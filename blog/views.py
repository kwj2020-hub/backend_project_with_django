from django.shortcuts import render, redirect     # render를 임포트해야 FBV 사용 가능
from django.views.generic import ListView, DetailView, CreateView, UpdateView   # ListView와 DetailView 클래스를 임포트해야 CBV 사용 준비 완료!
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from .models import Post, Category, Tag
from .forms import CommentForm
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify

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
        context['comment_form'] = CommentForm
        return context

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):   # 장고가 제공하는 CreateView를 상속받는 PostCreate 클래스...인데, LoginRequiredMixin 클래스를 또 상속받을 수 있는 이유는 Mixin이라는 개념을 사용했기 때문.
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category'] # Post 모델에 사용할 필드명을 리스트로 작성

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user    # 웹 사이트의 방문자를 의미
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):   # 웹 사이트의 방문자가 (슈퍼유저 또는 스태프로) 로그인한 상태인지 아닌지를 확인(is_authenticated)
            form.instance.author = current_user # form에서 생성한 instance의 author 필드에 current_user를 담음
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

            return response

        else:
            return redirect('/blog/') # redirect 함수를 통해 블로그로 돌아감

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']

    template_name = 'blog/post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response

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

def new_comment(request, pk):
    if request.user.is_authenticated:   # 비정상적인 접근에 대비해 로그인하지 않은 경우에는 PermissionDined를 발생시킴
        post = get_object_or_404(Post, pk=pk)   # pk를 인자로 받아 댓글을 달 포스트를 날려 쿼리를 가져옮. 해당하는 pk가 없으면 404를 출력하도록 get_object_or_404라는 기능을 활용

        if request.method == 'POST':    # 폼을 작성하고 submit하면 POST 방식으로 전달되지만, 브라우저 URL 입력으로 접근하는 경우 pk에 해당하는 포스트 페이지로 리다이렉트
            comment_form = CommentForm(request.POST)   # POST 방식으로 들어온 정보를 CommentForm의 형태로 가져옮.
            if comment_form.is_valid(): # 폼이 유효하게 작성되었다면 해당 내용으로 새로운 레코드를 만들어 데이터베이스에 저장함.
                comment = comment_form.save(commit=False)   # 바로 저장하는 기능을 잠시 미루고 comment_form에 담김 정보로 Comment 인스턴스만 가져오기
                comment.post = post     # pk로 가져온 포스트로 채우고
                comment.author = request.user   # 로그인한 사용자 정보로 채움.
                comment.save()  # 모든 작업을 끝내고 저장
                return redirect(comment.get_absolute_url()) # 마지막으로 comment의 URL로 리다이렉트!
        else:   # 폼을 작성하고 submit하면 POST 방식으로 전달되지만, 브라우저 URL 입력으로 접근하는 경우 pk에 해당하는 포스트 페이지로 리다이렉트
            return redirect(post.get_absolute_url())
    else:   # 비정상적인 접근에 대비해 로그인하지 않은 경우에는 PermissionDined를 발생시킴
        raise PermissionDenied

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