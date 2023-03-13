from django import forms
from .models import Posts, Comments

class PostForm(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ['title', 'user', 'post_content']
        labels = {
            'user' : 'Your username',
            'post_content' : '',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['user', 'post_content']
        labels = {
            'user' : 'Your username',
            'post_content' : ''
        }
