from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from tinymce.models import HTMLField
# Create your models here.

class Posts(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    user = models.CharField(max_length=100, db_index=True)
    post_content = HTMLField()
    inital_post_date = models.DateTimeField()
    last_modified_post_date = models.DateTimeField()
    slug = models.SlugField(unique=True)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Posts, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Posts'

    def __str__(self):
        return f'"{self.title}" by {self.user}'

class Comments(models.Model):
    user = models.CharField(max_length=100, db_index=True)
    post_content = HTMLField()
    inital_post_date = models.DateTimeField()
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='comments', null=True)
    votes = models.IntegerField(default=0)
    class Meta:
        verbose_name_plural = 'Comments'
    def __str__(self):
        return f'{self.user}'
