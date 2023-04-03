from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        help_texts = {
            "text": "Введите или отредактируйте текст",
            "group": "Выбирете группу к которой относится ваш пост",
            "image": "Ну и чьё фото ты сюда влепишь",
        }

        fields = ('text', 'group', 'image')

        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
