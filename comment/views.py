from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from article.models import ArticlePost
from .forms import CommentForm
from .models import Comment
from notifications.signals import notify
from django.contrib.auth.models import User
from django.http import JsonResponse


# 文章评论
@login_required(login_url='/accounts/account_login')
def post_comment(request, article_id, parent_comment_id=None):
    article = get_object_or_404(ArticlePost, id=article_id)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.user = request.user

            # 二级评论
            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                # 若评论级数超过2级，则转换为2级
                new_comment.parent_id = parent_comment.get_root().id
                # 被回复人
                new_comment.reply_to = parent_comment.user
                new_comment.save()
                # 给其他用户发送通知

                notify.send(
                    sender=request.user,
                    recipient=parent_comment.user,
                    verb='回复了你',
                    target=article,
                    action_object=new_comment
                )
                return JsonResponse({"code": "200 OK", "new_comment_id": new_comment.id})

            new_comment.save()
            # 给管理员发送通知
            if not request.user.is_superuser:
                notify.send(
                    sender=request.user,
                    recipient=User.objects.filter(is_superuser=1),
                    verb='回复了你',
                    target=article,
                    action_object=new_comment
                )
            redirect_url = article.get_absolute_url() + '#comment_elem_' + str(new_comment.id)
            return redirect(redirect_url)
        else:
            return HttpResponse('表单内容有误，请重新填写')

    elif request.method == 'GET':
        comment_form = CommentForm()
        context = {'comment_form': comment_form, 'article_id': article_id, 'parent_comment_id': parent_comment_id}
        return render(request, 'comment/reply.html', context)

    else:
        return HttpResponse("仅接受POST和或ET请求")