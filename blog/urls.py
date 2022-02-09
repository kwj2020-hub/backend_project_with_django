from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.single_post_page), # blog/views.py의 single_post_page() 함수에 정의된 대로 처리
    path('', views.index),
]