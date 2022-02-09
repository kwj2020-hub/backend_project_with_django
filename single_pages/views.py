from django.shortcuts import render

# URL을 불러오기 위한 함수 정의
def landing(request):
    return render(
        request,
        'single_pages/landing.html'
    )

def about_me(request):
    return render(
        request,
        'single_pages/about_me.html'
    )