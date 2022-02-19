from django.urls import path
from . import views

urlpatterns = [
    path('category/<str:slug>/', views.category_page), # category/ 뒤에 문자열이 붙는 URL을 입력하면 그 문자열은 views.py에 정의할 category_page() 함수의 매개변수인 slug의 인자로 넘겨주도록 설정
    path('<int:pk>/', views.PostDetail.as_view()),
    path('', views.PostList.as_view()),   # URL 끝이 /blog/일 때는 PostList 클래스로 처리하도록 수정
    # path('<int:pk>/', views.single_post_page), # blog/views.py의 single_post_page() 함수에 정의된 대로 처리
    # path('', views.index),
]