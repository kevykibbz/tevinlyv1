
from django.urls import path
from django import views
from . import views
from .views import *
from django.contrib.auth import views as auth_views
urlpatterns=[
    path('',Home.as_view(),name='dashboard'),
    path('subscribe',views.subscribe,name='subscribe'),
    path('accounts/login',Login.as_view(),name='login'),
    path('accounts/register',Register.as_view(),name='register'),
    path('accounts/logout',views.UserLogout,name='logout'),
    path('accounts/activate',views.account_activate,name='account activate'),
    path('accounts/activate/<uidb64>/<token>', views.acc_acctivate,name='activate'),

    path('accounts/reset/password',auth_views.PasswordResetView.as_view(form_class=User_resetPassword,template_name='manager/password_reset.html'),{'site_name':'devme','title':'Password reset'},name='password_reset'),
    path('accounts/reset/password/done',auth_views.PasswordResetDoneView.as_view(template_name='manager/password_reset_done.html'),name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name='manager/password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset/password/success',auth_views.PasswordResetCompleteView.as_view(template_name='manager/password_reset_complete.html'),name='password_reset_complete'),

    path('<username>', Profile.as_view(),name='profile'),
    path('password/change',views.passwordChange,name='password change'),
    path('edit/social/links',views.edit_social_link,name='edit social link'),
    path('change/profile/pic',views.profilePic,name='profile pic'),


    path('site/users',views.users,name='users'),
    path('add/users',AddUser.as_view(),name='add users'),
    path('edit/users/<id>',EditUser.as_view(),name='edit user'),
    path('delete/users/<id>',views.deleteUser,name='delete user'),

    path('site/settings',EditSite.as_view(),name='site settings'),
    path('site/contact',views.siteContact,name='site contact'),
    path('site/working/days',views.siteWorking,name='site working days'),
    path('site/social/links',views.siteSocial,name='site social links'),
    path('site/chats',views.chats,name='chats'),

    path('site/blogs',views.blogs,name='blogs'),
    path('site/blogs/details',blogsDetails.as_view(),name='blogs details'),



    path('site/projects',views.projects,name='projects'),
    path('add/project',AddProject.as_view(),name='add project'),
    path('edit/project/<id>',EditProject.as_view(),name='edit project'),
    path('delete/project/<id>',views.deleteProject,name='delete project'),

    path('designs/and/clients',views.designs,name='designs'),
    path('add/skill',AddSkill.as_view(),name='add skill'),
    path('edit/skill/<id>',EditSkill.as_view(),name='edit skill'),
    path('delete/skill/<id>',views.deleteSkill,name='delete skill'),


    path('site/reviews',views.reviews,name='reviews'),
    path('add/review',AddReview.as_view(),name='add review'),
    path('edit/review/<id>',EditReview.as_view(),name='edit review'),
    path('delete/review/<id>',views.deleteReview,name='delete review'),

]