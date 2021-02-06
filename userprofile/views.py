from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm


# 用户登陆
def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            # cleaned_data用于清理出合法数据
            data = user_login_form.cleaned_data
            # 检验账号密码是否匹配数据库中的某个用户
            # 若均匹配则返回这个user对象
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                login(request, user)
                return redirect('article:article_list')
            else:
                return HttpResponse("账号或密码输入有误")
        else:
            return HttpResponse("账号或密码输入不合法")

    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = {'form': user_login_form}
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse("请使用POST或GET方法请求数据")


# 用户登出
def user_logout(request):
    logout(request)
    return redirect("article:article_list")


# 用户注册
def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            # 保存好数据后立刻登陆并返回至文章列表
            login(request, new_user)
            return redirect('article:article_list')
        else:
            return HttpResponse('注册表单输入有误，请重新输入')

    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {'form': user_register_form}
        return render(request, 'userprofile/register.html', context)
    else:
        return HttpResponse("请使用GET或POST请求上传数据！")


# 用户删除
@login_required(login_url='/userprofile/login/')
def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        # 验证登录用户和待删除用户是否相同
        if request.user == user:
            # 退出登陆，删除数据并返回文章列表
            logout(request)
            user.delete()
            return redirect('article:article_list')
        else:
            return HttpResponse("你没有删除操作的权限")

    else:
        return HttpResponse('仅接受POST请求')


# 编辑用户信息
@login_required(login_url='/userprofile/login')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    # profile = Profile.objects.get(user_id=id)
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        if request.user != user:
            return HttpResponse("你没有权限修改此账户的信息")

        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd['avatar']
            profile.save()
            return redirect("userprofile:edit", id=id)
        else:
            return HttpResponse('注册表单有误，请重新输入')

    elif request.method == 'GET':
        context = {'profile': profile, 'user': user}
        return render(request, 'userprofile/edit.html', context)

    else:
        return HttpResponse("请使用POST或GET请求")


















