from django.urls import path
from . import views

urlpatterns = [
    path('about_me/', views.about_me),  # 도메인 뒤에 about me/가 붙었을 때 about_me() 함수로 대문 페이지 보여주기
    path('', views.landing),    # 도메인 뒤에 아무것도 없을 때 landing() 함수로 대문 페이지 보여주기
]