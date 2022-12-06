from django.urls import path
from social_appe.views import Postlist,PostDetailView,PostEditView,PostDeleteView,CommentDeleteView,ProfileView,ProfileEditView,AddFollowers,RemoveFollowers,AddLike,AddDislike,UserSearch,ListFollowers,AddCommentLike,AddCommentDislike,Comment_Replay_View,PostNotification,FollowNotification,RemoveNotification,ListThreads,CreatThread,ThreadView,CreateMessage,ThreadNotification

urlpatterns = [
    path('',Postlist.as_view(),name='post_list'),
    path('post/<int:pk>',PostDetailView.as_view(),name="post_details"),
    path('post/edit/<int:pk>',PostEditView.as_view(),name='post_edit'),
    path('post/delete/<int:pk>',PostDeleteView.as_view(),name='post_delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>',CommentDeleteView.as_view(),name='comment_delete'),

    path('post/<int:pk>/like',AddLike.as_view(),name='like'),
    path('post/<int:pk>/dislike',AddDislike.as_view(),name='dislike'),
    path('post/<int:post_pk>/comment/<int:pk>/like',AddCommentLike.as_view(),name='comment_like'),
    path('post/<int:post_pk>/comment/<int:pk>/dislike',AddCommentDislike.as_view(),name='comment_dislike'),
    path('post/<int:post_pk>/comment/<int:pk>/replay',Comment_Replay_View.as_view(),name='comment_replay'),

    path('profile/<int:pk>',ProfileView.as_view(),name='profile'),
    path('profile/edit/<int:pk>',ProfileEditView.as_view(),name='profile_edit'),
    path('profile/<int:pk>/followers',ListFollowers.as_view(),name='list_followers'),

    path('profile/<int:pk>/followers/add',AddFollowers.as_view(),name='add_followers'),
    path('profile/<int:pk>/followers/remove',RemoveFollowers.as_view(),name='remove_followers'),
    path('search/',UserSearch.as_view(),name='profile_search'),

    path('notification/<int:notification_pk>/post/<int:post_pk>', PostNotification.as_view(), name='post-notification'),
    path('notification/<int:notification_pk>/profile/<int:profile_pk>', FollowNotification.as_view(), name='follow-notification'),
    path('notification/delete/<int:notification_pk>', RemoveNotification.as_view(), name='notification-delete'),
    path('notification/<int:notification_pk>/thread/<int:object_pk>',ThreadNotification.as_view(),name='thread-notification'),

    path('inbox',ListThreads.as_view(),name='inbox'),
    path('inbox/create_thread',CreatThread.as_view(),name='create_thread'),
    path('inbox/<int:pk>/',ThreadView.as_view(),name='thread'),
    path('inbox/<int:pk>/create_message/',CreateMessage.as_view(),name='create_message')
]