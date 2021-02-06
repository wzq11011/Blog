from django.db import models

# Create your models here.
# 导入内建的User模型
from django.contrib.auth.models import User
# timezone用于处理时间相关事务
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image
from ckeditor.fields import RichTextField


# 文章栏目
class ArticleColumn(models.Model):

    title = models.CharField(max_length=100, blank=True)

    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


# 博客文章数据模型
class ArticlePost(models.Model):

    # 文章的栏目
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )

    # 文章标签
    tags = TaggableManager(blank=True)

    # 文章标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)

    # 文章作者，参数on_delete用于指定数据删除的方式
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # 文章标题。models.CharField为字符串字段，用于保存较短的字符串
    title = models.CharField(max_length=100)

    # 文章正文。保存大量文本使用TextField
    body = RichTextField()

    # 文章创建时间。参数 default=timezone.now 指定其在写入数据时默认写入当前时间
    created = models.DateTimeField(default=timezone.now())

    # 文章更新时间。参数 auto_now=True 指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)

    # 浏览量
    total_views = models.PositiveIntegerField(default=0)

    # 获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])

    # 保存时处理图片
    def save(self, *args, **kwargs):
        # 调用原有的 save() 的功能
        article = super(ArticlePost, self).save(*args, **kwargs)

        # 固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            x, y = image.size()
            new_x = 480
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)
        return article

    # 内部类Meta用于给model定义元数据
    class Meta:
        # ordering指定模型返回的数据的排列顺序
        # '-created'表明数据应当以倒序排列
        ordering = ('-created',)

    # __str__定义当前对象调用str()方法时返回的内容
    def __str__(self):
        # 将文章的标题返回
        return self.title





