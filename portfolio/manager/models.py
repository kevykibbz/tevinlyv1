from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from manager.addons import send_email
import random
from .tokens import create_token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import jsonfield
from installation.models import SiteConstants
from django.utils.crypto import get_random_string
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Max
from django.utils.translation import gettext_lazy as _
import environ
env=environ.Env()
environ.Env.read_env()

def bgcolor():
    hex_digits=['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    digit_array=[]
    for i in range(6):
        digits=hex_digits[random.randint(0,15)]
        digit_array.append(digits)
    joined_digits=''.join(digit_array)
    color='#'+joined_digits
    return color
       
#generate random
def generate_id():
    return get_random_string(6,'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKMNOPQRSTUVWXYZ0123456789')


#generate random
def generate_serial():
    return get_random_string(12,'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKMNOPQRSTUVWXYZ0123456789')

class ExtendedAdmin(models.Model):
    user=models.OneToOneField(User,primary_key=True,on_delete=models.CASCADE)
    location=models.CharField(null=True,blank=True,max_length=100)
    main=models.BooleanField(default=False)
    is_installed=models.BooleanField(default=False)

    class Meta:
        db_table='extended_admin'
        verbose_name_plural='extended_admins'

    def __str__(self):
        return f'{self.user.username} site extended admin'




@receiver(post_save, sender=ExtendedAdmin)
def send_installation_email(sender, instance, created, **kwargs):
    if created:
        if instance.is_installed:
            #site is installed
            subject='Congragulations:Site installed successfully.'
            email=instance.user.email
            message={
                        'user':instance.user,
                        'site_name':instance.user.siteconstants.site_name,
                        'site_url':instance.user.siteconstants.site_url
                    }
            template='emails/installation.html'
            send_email(subject,email,message,template)




class SubscribersModel(models.Model):
    email=models.CharField(max_length=50,verbose_name='email address',unique=True,null=True)
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

@receiver(post_save, sender=SubscribersModel)
def send_notification_email(sender, instance, created, **kwargs):
    if created:
        obj=SiteConstants.objects.all().first()
        subject='Thank you for subscribing.'
        email=instance.email
        message={
                    'site_name':obj.site_name,
                    'site_url':obj.site_url
                }
        template='emails/subscription.html'
        send_email(subject,email,message,template)#






options=[
            ('employee','Employee'),
            ('admins','Admin'),
        ]
class ExtendedAuthUser(models.Model):
    user=models.OneToOneField(User,primary_key=True,on_delete=models.CASCADE)
    phone=PhoneNumberField(null=True,blank=True,verbose_name='phone',unique=True,max_length=13)
    initials=models.CharField(max_length=10,blank=True,null=True)
    is_client=models.BooleanField(default=False,blank=True,null=True)
    serial_no=models.CharField(max_length=100,default=get_random_string,null=True,blank=True)
    bgcolor=models.CharField(max_length=10,blank=True,null=True,default=bgcolor)
    followers=models.IntegerField(default=0,blank=True,null=True)
    following=models.IntegerField(default=0,blank=True,null=True)
    upvotes=models.IntegerField(default=0,blank=True,null=True)
    downvotes=models.IntegerField(default=0,blank=True,null=True)
    articles=models.IntegerField(default=10,blank=True,null=True)
    company=models.CharField(max_length=100,null=True,blank=True,default=env('SITE_NAME'))
    profile_pic=models.ImageField(upload_to='profiles/',null=True,blank=True,default="profiles/placeholder.jpg")
    role=models.CharField(choices=options,max_length=200,null=True,blank=True)
    bio=models.TextField(null=True,blank=True,default='something about you...')
    nickname=models.CharField(max_length=100,null=True,blank=True,default='Your nickname')
    facebook=models.URLField(max_length=200,null=True,blank=True,default='https://facebook.com/username')
    twitter=models.URLField(max_length=200,null=True,blank=True,default='https://twitter.com/username')
    instagram=models.URLField(max_length=200,null=True,blank=True,default='https://instagram.com/username')
    github=models.URLField(max_length=200,null=True,blank=True,default='https://github.com/username')
    bio=models.TextField(null=True,blank=True,default='something about you...')
    company=models.CharField(max_length=100,null=True,blank=True,default=env('SITE_NAME'))
    shipping_address=models.TextField(null=True,blank=True)
    gender=models.CharField(choices=[('Male','Male'),('Female','Female'),('Other','Other')],max_length=6,null=True,blank=True)
    birthday=models.DateField(null=True,blank=True)
    created_on=models.DateTimeField(default=now)
    class Meta:
        db_table='extended_auth_user'
        verbose_name_plural='extended_auth_users'
    def __str__(self)->str:
        return f'{self.user.username} extended auth profile'



@receiver(post_save, sender=ExtendedAuthUser)
def send_success_email(sender, instance, created, **kwargs):
    if created and instance.is_client:
        #site is installed
        subject='Congragulations:Registration Successfully.'
        email=instance.user.email
        obj=SiteConstants.objects.all()[0]
        message={
                    'user':instance.user,
                    'email':instance.user.email,
                    'address':obj.address,
                    'loation':obj.location,
                    'phone':obj.phone,
                    'uid':urlsafe_base64_encode(force_bytes(instance.user.id)),
                    'token':create_token.make_token(instance.user),
                    'site_logo':obj.favicon,
                    'site_name':obj.site_name,
                    'site_url':obj.site_url
                }
        template='emails/success.html'
        send_email(subject,email,message,template)

class ContactModel(models.Model):
    name=models.CharField(max_length=50,verbose_name='name',null=True)
    email=models.CharField(max_length=50,verbose_name='email address',null=True)
    phone=PhoneNumberField(null=True,blank=True,verbose_name='phone',unique=True,max_length=13)
    subject=models.CharField(max_length=50,verbose_name='subject',null=True)
    message=models.TextField(null=True)
    date=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
@receiver(post_save, sender=ContactModel)
def send_notification_email(sender, instance, created, **kwargs):
    if created:
        obj=SiteConstants.objects.all().first()
        subject='Thank you for contacting us.'
        email=instance.email
        message={
                    'user':instance.name,
                    'site_name':obj.site_name,
                    'site_url':obj.site_url
                }
        template='emails/contact_us.html'
        send_email(subject,email,message,template)

class Project(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=50,verbose_name='title',null=True,blank=True)
    link=models.CharField(max_length=50,verbose_name='link',null=True,blank=True)
    caption=models.CharField(max_length=50,verbose_name='caption',null=True,blank=True)
    project_id=models.CharField(max_length=50,verbose_name='project id',default=generate_id)
    likes=models.IntegerField(verbose_name='likes',null=True,blank=True)
    views=models.IntegerField(verbose_name='views',null=True,blank=True)
    comments=models.IntegerField(verbose_name='comments',null=True,blank=True)
    replies=models.IntegerField(verbose_name='replies',null=True,blank=True)
    upvote=models.IntegerField(verbose_name='upvote',null=True,blank=True)
    downvote=models.IntegerField(verbose_name='downvote',null=True,blank=True)
    tags=models.CharField(max_length=250,verbose_name='tags',null=True,blank=True)
    category=models.CharField(max_length=100,verbose_name='tag',null=True,blank=True)
    description=models.TextField(verbose_name='description',null=True,blank=True)
    thumbnail=models.ImageField(upload_to='gallary/',null=True,blank=True)
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self)->str:
        return f'{self.user.username} project'

class ExtendedProject(models.Model):
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    images=models.ImageField(upload_to='gallary/',null=True,blank=True)
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self)->str:
        return f'{self.user.title} project gallary'

class ProjectComments(models.Model):
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    comment=models.TextField(null=True,blank=True)
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self)->str:
        return f'{self.user.title} project comment'

class ProjectReplies(models.Model):
    comment=models.ForeignKey(ProjectComments,on_delete=models.CASCADE)
    reply=models.TextField(null=True,blank=True)
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self)->str:
        return f'{self.user.title} project reply'


class DesignModel(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    category=models.CharField(max_length=100,blank=True,null=True)
    name=models.CharField(max_length=100,default=False,blank=True,null=True)
    progress=models.IntegerField(default=0,blank=True,null=True)
    created_on=models.DateTimeField(default=now)
    class Meta:
        db_table='design_tbl'
        verbose_name_plural='design_tbl'
    def __str__(self)->str:
        return f'{self.user.username} skills set'

class ReviewModel(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=100,default=False,blank=True,null=True)
    message=models.TextField(blank=True,null=True)
    profile_pic=models.CharField(max_length=100,default=False,blank=True,null=True)
    created_on=models.DateTimeField(default=now)
    class Meta:
        db_table='review_tbl'
        verbose_name_plural='review_tbl'
    def __str__(self)->str:
        return f'{self.user.username} review'