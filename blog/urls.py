from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.PostDetail.as_view()),
    path('', views.PostList.as_view()),   # URL 끝이 /blog/일 때는 PostList 클래스로 처리하도록 수정
    # path('<int:pk>/', views.single_post_page), # blog/views.py의 single_post_page() 함수에 정의된 대로 처리
    # path('', views.index),
]