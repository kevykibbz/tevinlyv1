import dataclasses
from django.shortcuts import render
from manager.decorators import unauthenticated_user,allowed_users
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import *
from django.contrib.auth.models import User,Group,Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import View
from django.template.loader import get_template
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse,HttpResponse,HttpResponseBadRequest
from installation.models import SiteConstants
from .forms import *
from django.core.paginator import Paginator
from django.contrib.sites.shortcuts import get_current_site
from .addons import send_email,getSiteData
import json
from .tokens import create_token
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.humanize.templatetags.humanize import intcomma
from django import template
import math
from django.utils.crypto import get_random_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.templatetags.static import static
from installation.models import SiteConstants
import re
from six.moves import urllib
import environ
env=environ.Env()
environ.Env.read_env()
from xhtml2pdf import pisa

def generate_id():
    return get_random_string(6,'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKMNOPQRSTUVWXYZ0123456789')

class Home(View):
    def get(self,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=User.objects.filter(is_superuser=True).first()
        coding_skills=DesignModel.objects.filter(category__icontains='Coding skills').order_by("-id")
        design_skills=DesignModel.objects.filter(category__icontains='Design Skills').order_by("-id")
        reviews=ReviewModel.objects.all().order_by("-id")[:5]
        projects=Project.objects.all().order_by("-id")[:20]
        total_projects=Project.objects.all().count()
        subscribe_form=SubscriberForm()
        contact_form=ContactForm()
        data={
            'title':f'Welcome to {obj.site_name}',
            'obj':obj,
            'data':request.user,
            'subscribe_form':subscribe_form,
            'contact_form':contact_form,
            'user':user,
            'coding_skills':coding_skills,
            'design_skills':design_skills,
            'reviews':reviews,
            'projects':projects,
            'total_projects':total_projects,
        }
        return render(request,'manager/index.html',context=data)
    def post(self,request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form=ContactForm(request.POST or None)
            if form.is_valid():
                form.save()
                return JsonResponse({'valid':True,'message':'success:message sent!'},content_type='application/json')
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#subscriber
def subscribe(request,*args,**kwargs):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        form=SubscriberForm(request.POST or None)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'success:subscribed successfully'},content_type='application/json')
        return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')


#Login
@method_decorator(unauthenticated_user,name='dispatch')
class Login(View):
    def get(self,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        form=UserSignIn()
        data={
            'title':'Login',
            'obj':obj,
            'form':form,
            'data':request.user,
            'login':True,
        }
        return render(request,'manager/login.html',context=data)
    def post(self,request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            key=request.POST['username']
            password=request.POST['password1']
            if key:
                if password:
                    regex=re.compile(r'([A-Za-z0-9+[.-_]])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
                    if re.fullmatch(regex,key):
                        #email address
                        if User.objects.filter(email=key).exists():
                            data=User.objects.get(email=key)
                            user=authenticate(username=data.username,password=password)
                        else:
                            form_errors={"username": ["Invalid email address."]}
                            return JsonResponse({'valid':False,'uform_errors':form_errors},content_type="application/json")
                    else:
                        #username
                        if User.objects.filter(username=key).exists():
                            user=authenticate(username=key,password=password)
                        else:
                            form_errors={"username": ["Invalid username."]}
                            return JsonResponse({'valid':False,'uform_errors':form_errors},content_type="application/json")
                        
                    if user is not None:
                        if 'remember' in request.POST:
                           request.session.set_expiry(1209600) #two weeeks
                        else:
                           request.session.set_expiry(0) 
                        login(request,user)
                        return JsonResponse({'valid':True,'message':'success:Login Successfully.','login':True},content_type="application/json")
                    form_errors={"password1": ["Password is incorrect."]}
                    return JsonResponse({'valid':False,'uform_errors':form_errors},content_type="application/json")
                else:
                    form_errors={"password1": ["Password is required."]}
                    return JsonResponse({'valid':False,'uform_errors':form_errors},content_type="application/json")
            else:
                form_errors={"username": ["Username/Email Address is required."]}
                return JsonResponse({'valid':False,'uform_errors':form_errors},content_type="application/json")

#logout
def UserLogout(request):
    logout(request)
    return redirect('/accounts/login')

#user register view
@method_decorator(unauthenticated_user,name='dispatch')
class Register(View):
    def get(self,request):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        form=UserReg()
        form2=EProfileForm()
        subscribe_form=SubscriberForm()
        data={'title':'Account | Register','form2':form2,'form':form,'subscribe_form':subscribe_form,'obj':obj}
        return render(request,'manager/register.html',context=data)

    def post(self,request):
        if  request.headers.get('x-requested-with') == 'XMLHttpRequest':
            uform=UserReg(request.POST or None)
            eform=EProfileForm(request.POST , request.FILES or None)
            if uform.is_valid() and  eform.is_valid():
                userme=uform.save(commit=False)
                userme.is_active = True
                userme.save()
                extended=eform.save(commit=False)
                extended.user=userme
                extended.is_client=True
                extended.role='Client'
                extended.initials=uform.cleaned_data.get('first_name')[0].upper()+uform.cleaned_data.get('last_name')[0].upper()
                extended.save()
                return JsonResponse({'valid':True,'message':'Registered successfully','register':True},content_type="application/json")
            else:
                return JsonResponse({'valid':False,'uform_errors':uform.errors,'eform_errors':eform.errors},content_type="application/json")

#activate account view
def account_activate(request):
    obj=SiteConstants.objects.count()
    if obj == 0:
        return redirect('/site/installation/')
    obj=SiteConstants.objects.all()[0]
    subscribe_form=SubscriberForm()
    data={'title':'Account activate link sent!','subscribe_form':subscribe_form,'obj':obj}
    return render(request,'manager/sent_activation_done.html',context=data)


#activate user
def acc_acctivate(request,uidb64,token):
    form=get_user_model()
    subscribe_form=SubscriberForm()
    obj=SiteConstants.objects.count()
    if obj == 0:
        return redirect('/site/installation/')
    obj=SiteConstants.objects.all()[0]
    try:
        uid=urlsafe_base64_decode(uidb64)
        user=form.objects.get(pk=uid)
    except(TypeError,OverflowError,ValueError,User.DoesNotExist):
        user = None
    if user is not None and create_token.check_token(user, token):
        user.is_active = True
        user.save()
        message="Thank you for your email confirmation. Now you can login your account."
        data={'title':'Account | Activate','valid':True,'title':'Success','message':message,'subscribe_form':subscribe_form,'obj':obj}
        return render(request,'manager/account_activation_done.html',context=data)
    else:
        message="Activation link is invalid !"
        data={'title':'Account | Activate','valid':True,'title':'Success','message':message,'subscribe_form':subscribe_form,'obj':obj}
        return render(request,'manager/account_activation_done.html',context=data)


#profile view
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
class Profile(View):
    def get(self,request,username):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        subscribe_form=SubscriberForm()
        uform=CurrentUserProfileChangeForm(instance=request.user)
        eform=CurrentExtUserProfileChangeForm(instance=request.user.extendedauthuser)
        passform=UserPasswordChangeForm()
        socialform=UserSocialForm(instance=request.user.extendedauthuser)
        profileform=ProfilePicForm()
        data={'title':username,'obj':obj,'subscribe_form':subscribe_form,'uform':uform,'eform':eform,'passform':passform,'socialform':socialform,'profileform':profileform}
        return render(request,'manager/profile.html',context=data)
    def post(self,request,username,*args ,**kwargs):
        uform=CurrentUserProfileChangeForm(request.POST or None,instance=request.user)
        eform=CurrentExtUserProfileChangeForm(request.POST,request.FILES or None,instance=request.user.extendedauthuser)
        if uform.has_changed() or eform.has_changed():
            if uform.is_valid() and eform.is_valid():
                uform.save()
                eform.save()
                return JsonResponse({'valid':True,'message':'Profile updated.'},content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':uform.errors,'eform_errors':eform.errors,},content_type='application/json')
        return JsonResponse({'valid':False,'error':'No changes made'},content_type='application/json')


#passwordChange
@login_required(login_url='/accounts/login')
def passwordChange(request):
    if request.method=='POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        passform=UserPasswordChangeForm(request.POST or None,instance=request.user)
        if passform.is_valid():
            user=User.objects.get(username__exact=request.user.username)
            user.password=make_password(passform.cleaned_data.get('password1'))
            user.save()
            update_session_auth_hash(request,request.user)
            return JsonResponse({'valid':True,'message':'Password changed successfully.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':passform.errors},content_type='application/json')


#social
@login_required(login_url='/accounts/login')
def edit_social_link(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        socialform=UserSocialForm(request.POST or None , instance=request.user.extendedauthuser)
        if socialform.has_changed():
            if socialform.is_valid():
                userme=socialform.save(commit=False)
                userme.user=request.user
                userme.save()
                return JsonResponse({'valid':True,'message':'Social link(s) updated.'},status=200,safe=False)
            else:
                return JsonResponse({'valid':False,'uform_errors':socialform.errors},status=200)    
        return JsonResponse({'valid':False,'error':'No changes made'},content_type='application/json')


#profilePic
@login_required(login_url='/accounts/login')
def profilePic(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        profilePicform=ProfilePicForm(request.POST , request.FILES or None , instance=request.user.extendedauthuser)
        if profilePicform.has_changed():
            if profilePicform.is_valid():
                userme=profilePicform.save(commit=False)
                userme.user=request.user
                userme.save()
                return JsonResponse({'valid':True,'message':'Profile picture updated.'},status=200,safe=False)
            else:
                return JsonResponse({'valid':False,'uform_errors':profilePicform.errors},status=200)    
        return JsonResponse({'valid':False,'error':'No changes made'},content_type='application/json')

#users
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def users(request):
    obj=SiteConstants.objects.count()
    if obj == 0:
        return redirect('/site/installation/')
    obj=SiteConstants.objects.all()[0]
    data=User.objects.all().order_by("-id")
    paginator=Paginator(data,20)
    page_num=request.GET.get('page')
    users=paginator.get_page(page_num)    
    data={
            'title':'view all users',
            'obj':obj,
            'count':paginator.count,
            'data':request.user,
            'users':users,
        }
    return render(request,'manager/users.html',context=data)


#AddUser
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class AddUser(View):
    def get(self,request):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        uform=UserReg()
        eform=EProfileForm()        
        data={
            'title':'Add New User',
            'obj':obj,
            'data':request.user,
            'uform':uform,
            'eform':eform,
        }
        return render(request,'manager/add_users.html',context=data)
    def post(self,request):
        uform=UserReg(request.POST or None)
        eform=EProfileForm(request.POST or None)
        if uform.is_valid() and  eform.is_valid():
            userme=uform.save(commit=False)
            userme.is_active = True
            userme.save()
            extended=eform.save(commit=False)
            extended.user=userme
            extended.is_client=True
            extended.role='Client'
            extended.initials=uform.cleaned_data.get('first_name')[0].upper()+uform.cleaned_data.get('last_name')[0].upper()
            extended.save()
            return JsonResponse({'valid':True,'message':'Registered successfully','register':False},content_type="application/json")
        else:
            return JsonResponse({'valid':False,'uform_errors':uform.errors,'eform_errors':eform.errors},content_type="application/json")


@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class EditUser(View):
    def get(self,request,id):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        try:
            user=User.objects.get(id__exact=id)
            uform=CurrentUserProfileChangeForm(instance=user)
            eform=CurrentExtUserProfileChangeForm(instance=user.extendedauthuser)        
            data={
                'title':f'Edit {user.get_full_name}',
                'obj':obj,
                'data':request.user,
                'uform':uform,
                'eform':eform,
                'user':user,
                'edit':True,
            }
            return render(request,'manager/add_users.html',context=data)
        except User.DoesNotExist:
            data={
                'title':'Error | Page Not Found',
                'obj':obj
             }
            return render(request,'manager/404.html',context=data,status=404)
       
    def post(self,request,id):
        user=User.objects.get(id__exact=id)
        uform=CurrentUserProfileChangeForm(request.POST or None,instance=user)
        eform=CurrentExtUserProfileChangeForm(request.POST or None,instance=user.extendedauthuser)
        if uform.is_valid() and  eform.is_valid():
            userme=uform.save(commit=False)
            userme.save()
            extended=eform.save(commit=False)
            extended.user=userme
            extended.initials=uform.cleaned_data.get('first_name')[0].upper()+uform.cleaned_data.get('last_name')[0].upper()
            extended.save()
            return JsonResponse({'valid':True,'message':'User updated successfully'},content_type="application/json")
        else:
            return JsonResponse({'valid':False,'uform_errors':uform.errors,'eform_errors':eform.errors},content_type="application/json")


#deleteUser
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteUser(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=User.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'User deleted successfully.','id':id},content_type='application/json')       
        except User.DoesNotExist:
            return JsonResponse({'valid':False,'message':'User does not exist'},content_type='application/json')


#EditSite
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class EditSite(View):
    def get(self,request):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        form1=SiteForm(instance=obj)
        form2=AddressConfigForm(instance=obj)
        form3=UserSocialForm(instance=obj)
        form4=WorkingConfigForm(instance=obj)
        data={
            'title':'Edit Site Settings',
            'obj':obj,
            'data':request.user,
            'form1':form1,
            'form2':form2,
            'form3':form3,
            'form4':form4,
        }
        return render(request,'manager/site.html',context=data)
    def post(self,request,*args , **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            instance_data=SiteConstants.objects.all().first()
            form=SiteForm(request.POST,request.FILES or None , instance=instance_data)
            if form.is_valid():
                form.save()
                return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')



#siteContact
@login_required(login_url='accounts/login')
@allowed_users(allowed_roles=['admins'])
def siteContact(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        instance_data=SiteConstants.objects.all().first()
        form=AddressConfigForm(request.POST or None , instance=instance_data)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')

#siteWorking
@login_required(login_url='accounts/login')
@allowed_users(allowed_roles=['admins'])
def siteWorking(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        instance_data=SiteConstants.objects.all().first()
        form=WorkingConfigForm(request.POST, request.FILES or None , instance=instance_data)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')


#siteSocial
@login_required(login_url='accounts/login')
@allowed_users(allowed_roles=['admins'])
def siteSocial(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        instance_data=SiteConstants.objects.all().first()
        form=UserSocialForm(request.POST or None , instance=instance_data)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')

#chats
@login_required(login_url='accounts/login')
def chats(request):
    obj=SiteConstants.objects.count()
    if obj == 0:
        return redirect('/site/installation/')
    obj=SiteConstants.objects.all()[0]
    data={
        'title':'View all chats',
        'obj':obj,
        'data':request.user,
    }
    return render(request,'manager/chats.html',context=data)

#projects
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def projects(request):
    obj=SiteConstants.objects.count()
    if obj == 0:
        return redirect('/site/installation/')
    obj=SiteConstants.objects.all()[0]
    data=Project.objects.all().order_by("-id")
    paginator=Paginator(data,20)
    page_num=request.GET.get('page')
    projects=paginator.get_page(page_num)    
    data={
            'title':'view all projects',
            'obj':obj,
            'count':paginator.count,
            'data':request.user,
            'projects':projects,
        }
    return render(request,'manager/projects.html',context=data)

#blogs
def blogs(request):
    obj=SiteConstants.objects.count()
    if obj == 0:
        return redirect('/site/installation/')
    obj=SiteConstants.objects.all()[0]
    data=Project.objects.all().order_by("-id")
    paginator=Paginator(data,20)
    page_num=request.GET.get('page')
    users=paginator.get_page(page_num)    
    data={
            'title':'Blogs',
            'obj':obj,
            'count':paginator.count,
            'data':request.user,
            'projects':projects,
        }
    return render(request,'manager/blogs.html',context=data)

#blogsDetails
class blogsDetails(View):
    def get(self,request):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        data={
            'title':'Blogs Details',
            'obj':obj,
            'data':request.user,
        }
        return render(request,'manager/blog_details.html',context=data)

#designs
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def designs(request):
    obj=SiteConstants.objects.count()
    if obj == 0:
        return redirect('/site/installation/')
    obj=SiteConstants.objects.all()[0]
    data=DesignModel.objects.all().order_by("-id")
    paginator=Paginator(data,20)
    page_num=request.GET.get('page')
    designs=paginator.get_page(page_num)    
    data={
            'title':'Designs and Clients',
            'obj':obj,
            'count':paginator.count,
            'data':request.user,
            'designs':designs,
        }
    return render(request,'manager/designs.html',context=data)

#AddSkill
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class AddSkill(View):
    def get(self,request):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        form=SkillsForm()
        data={
            'title':'Add Skill',
            'obj':obj,
            'data':request.user,
            'form':form,
        }
        return render(request,'manager/add_skill.html',context=data)
    def post(self,request,*args , **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form=SkillsForm(request.POST or None)
            if form.is_valid():
                user=form.save(commit=False)
                user.user_id=request.user.pk
                user.save()
                return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')

#EditSkill
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class EditSkill(View):
    def get(self,request,id):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        try:
            user=DesignModel.objects.get(id__exact=id)
            form=SkillsForm(instance=user)
            data={
                'title':f'Edit skill | {user.name}',
                'obj':obj,
                'data':request.user,
                'form':form,
                'user':user,
                'edit':True,
            }
            return render(request,'manager/add_skill.html',context=data)
        except DesignModel.DoesNotExist:
            data={
                'title':'Error | Page Not Found',
                'obj':obj
             }
            return render(request,'manager/404.html',context=data,status=404)
    def post(self,request,id,*args , **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            user=DesignModel.objects.get(id__exact=id)
            form=SkillsForm(request.POST or None,instance=user)
            if form.is_valid():
                form.save()
                return JsonResponse({'valid':True,'message':'data updated successfully'},status=200,content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')


#deleteSkill
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteSkill(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=DesignModel.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Skill deleted successfully.','id':id},content_type='application/json')       
        except DesignModel.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Skill does not exist'},content_type='application/json')

#reviews
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def reviews(request):
    obj=SiteConstants.objects.count()
    if obj == 0:
        return redirect('/site/installation/')
    obj=SiteConstants.objects.all()[0]
    data=ReviewModel.objects.all().order_by("-id")
    paginator=Paginator(data,20)
    page_num=request.GET.get('page')
    reviews=paginator.get_page(page_num)    
    data={
            'title':'Site Reviews',
            'obj':obj,
            'count':paginator.count,
            'data':request.user,
            'reviews':reviews,
        }
    return render(request,'manager/reviews.html',context=data)

#AddReview
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class AddReview(View):
    def get(self,request):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        form=ReviewForm()
        data={
            'title':'Add Review',
            'obj':obj,
            'data':request.user,
            'form':form,
        }
        return render(request,'manager/add_review.html',context=data)
    def post(self,request,*args , **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form=ReviewForm(request.POST or None)
            if form.is_valid():
                user=form.save(commit=False)
                user.user_id=request.user.pk
                user.name=request.user.get_full_name()
                user.profile_pic=request.user.extendedauthuser.profile_pic.url
                user.save()
                return JsonResponse({'valid':True,'message':'Review posted successfully'},status=200,content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')

#EditReview
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class EditReview(View):
    def get(self,request,id):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        try:
            user=ReviewModel.objects.get(id__exact=id)
            form=ReviewForm(instance=user)
            data={
                'title':f'Edit Review | {user.name}',
                'obj':obj,
                'data':request.user,
                'form':form,
                'user':user,
                'edit':True,
            }
            return render(request,'manager/add_review.html',context=data)
        except DesignModel.DoesNotExist:
            data={
                'title':'Error | Page Not Found',
                'obj':obj
             }
            return render(request,'manager/404.html',context=data,status=404)
    def post(self,request,id,*args , **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            user=ReviewModel.objects.get(id__exact=id)
            form=ReviewForm(request.POST or None,instance=user)
            if form.is_valid():
                form.save()
                return JsonResponse({'valid':True,'message':'data updated successfully'},status=200,content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')


#deleteReview
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteReview(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=ReviewModel.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Review deleted successfully.','id':id},content_type='application/json')       
        except ReviewModel.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Review does not exist'},content_type='application/json')


#AddProject
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class AddProject(View):
    def get(self,request):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        form=Projectorm()
        data={
            'title':'Add Project',
            'obj':obj,
            'data':request.user,
            'form':form,
        }
        return render(request,'manager/add_project.html',context=data)
    def post(self,request,*args , **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form=Projectorm(request.POST,request.FILES or None)
            if form.is_valid():
                user=form.save(commit=False)
                user.user_id=request.user.pk
                user.save()
                return JsonResponse({'valid':True,'message':'Project posted successfully'},status=200,content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')


#EditProject
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class EditProject(View):
    def get(self,request,id):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/site/installation/')
        obj=SiteConstants.objects.all()[0]
        try:
            user=Project.objects.get(id__exact=id)
            form=Projectorm(instance=user)
            data={
                'title':f'Edit Project | {user.title}',
                'obj':obj,
                'data':request.user,
                'form':form,
                'user':user,
                'edit':True,
            }
            return render(request,'manager/add_project.html',context=data)
        except Project.DoesNotExist:
            data={
                'title':'Error | Page Not Found',
                'obj':obj
             }
            return render(request,'manager/404.html',context=data,status=404)
    def post(self,request,id,*args , **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            user=Project.objects.get(id__exact=id)
            form=Projectorm(request.POST,request.FILES or None,instance=user)
            if form.is_valid():
                form.save()
                return JsonResponse({'valid':True,'message':'data updated successfully'},status=200,content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')


#deleteProject
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteProject(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=Project.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Project deleted successfully.','id':id},content_type='application/json')       
        except Project.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Project does not exist'},content_type='application/json')