from django.shortcuts import render,redirect,HttpResponse
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .models import Post,Comment,UserProfile,Notification,ThreadModel,MessageModel,Image
from django.views import View
from .forms import PostForm,CommentForm,ThreadForm,MessageForm
from django.views.generic.edit import UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.

class Postlist(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        login_user = request.user
        posts=Post.objects.filter(author__profile__followers__in=[login_user.id]).order_by('-created_on')
        form=PostForm()
        content = {
            'post_list':posts,
            'form':form
        }
        return render(request,'social_appe/post_list.html',content)

    def post(self,request,*args,**kwargs):
        login_user = request.user
        posts = Post.objects.filter(author__profile__followers__in=[login_user.id]).order_by('-created_on')
        form = PostForm(request.POST,request.FILES)
        files=request.FILES.getlist('image')
        if form.is_valid():
            new_post=form.save(commit=False)
            new_post.author=request.user
            new_post.save()
            for f in files:
                img=Image(image=f)
                img.save()
                new_post.image.add(img)
            new_post.save()
        content = {
            'post_list': posts,
            'form': form
        }
        return render(request, 'social_appe/post_list.html', content)
class PostDetailView(LoginRequiredMixin,View):
    def get(self,request,pk,*args,**kwargs):
        post=Post.objects.get(pk=pk)
        form=CommentForm()
        comments = Comment.objects.filter(post=post).order_by('-created_on')
        content={
            'post':post,
            'form':form,
            'comments': comments
        }
        return render(request,'social_appe/post_details.html',content)
    def post(self,request,pk,*args,**kwargs):
        post=Post.objects.get(pk=pk)
        form=CommentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.post=post
            new_comment.author=request.user
            new_comment.save()
        comments = Comment.objects.filter(post=post).order_by('-created_on')
        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=post.author, post=post)
        content = {
            'post':post,
            'form':form,
            'comments':comments
        }
        return render(request,'social_appe/post_details.html',content)

class PostEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Post
    fields = ['body']
    template_name = 'social_appe/post_edit.html'

    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('post_details',kwargs={'pk':pk})

    def test_func(self):
        post=self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Post
    template_name = 'social_appe/post_delete.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        post=self.get_object()
        return self.request.user == post.author

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Comment
    template_name = 'social_appe/comment_delete.html'

    def get_success_url(self):
        pk=self.kwargs['post_pk']
        return reverse_lazy('post_details',kwargs={'pk':pk})

    def test_func(self):
        post=self.get_object()
        return self.request.user == post.author

class ProfileView(View):
    def get(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        user=profile.user
        posts=Post.objects.filter(author=user).order_by('-created_on')

        followers=profile.followers.all()
        if len(followers) == 0:
            is_following = False

        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False

        number_of_followers=len(followers)

        content={
            'user':user,
            'profile':profile,
            'posts':posts,
            'number_of_followers':number_of_followers,
            'is_following':is_following
        }
        return render(request,'social_appe/profile.html',content)

class ProfileEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = UserProfile
    fields = ['name','bio','birth_date','location','picture']
    template_name = 'social_appe/profile_edit_form.html'

    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('profile',kwargs={'pk':pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

class AddFollowers(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)
        notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=profile.user)
        return redirect('profile',pk=profile.pk)

class RemoveFollowers(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        return redirect('profile',pk=profile.pk)

class AddLike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        post=Post.objects.get(pk=pk)

        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            post.dislikes.remove(request.user)

        is_like=False
        for likes in post.likes.all():
            if likes == request.user:
                is_like = True
                break
        if not is_like:
            post.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.author,
                                                       post=post)

        if is_like:
            post.likes.remove(request.user)
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class AddDislike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        post = Post.objects.get(pk=pk)

        is_like = False
        for likes in post.likes.all():
            if likes == request.user:
                is_like = True
                break
        if is_like:
            post.likes.remove(request.user)

        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if not is_dislike:
            post.dislikes.add(request.user)
        if is_dislike:
            post.dislikes.remove(request.user)
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class UserSearch(View):
    def get(self,request,*args,**kwargs):
        query=self.request.GET.get('query')
        profile=UserProfile.objects.filter(Q(user__username__icontains=query))
        content={
            'profile_list':profile
        }
        return render(request,'social_appe/search.html',content)

class ListFollowers(View):
    def get(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        followers=profile.followers.all()

        content={
            'profile':profile,
            'followers':followers
        }
        return render(request,'social_appe/followers_list.html',content)


class AddCommentLike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        comment=Comment.objects.get(pk=pk)

        is_dislike = False
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            comment.dislikes.remove(request.user)

        is_like=False
        for likes in comment.likes.all():
            if likes == request.user:
                is_like = True
                break
        if not is_like:
            comment.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=comment.author,
                                                       comment=comment)

        if is_like:
            comment.likes.remove(request.user)
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class AddCommentDislike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        comment = Comment.objects.get(pk=pk)

        is_like = False
        for likes in comment.likes.all():
            if likes == request.user:
                is_like = True
                break
        if is_like:
            comment.likes.remove(request.user)

        is_dislike = False
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if not is_dislike:
            comment.dislikes.add(request.user)
        if is_dislike:
            comment.dislikes.remove(request.user)
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class Comment_Replay_View(LoginRequiredMixin,View):
    def post(self,request,post_pk,pk,*args,**kwargs):
        post=Post.objects.get(pk=post_pk)
        parent_comment=Comment.objects.get(pk=pk)
        form=CommentForm(request.POST)

        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent=parent_comment
            new_comment.save()
        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=parent_comment.author, comment=new_comment)
        return redirect('post_details',pk=post_pk)

class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('post_details', pk=post_pk)

class FollowNotification(View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        profile = UserProfile.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('profile', pk=profile_pk)


class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)

        notification.user_has_seen = True
        notification.save()

        return HttpResponse('Success', content_type='text/plain')

class ListThreads(View):
    def get(self,request,*args,**kwargs):
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))
        content={
            'threads' : threads
        }
        return render(request,'social_appe/inbox.html',content)

class CreatThread(View):
    def get(self,request,*args,**kwargs):
        form =ThreadForm()
        content = {
            'form':form
        }
        return render(request,'social_appe/create_thread.html',content)
    def post(self,request,*args,**kwargs):
        form = ThreadForm(request.POST)
        username = request.POST.get('username')
        print(username)
        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(user=request.user,receiver=receiver).exists():
                thread = ThreadModel.objects.filter(user=request.user,receiver=receiver)[0]
                return redirect('thread',pk=thread.pk)
            elif ThreadModel.objects.filter(user=receiver,receiver=request.user).exists():
                thread = ThreadModel.objects.filter(user=receiver,receiver=request.user)[0]
                return redirect('thread',pk=thread.pk)
            if form.is_valid():
                thread = ThreadModel(user=request.user,receiver=receiver)
                thread.save()
                return redirect('thread',pk=thread.pk)
        except Exception as e:
            print(e)
            messages.info(request,'invalid username')
            return redirect('create_thread')

class ThreadView(View):
    def get(self,request,pk,*args,**kwargs):
        form=MessageForm()
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)
        content = {
            'thread' :thread,
            'form':form,
            'message_list':message_list
        }
        return render(request,'social_appe/thread.html',content)

# class CreateMessage(View):
#     def post(self,request,pk,*args,**kwargs):
#         # form=MessageForm(request.POST,request.FILES)
#         thread = ThreadModel.objects.get(pk=pk)
#         if thread.receiver == request.user:
#             receiver = thread.user
#         else:
#             receiver = thread.receiver
#         message = MessageModel(thread=thread,
#                                send_user=request.user,
#                                receiver_user=receiver,
#                                body=request.POST.get('message'))
#         message.save()
#         notification = Notification.objects.create(
#             notification_type=4,
#             from_user=request.user,
#             to_user=receiver,
#             thread = thread
#         )
#         return redirect('thread',pk=pk)

class CreateMessage(View):
    def post(self,request,pk,*args,**kwargs):
        form=MessageForm(request.POST,request.FILES)
        thread = ThreadModel.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.send_user = request.user
            message.receiver_user=receiver
            message.save()

        notification = Notification.objects.create(
            notification_type=4,
            from_user=request.user,
            to_user=receiver,
            thread = thread
        )
        return redirect('thread',pk=pk)




class ThreadNotification(View):
    def get(self, request, notification_pk, object_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        thread= ThreadModel.objects.get(pk=object_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('thread', pk=object_pk)