from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost, ArticleColumn
import markdown
from .forms import ArticlePostForm
from django.contrib.auth.admin import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
from comment.forms import CommentForm


# 文章列表
def article_list(request):

    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    # 初始化查询集合
    article_list = ArticlePost.objects.all()

    if search:
        article_list = article_list.filter(
            Q(title__icontains=search)|
            Q(body__icontains=search)
        )
    else:
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    # 每页显示一篇文章
    paginator = Paginator(article_list, 3)
    # 获取URL中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给articles
    articles = paginator.get_page(page)

    # 需要传递给模板(templates)的对象
    context = {'articles': articles, 'order': order, 'search': search, 'column': column, 'tag': tag}
    # render函数，载入模板，并返回context对象
    return render(request, 'article/list.html', context)


# 文章详情
def article_detail(request, id):
    # 取出相应的文章
    article = ArticlePost.objects.get(id=id)

    # 取出相应评论
    comments = Comment.objects.filter(article=id)

    comment_form = CommentForm()

    # 浏览量+1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # 将markdown语法渲染成html样式
    md = markdown.Markdown(
        extensions=[
            # 包含缩写，表格等常用拓展
            'markdown.extensions.extra',
            # 语法高亮拓展
            'markdown.extensions.codehilite',
            # 目录拓展
            'markdown.extensions.toc',
        ])
    article.body = md.convert(article.body)

    # 需要传递给模板的对象
    context = {'article': article, 'toc': md.toc, 'comments': comments, 'comment_form': comment_form}
    # 载入模板，并返回context对象
    return render(request, 'article/detail.html', context)


# 写文章
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户请求类型
    if request.method == 'POST':
        # 将django表单类与数据进行绑定
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断表单数据有效性(是否符合数据模型)
        if article_post_form.is_valid():
            # 若数据有效，则保存(commit=False表明先不提交到数据库)
            new_article = article_post_form.save(commit=False)
            # 获取作者信息
            new_article.author = User.objects.get(id=request.user.id)
            # 获取文章栏目信息
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 提交数据至数据库
            new_article.save()
            # 保存tags多对多关系
            article_post_form.save_m2m()
            # 重定向回文章列表页
            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写")
    # 用户请求为GET的情况
    else:
        # 创建空的表单数据
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 将空表单数据返回
        context = {'article_post_form': article_post_form, 'columns': columns}
        return render(request, 'article/create.html', context)


# 删除文章
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method == 'POST':
        # 根据id获取需要删除的文章
        article = ArticlePost.objects.get(id=id)

        if request.user != article.author:
            return HttpResponse("抱歉，您无权删除此文章")
        else:
            # 调用delete()方法删除
            article.delete()
            # 重定向回文章列表
            return redirect("article:article_list")

    else:
        return HttpResponse("仅允许POST请求")


# 修改文章
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    # 提取需要修改的文章对象
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改此文章")

    else:
        # 判断用户请求类型
        if request.method == 'POST':
            # 将提交的数据复制到表单实例中
            article_post_form = ArticlePostForm(data=request.POST)
            # 判断提交的数据的有效性
            if article_post_form.is_valid():
                # 将原文章的title、body和column用提交的内容替换
                article.title = request.POST['title']
                article.body = request.POST['body']
                if request.POST['column'] != 'none':
                    article.column = ArticleColumn.objects.get(id=request.POST['column'])
                else:
                    article.column = None
                if request.FILES.get('avatar'):
                    article.avatar = request.FILES.get('avatar')
                article.tags.set(*request.POST.get('tags').split(','), clear=True)
                article.save()
                # 重定向回该文章详情页
                return redirect("article:article_detail", id=id)
            else:
                return HttpResponse("表单内容有误，请重新填写")
        else:
            article_post_form = ArticlePostForm(initial={'body': article.body})
            columns = ArticleColumn.objects.all()
            tags = ','.join([x for x in article.tags.names()])
            # 赋值上下文，将article对象也传递进去，用以提取旧文章内容
            context = {'article': article, 'article_post_form': article_post_form, 'columns': columns, 'tags': tags}
            return render(request, 'article/update.html', context)

