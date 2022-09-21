from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import *
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm,UserChangeForm,PasswordChangeForm
from django.contrib.auth.forms import User
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.contrib.auth.hashers import check_password
from django.core.validators import FileExtensionValidator,URLValidator
from installation.forms import SiteConstants
from django.contrib.auth import authenticate
import re
from urllib.parse import urlparse


#subscriber form
class SubscriberForm(forms.ModelForm):
    email=forms.EmailField(widget=forms.EmailInput(attrs={'aria-label':'email','class':'form-control','placeholder':'Enter email address'}),error_messages={'required':'Email address is required'})
    class Meta:
        model=SubscribersModel
        fields=['email']
        
    def clean_email(self):
        email=self.cleaned_data['email']
        if SubscribersModel.objects.filter(email=email).exists():
            raise forms.ValidationError('you have already been subscribed')
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('invalid email address')
        return email


#contact form
class ContactForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'name','class':'form-control','placeholder':'Enter name'}),error_messages={'required':'Name is required'})
    email=forms.EmailField(widget=forms.EmailInput(attrs={'aria-label':'email','class':'form-control','placeholder':'Enter email address'}),error_messages={'required':'Email address is required'})
    subject=forms.CharField(min_length=5,widget=forms.TextInput(attrs={'aria-label':'subject','class':'form-control','placeholder':'Enter subject'}),error_messages={'required':'Subject is required','min_length':'enter atleast 5 characters long subject'})
    message=forms.CharField(min_length=10,widget=forms.Textarea(attrs={'aria-label':'message','class':'form-control','placeholder':'Enter message','rows':6}),error_messages={'required':'Message is required','min_lenghth':'enter atleast 10 characters long message'})
    class Meta:
        model=ContactModel
        fields=['name','email','subject','message']
        
    def clean_name(self):
        name=self.cleaned_data['name']
        try:
             re.match('^[a-zA-Z]+$',name)
        except ValidationError as e:
            raise forms.ValidationError('only characters are allowed')
        return name
    
    def clean_email(self):
        email=self.cleaned_data['email']
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('invalid email address')
        return email


    def clean_message(self):
        subject=self.cleaned_data['subject']
        message=self.cleaned_data['message']
        if ContactModel.objects.filter(subject=subject,message=message).exists():
            raise forms.ValidationError('message found please say something else')
        return message
#user login form
class UserSignIn(UserCreationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'username','class':'form-control','placeholder':'Enter username/Email address'}),error_messages={'required':'Username is required'})
    password1=forms.CharField(min_length=5,widget=forms.PasswordInput(attrs={'aria-label':'password1','class':'form-control','placeholder':'Enter password'}),error_messages={'required':'Password is required','min_length':'enter atleast 6 characters long'})
    class Meta:
        model=User
        fields=['username','password1']

#user register form
class UserReg(UserCreationForm):
    first_name=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'first_name','class':'form-control fg-theme','placeholder':'Enter first name'}),error_messages={'required':'First name is required'})
    last_name=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'last_name','class':'form-control','placeholder':'Enter last name'}),error_messages={'required':'Last name is required'})
    email=forms.EmailField(widget=forms.EmailInput(attrs={'aria-label':'email','class':'form-control','placeholder':'Enter email address'}),error_messages={'required':'Email address is required'})
    username=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'username','class':'form-control','placeholder':'Enter username'}),error_messages={'required':'Username is required'})
    password1=forms.CharField(min_length=6,widget=forms.PasswordInput(attrs={'aria-label':'password1','class':'form-control','placeholder':'Enter password'}),error_messages={'required':'Password is required','min_length':'enter atleast 6 characters long'})
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'aria-label':'password2','class':'form-control','placeholder':'Enter confirm password'}),error_messages={'required':'Confirm password is required'})
    class Meta:
        model=User
        fields=['first_name','last_name','username','email','password1','password2']

    def clean_first_name(self):
        first_name=self.cleaned_data['first_name']
        if not str(first_name).isalpha():
            raise forms.ValidationError('only characters are required')
        return first_name
    def clean_last_name(self):
        last_name=self.cleaned_data['last_name']
        if not str(last_name).isalpha():
            raise forms.ValidationError('only characters are required')
        return last_name

    def clean_email(self):
        email=self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with that email already exist')
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('Invalid email address')
        return email


class EProfileForm(forms.ModelForm):
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'class':'form-control input-rounded','type':'tel','aria-label':'phone','placeholder':'Phone'}),error_messages={'required':'Phone number is required'})
    profile_pic=forms.ImageField(
                                widget=forms.FileInput(attrs={'class':'profile','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=ExtendedAuthUser
        fields=['phone','profile_pic']

    
    def clean_phone(self):
        phone=self.cleaned_data['phone']
        if phone !='':
            if ExtendedAuthUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('A user with this phone number already exists.')
            else:
                return phone
        else:
            raise forms.ValidationError('Phone number is required')

class User_resetPassword(PasswordResetForm):
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter email address'}),error_messages={'required':'Email address is required'})
    def clean_email(self):
        email=self.cleaned_data['email']
        if  not User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address does not exist')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError('Invalid email address')
        return email

#profileForm
class CurrentUserProfileChangeForm(UserChangeForm):
    first_name=forms.CharField(widget=forms.TextInput(attrs={'style':'text-transform:lowercase;','class':'form-control input-rounded'}),required=False)
    last_name=forms.CharField(widget=forms.TextInput(attrs={'style':'text-transform:lowercase;','class':'form-control input-rounded','aria-label':'last_name'}),error_messages={'required':'Last name is required'})
    email=forms.EmailField(widget=forms.EmailInput(attrs={'style':'text-transform:lowercase;','class':'form-control input-rounded','aria-label':'email'}),error_messages={'required':'Email address is required'})
    username=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'username','class':'form-control','placeholder':'Enter username'}),error_messages={'required':'Username is required'})
    is_active=forms.BooleanField(widget=forms.CheckboxInput(attrs={'aria-label':'is_active','id':'checkbox1'}),required=False)
    class Meta:
        model=User
        fields=['first_name','last_name','email','is_active','username',]


    def clean_first_name(self):
        first_name=self.cleaned_data['first_name']
        if not str(first_name).isalpha():
                raise forms.ValidationError('only characters are allowed.')
        return first_name
    
    def clean_last_name(self):
        last_name=self.cleaned_data['last_name']
        if not str(last_name).isalpha():
                raise forms.ValidationError('only characters are allowed.')
        return last_name

    def clean_email(self):
        email=self.cleaned_data['email']
        if email != self.instance.email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('A user with this email already exists.')
            try:
                validate_email(email)
            except ValidationError as e:
                raise forms.ValidationError('Invalid email address.')
            return email
        else:
           return email

    def clean_username(self):
        username=self.cleaned_data['username']
        if username != self.instance.username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('A user with this username already exists.')
        else:
           return username

options=[
            ('---Select gender---',
                    (
                        ('Male','Male'),
                        ('Female','Female'),
                        ('Other','Other'),
                    )
            ),
        ]
#profileForm
class CurrentExtUserProfileChangeForm(forms.ModelForm):
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'class':'form-control input-rounded ','type':'tel','aria-label':'phone','placeholder':'Phone example +25479626...'}),error_messages={'required':'Phone number is required'})
    bio=forms.CharField(widget=forms.Textarea(attrs={'style':'text-transform:lowercase;','class':'form-control','aria-label':'email'}),required=False)
    nickname=forms.CharField(widget=forms.TextInput(attrs={'style':'text-transform:lowercase;','class':'form-control input-rounded','aria-label':'nickname'}),error_messages={'required':'Nickname is required'})
    gender=forms.ChoiceField(choices=options, error_messages={'required':'Gender is required','aria-label':'gender'},widget=forms.Select(attrs={'class':'form-control show-tick ms select2','placeholder':'Gender'}))
    birthday=forms.DateField(widget=forms.DateInput(attrs={'style':'text-transform:lowercase;','class':'form-control','aria-label':'birthday','type':'date'}),error_messages={'required':'Birthday is required'})
    profile_pic=forms.ImageField(
                                widget=forms.FileInput(attrs={'class':'profile','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=ExtendedAuthUser
        fields=['phone','profile_pic','bio','gender','birthday','nickname',]

    
    def clean_phone(self):
        phone=self.cleaned_data['phone']
        if phone != self.instance.phone:
            if ExtendedAuthUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('A user with this phone number already exists.')
            else:
                return phone
        else:
           return phone 

class UserPasswordChangeForm(UserCreationForm):
    oldpassword=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Old password','aria-label':'oldpassword'}),error_messages={'required':'Old password is required','min_length':'enter atleast 6 characters long'})
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'New password Eg Example12','aria-label':'password1'}),error_messages={'required':'New password is required','min_length':'enter atleast 6 characters long'})
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm new password','aria-label':'password2'}),error_messages={'required':'Confirm new password is required'})

    class Meta:
        model=User
        fields=['password1','password2']
    
    def clean_oldpassword(self):
        oldpassword=self.cleaned_data['oldpassword']
        if not self.instance.check_password(oldpassword):
            raise forms.ValidationError('Wrong old password.')
        else:
           return oldpassword 

#social form
class UserSocialForm(forms.ModelForm):
    facebook=forms.URLField(widget=forms.URLInput(attrs={'style':'text-transform:lowercase;','class':'form-control','aria-label':'facebook','placeholder':'Facebook profile link'}),required=False,validators=[URLValidator])    
    twitter=forms.URLField(widget=forms.URLInput(attrs={'style':'text-transform:lowercase;','class':'form-control','aria-label':'twitter','placeholder':'Twitter profile link'}),required=False,validators=[URLValidator])    
    github=forms.URLField(widget=forms.URLInput(attrs={'style':'text-transform:lowercase;','class':'form-control','aria-label':'github','placeholder':'Github profile link'}),required=False,validators=[URLValidator])  
    instagram=forms.URLField(widget=forms.URLInput(attrs={'style':'text-transform:lowercase;','class':'form-control','aria-label':'instagram','placeholder':'Instagram profile link'}),required=False,validators=[URLValidator])    
    class Meta:
        model=ExtendedAuthUser
        fields=['facebook','twitter','github','instagram',]
    def clean_facebook(self):
        facebook=self.cleaned_data['facebook']
        output=urlparse(facebook)
        username=output.path.strip('/')
        if not username:
            raise forms.ValidationError('Username parameter missing')
        else:
            return facebook
    
    def clean_twitter(self):
        twitter=self.cleaned_data['twitter']
        output=urlparse(twitter)
        username=output.path.strip('/')
        if not username:
            raise forms.ValidationError('Username parameter missing')
        else:
            return twitter
    

    def clean_github(self):
        github=self.cleaned_data['github']
        output=urlparse(github)
        username=output.path.strip('/')
        if not username:
            raise forms.ValidationError('Username parameter missing')
        else:
            return github

    def clean_instagram(self):
        instagram=self.cleaned_data['instagram']
        output=urlparse(instagram)
        username=output.path.strip('/')
        if not username:
            raise forms.ValidationError('Username parameter missing')
        else:
            return instagram

class ProfilePicForm(forms.ModelForm):
    profile_pic=forms.ImageField(
                                widget=forms.FileInput(attrs={'class':'profile','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=ExtendedAuthUser
        fields=['profile_pic',]

class SiteForm(forms.ModelForm):
    site_name=forms.CharField(widget=forms.EmailInput(attrs={'aria-label':'site_name','class':'form-control input-rounded','placeholder':'Site name'}),error_messages={'required':'Site Name is required'})
    clients=forms.CharField(widget=forms.NumberInput(attrs={'aria-label':'clients','class':'form-control input-rounded','placeholder':'clients'}),error_messages={'required':'Number of clients is required'})
    completed_projects=forms.CharField(widget=forms.NumberInput(attrs={'aria-label':'completed_projects','class':'form-control input-rounded','placeholder':'Completed projects'}),error_messages={'required':'Number of completed projects is required'})
    ongoing_projects=forms.CharField(widget=forms.NumberInput(attrs={'aria-label':'ongoing_projects','class':'form-control input-rounded','placeholder':'Ongoing projects'}),error_messages={'required':'Number of ongoing projects is required'})
    client_satisfactory=forms.CharField(widget=forms.NumberInput(attrs={'aria-label':'client_satisfactory','class':'form-control input-rounded','placeholder':'Client Satisfaction'}),error_messages={'required':'Number of client satisfaction is required'})
    description=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'description','class':'form-control','placeholder':'Site Description'}),error_messages={'required':'Site Description is required'})
    theme_color=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'theme_color','class':'form-control gradient-colorpicker input-rounded','placeholder':'Site Theme Color eg #ff0000'}),required=False)
    key_words=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'key_words','class':'form-control input-rounded tags','placeholder':'Site Keywords'}),required=False)
    site_url=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'site_url','class':'form-control input-rounded','placeholder':'Site URL'}),error_messages={'required':'Site URL is required'})
    favicon=forms.ImageField(
                                widget=forms.FileInput(attrs={'aria-label':'favicon','class':'custom-file-input','id':'customFileInput','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','ico'],message="Invalid image extension",code="invalid_extension")]
                                )
    cv=forms.FileField(
                                widget=forms.FileInput(attrs={'aria-label':'cv','class':'custom-file-input','id':'customFileInput1','accept':'application/pdf','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['pdf',],message="Invalid file extension",code="invalid_extension")]
                                )
    class Meta:
        model=SiteConstants
        fields=['clients','completed_projects','ongoing_projects','client_satisfactory','site_name','theme_color','site_url','description','key_words','favicon',]
    
    def clean_theme_color(self):
        theme_color=self.cleaned_data['theme_color']
        match=re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$',theme_color)
        if not match:
            raise forms.ValidationError('Invalid color code given')
        else:
            return theme_color
            
    def clean_site_url(self):
        site_url=self.cleaned_data['site_url']
        if URLValidator(site_url):
            return site_url
        else:
            raise forms.ValidationError('Invalid url')

#AddressConfigForm
class AddressConfigForm(forms.ModelForm):
    site_email=forms.EmailField(widget=forms.EmailInput(attrs={'aria-label':'site_email','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Site Email Address'}),error_messages={'required':'Address is required'})
    site_email2=forms.EmailField(widget=forms.EmailInput(attrs={'aria-label':'site_email2','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Site Additional Email Address'}),required=False)
    address=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'address','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Address is required'})
    location=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'location','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Location is required'})
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'aria-label':'phone','style':'text-transform:lowercase;','class':'form-control input-rounded'},initial='KE'),required=False)
    class Meta:
        model=SiteConstants
        fields=['address','location','phone','site_email','site_email2']
    

#social form
class UserSocialForm(forms.ModelForm):
    facebook=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'facebook','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Facebook Link'}),required=False)    
    twitter=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'twitter','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Twitter Link'}),required=False)    
    github=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'github','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Github Link'}),required=False)  
    instagram=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'instagram','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Instagram Link'}),required=False)    
    linkedin=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'linkedin','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Linkedin Link'}),required=False)   
    youtube=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'youtube','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Youtube Link'}),required=False)    
    whatsapp=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'whatsapp','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Whats App'}),required=False)
    class Meta:
        model=SiteConstants
        fields=['facebook','twitter','linkedin','instagram','whatsapp','youtube','github',]

    def clean_facebook(self):
        facebook=self.cleaned_data['facebook']
        if URLValidator(facebook):
                output=urlparse(facebook)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [facebook,username]
        else:
            raise forms.ValidationError('Invalid url')
    
    def clean_twitter(self):
        twitter=self.cleaned_data['twitter']
        if URLValidator(twitter):
                output=urlparse(twitter)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [twitter,username]
        else:
            raise forms.ValidationError('Invalid url')
    

    def clean_github(self):
        github=self.cleaned_data['github']
        if URLValidator(github):
                output=urlparse(github)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [github,username]
        else:
            raise forms.ValidationError('Invalid url')
    def clean_instagram(self):
        instagram=self.cleaned_data['instagram']
        if URLValidator(instagram):
                output=urlparse(instagram)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [instagram,username]
        else:
            raise forms.ValidationError('Invalid url')
    
    def clean_linkedin(self):
        linkedin=self.cleaned_data['linkedin']
        if URLValidator(linkedin):
                output=urlparse(linkedin)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [linkedin,username]
        else:
            raise forms.ValidationError('Invalid url')
    
    def clean_youtube(self):
        youtube=self.cleaned_data['youtube']
        if URLValidator(youtube):
                output=urlparse(youtube)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Channel id parameter missing')
                else:
                    return [youtube,username]
        else:
            raise forms.ValidationError('Invalid url')
    def clean_whatsapp(self):
        whatsapp=self.cleaned_data['whatsapp']
        if URLValidator(whatsapp):
            output=urlparse(whatsapp)
            username=output.path.strip('/')
            if not username:
                raise forms.ValidationError('username parameter missing')
            else:
                return [whatsapp,username]
        else:
            raise forms.ValidationError('Invalid url')

#WorkingConfigForm
class WorkingConfigForm(forms.ModelForm):
    working_days=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'working_days','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Working days is required'})
    working_hours=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'working_hours','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Working hours is required'})

    class Meta:
        model=SiteConstants
        fields=['working_days','working_hours',]


#AddressConfigForm
class SkillsForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'name','class':'form-control input-rounded','placeholder':'Skill name'}),error_messages={'required':'Skill name is required'})
    progress=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'progress','class':'form-control input-rounded','placeholder':'Percentage progress'}),error_messages={'required':'Percentage progress is required'})
    category=forms.ChoiceField(choices=[('Coding skills','Coding skills'),('Design Skills','Design Skills')],widget=forms.Select(attrs={'aria-label':'category','class':'form-control input-rounded','placeholder':'Skill category'}),error_messages={'required':'Skill category is required'})
    class Meta:
        model=DesignModel
        fields=['name','category','progress',]

    def clean_name(self):
        name=self.cleaned_data['name']
        if self.instance.name:
            if name != self.instance.name:
                if DesignModel.objects.filter(name=name).exists():
                    raise forms.ValidationError('Skill name already exists.')
            else:
               return name
        else:
            if DesignModel.objects.filter(name=name).exists():
                raise forms.ValidationError('Skill name already exist')
            return name

class ReviewForm(forms.ModelForm):
    message=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'message','class':'form-control input-rounded','placeholder':'Enter review here'}),error_messages={'required':'Review is required'})
    class Meta:
        model=ReviewModel
        fields=['message',]

class Projectorm(forms.ModelForm):
    title=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'title','class':'form-control input-rounded','placeholder':'Project title'}),error_messages={'required':'Project title is required'})
    link=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'link','class':'form-control input-rounded','placeholder':'Project link'}),error_messages={'required':'Percentage link is required'})
    caption=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'caption','class':'form-control input-rounded','placeholder':'Caption'}),error_messages={'required':'Project caption is required'})
    category=forms.ChoiceField(choices=[('template','Template'),('ui-ux','UI/UX'),('graphic','Graphic')],widget=forms.Select(attrs={'aria-label':'category','class':'form-control input-rounded','placeholder':'Skill category'}),error_messages={'required':'Skill category is required'})
    thumbnail=forms.ImageField(
                                widget=forms.FileInput(attrs={'aria-label':'favicon','class':'custom-file-input','id':'customFileInput','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png',],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=Project
        fields=['title','category','link','thumbnail','caption',]