from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        # exclude = ('post', 'author', 'created_at', 'modified_at',)
        # 위에서처럼 별도로 필드를 지정해도 되지만 exclude를 써서 몇 개의 필드만 제외하는 방식으로 해도 됩니다.

        