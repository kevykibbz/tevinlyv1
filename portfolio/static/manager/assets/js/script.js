/*proloader*/
function load()
{
  document.querySelector('.placeholder').style.display="none";
  document.querySelector('.main-display').style.display="block";
}

/*insection observer API */
function observerImages()
{
    var images=document.querySelectorAll('[data-src]'),
    imgOpts={},
    observer=new IntersectionObserver((entries,observer)=>
    {
        entries.forEach((entry)=>
        {
            if(!entry.isIntersecting) return;
            const img=entry.target;
            const newUrl=img.getAttribute('data-src');
            img.src=newUrl;
            observer.unobserve(img);
        });
    },imgOpts);
  
    images.forEach((image)=>
    {
      observer.observe(image)
    });
}
$(document).on('click','.color-item',function()
{
  localStorage.theme_name=$(this).data('class');
  var color=$(document).find('body').attr('class').split(' ')[0],
  theme={
    'theme-red': '#ef3724',
    'theme-blue': '#2960f7',
    'theme-green': '#8cc63f',
    'theme-orange': '#fd7e14',
    'theme-purple': '#6f42c1'
  };
  const style=document.querySelector('style');
  style.innerHTML='::-webkit-scrollbar-thumb{background:'+theme[color]+' !important;';
  document.head.appendChild(style);
  if(localStorage.darktheme)
  {
    localStorage.lighttheme=false;
    $('body').addClass("theme-dark");
  }
  else
  {
    localStorage.darktheme=false;
    $('body').removeClass("theme-dark");
  }

});
$(document).on('click','#darktheme',function()
{
  localStorage.darktheme=$(this).is(':checked');
  localStorage.theme_bg='darktheme';
  localStorage.lighttheme=false;
});
$(document).on('click','#lighttheme',function()
{
  localStorage.lighttheme=$(this).is(':checked');
  localStorage.theme_bg='lighttheme';
  localStorage.darktheme=false;
});
$(document).ready(function ()
{  
    observerImages();
    var b=$('body').attr('class').split(' '),
    c=$(b).get(-1);
    if(c == 'ls-closed')
    {
        $('.user-pallate').addClass('user-area');
    }
    if(localStorage.getItem("theme_name"))
    {
      $('body').removeClass('theme-red').addClass(localStorage.getItem("theme_name"));
      $(document).find('.color-bar span[data-class="theme-red"]').removeClass('selected');
      $(document).find('.color-bar span[data-class="'+localStorage.getItem("theme_name")+'"]').addClass('selected');
      $(document).find('#'+localStorage.getItem("theme_bg")).attr('checked',true);
    }
    if(localStorage.getItem('darktheme') == 'true')
    {
      $('body').addClass("theme-dark");
    }
    else
    {
      $('body').removeClass("theme-dark");
    }
});

$(document).on('click','.ls-toggle-btn',function()
{
    var b=$('body').attr('class').split(' '),
    c=$(b).get(-1);
    if(c !== 'ls-toggle-menu')
    {
        $('.user-pallate').removeClass('user-area');
    }
    else
    {
        $('.user-pallate').addClass('user-area');
    }
});


/*login form*/
$(document).on('submit','.login_form',function()
{   
    var form_data=new FormData(this);
    $('.feedback').removeClass('invalid-feedback').html('');
    $('.vg-contact-form input').removeClass('is-invalid').removeClass('is-valid');
    $.ajax(
    {
        url:$(this).data('url'),
        type:'post',
        dataType:'json',
        data:form_data,
        cache:false,
        contentType:false,
        processData:false,
        beforeSend:function()
        {
            $('.login_spinner').show();
            $('.login_text').text(' Please wait...');
            $('#login_btn').attr('disabled',true);
        },
        success:function(callback)
        {
            $('.login_spinner').hide();
            $('.login_text').text('Login');
            $('#login_btn').attr('disabled',false);
            var data=JSON.parse(callback);
            if(data.valid)
            {
                $('.message').html('<div class="alert alert-success">'+data.feedback+'</div>');
                window.location='/projects';
            }
            else
            {
                $('.message').html('<div class="alert alert-danger">'+data.feedback+'</div>');
                $(".login_form input[name='username']").addClass('is-invalid');
                $(".login_form input[name='password1']").addClass('is-invalid');
            }
        },
        error:function()
        {
            $('.login_spinner').hide();
            $('.login_text').text('Login');
            $('#login_btn').attr('disabled',false);
            alert('something went wrong');
        }
    });
    return false;
});

/*register form*/
$(document).on('submit','.register_form',function()
{   
    var form_data=new FormData(this);
    $('.feedback').removeClass('invalid-feedback').html('');
    $('.vg-contact-form input').removeClass('is-invalid').removeClass('is-valid');
    $.ajax(
    {
        url:$(this).data('url'),
        type:'post',
        dataType:'json',
        data:form_data,
        cache:false,
        contentType:false,
        processData:false,
        beforeSend:function()
        {
            $('.register_spinner').show();
            $('.register_text').text(' Please wait...');
            $('#register_btn').attr('disabled',true);
        },
        success:function(callback)
        {
            $('.register_spinner').hide();
            $('.register_text').text('Register');
            $('#register_btn').attr('disabled',false);
            var data=JSON.parse(callback);
            if(data.valid)
            {
                $('.message').html('<div class="alert alert-success">'+data.feedback+'</div>');
                window.location='/account_activate';
            }
            else
            {
                $.each(data.feedback,function(key,value)
                {
                    $(".vg-contact-form input[name='"+key+"']").addClass('is-invalid').parent().find('.feedback').addClass('invalid-feedback').html(value[0]);
                    $(".vg-contact-form textarea[name='"+key+"']").addClass('is-invalid').parent().find('.feedback').addClass('invalid-feedback').html(value[0]);
                });
            }
        },
        error:function()
        {
            $('.register_spinner').hide();
            $('.register_text').text('Register');
            $('#register_btn').attr('disabled',false);
            alert('something went wrong');
        }
    });
    return false;
});






/*ActiveForm*/
$(document).on('submit','.ActiveForm',function()
{
    var el=$(this),
    urlparams=new URLSearchParams(window.location.search),
    next=urlparams.get('next'),
    btn_txt=el.find('button:last').text(),
    form_data=new FormData(this);
    $('.feedback').html('');
    el.children().find('.is-invalid').removeClass('is-invalid');
    $.ajax(
    {
      url:el.attr('action'),
      method:el.attr('method'),
      dataType:'json',
      data:form_data,
      contentType:false,
      cache:false,
      processData:false,
      beforeSend:function()
      {
        el.find('button:last').html('<i class="spinner-border spinner-border-sm" role="status"></i> Please wait...').attr('disabled',true);
      },
      success:function(callback)
      {
        el.find('button:last').text(btn_txt).attr('disabled',false);
        if(callback.valid)
        {
            $('.small-model').modal({show:true});
            $('.small-model').find('.modal-title').text('Success');
            $('.small-model').find('.modal-body').html('<div class="text-success text-center"><i class="fa fa-check-circle"></i> '+callback.message+'.</div>');
            el[0].reset();
            if(callback.register)
            {
                window.location='/accounts/activate';
            } 
            if(callback.login)
            {
                if(next)
                {
                    window.location=next;
                }
                else
                {
                    window.location='/questions';
                }
            }
          }
        else
        {
            $.each(callback.uform_errors,function(key,value)
            {
              el.find("input[aria-label='"+key+"'],select[aria-label='"+key+"'],textarea[aria-label='"+key+"']").addClass('is-invalid').parents('.form-group,.wrapper').find('.feedback').addClass('text-danger').html('<i class="fa fa-exclamation-circle"></i> '+value);
            });
            $.each(callback.eform_errors,function(key,value)
            {
              el.find("input[aria-label='"+key+"'],textarea[aria-label='"+key+"'],select[aria-label='"+key+"']").addClass('is-invalid').parents('.form-group,.wrapper').find('.feedback').addClass('text-danger').html('<i class="fa fa-exclamation-circle"></i> '+value);
            });
        }
        if(callback.error)
        {
            $('.small-model').modal({show:true});
            $('.small-model').find('.modal-title').text('Info');
            $('.small-model').find('.modal-body').html('<div class="text-info text-center"><i class="fas fa-exclamation-triangle"></i> No changes made.</div>');
        }
      },
      error:function(err)
      {
        el.find('button:last').text(btn_txt).attr('disabled',false);
      }
    });
  return false;
});

$(document).on('click','.getprofilepic',function()
{
    var el=$(this);
    el.removeClass('getprofilepic fa fa-camera').addClass('uploadbtn spinner-border spinner-border-sm');
    $('#id_profile_pic').click();
});


/*ProfileForm*/
$(document).on('submit','.ProfileImageForm',function()
{
  var el=$(this),
  form_data=new FormData(this);
  $('.feedback').html('');
  $.ajax(
    {
      url:el.attr('action'),
      method:el.attr('method'),
      dataType:'json',
      data:form_data,
      contentType:false,
      cache:false,
      processData:false,
      beforeSend:function()
      {
        $('.uploadbtn').removeClass('ti-upload').addClass('spinner-border spinner-border-sm');
      },
      success:function(callback)
      {
        $('.uploadbtn').removeClass('uploadbtn spinner-border spinner-border-sm').addClass('getprofilepic fa fa-camera');
        if(callback.valid)
        {
            $('.small-model').modal({show:true});
            $('.small-model').find('.modal-title').text('Success');
            $('.small-model').find('.modal-body').html('<div class="text-success text-center"><i class="fa fa-check-circle"></i> '+callback.message+'.</div>');
            el[0].reset();
          }
        else
        {
            $.each(callback.uform_errors,function(key,value)
            {
              el.find("input[aria-label='"+key+"']").addClass('is-invalid').parents('.form-group').find('.feedback').addClass('invalid-feedback').html('<i class="fa fa-exclamation-circle"></i> '+value);
            });
        }
        if(callback.error)
        {
            $('.small-model').modal({show:true});
            $('.small-model').find('.modal-title').text('Info');
            $('.small-model').find('.modal-body').html('<div class="text-info text-center"><i class="fas fa-exclamation-triangle"></i> No changes made.</div>');
        }
      },
      error:function(err)
      {
        $('.uploadbtn').removeClass('spinner-border spinner-border-sm').addClass('ti-upload');
        console.log(err.status+':'+err.statusText);
      }
    });
  return false;
});

$(document).on('change','.profile',function()
{
    var el=$(this),
    file=el.get(0).files[0],
    ext=el.val().substring(el.val().lastIndexOf('.')+1).toLowerCase();
    $('.uploadbtn').removeClass('spinner-border spinner-border-sm').addClass('ti-upload');
    if(file && (ext=='jpg' || ext=='png' || ext=='jpeg' || ext=='gif'))
    {
        var reader=new FileReader();
        reader.onload=function(e)
        {
            $('.imagecard').find('img:last').attr('src',reader.result);
            $('.uploadbtn').removeClass('spinner-border spinner-border-sm').addClass('ti-upload').parent().attr('type','submit');
        }
        reader.readAsDataURL(file);
    }
    else
    {
      $('.small-model').modal({show:true});
      $('.small-model').find('.modal-title').text('Warning');
      $('.small-model').find('.modal-body').html('<div class="text-warning text-center"><i class="zmdi zmdi-alert-triangle"></i> Invalid image format</div>');
    }
});

/*ActiveForm*/
$(document).on('submit','.UploadForm',function()
{
  var el=$(this),
  form_data=new FormData(this);
  $('.feedback').html('');
  el.children().find('.is-invalid').removeClass('is-invalid');
  $.ajax(
    {
      url:el.attr('action'),
      method:el.attr('method'),
      dataType:'json',
      data:form_data,
      contentType:false,
      cache:false,
      processData:false,
      beforeSend:function()
      {
        el.find('button:last').attr('disabled',true).html('<i class="spinner-border spinner-border-sm" role="status"></i> Please wait...');
      },
      xhr:function()
      {
        const xhr=new window.XMLHttpRequest();
        xhr.upload.addEventListener('progress',function(e)
        {
          if(e.lengthComputable)
          {
            const percent=Math.round((e.loaded/e.total)*100);
            el.find('button:last').html('<i class="spinner-border spinner-border-sm" role="status"></i> Uploading '+percent+'% ...');
          }
        });
        return xhr
      },
      success:function(callback)
      {
        el.find('button:last').attr('disabled',false).html('submit');
        if(callback.valid)
        {
            $('.small-model').modal({show:true});
            $('.small-model').find('.modal-title').text('Success');
            $('.small-model').find('.modal-body').html('<div class="text-success text-center"><i class="fa fa-check-circle"></i> '+callback.message+'.</div>');
            el.find('small').html('');
            $('.dropify-clear').click();
            el[0].reset();
            if(callback.project_id)
            {
              window.location='/add/pictures/'+callback.project_id+'/';
            }
          }
        else
        {
            $.each(callback.uform_errors,function(key,value)
            {
              el.find("input[aria-label='"+key+"'],textarea[aria-label='"+key+"']").addClass('is-invalid').parents('.form-group').find('.feedback').addClass('invalid-feedback').html('<i class="fa fa-exclamation-circle"></i> '+value);
            });
        }
        if(callback.error)
        {
            $('.small-model').modal({show:true});
            $('.small-model').find('.modal-title').text('Info');
            $('.small-model').find('.modal-body').html('<div class="text-info text-center"><i class="fas fa-exclamation-triangle"></i> No changes made.</div>');
        }
      },
      error:function(err)
      {
        el.find('button:last').attr('disabled',false).html('submit');
      }
    });
  return false;
});

$(document).on('change','.fileinput',function()
{
    var el=$(this),
    file=el.get(0).files[0],
    ext=el.val().substring(el.val().lastIndexOf('.')+1).toLowerCase();
    if(file && (ext=='zip' || ext=='rar'))
    {
        return true;
    }
    else
    {
      $('.small-model').modal({show:true});
      $('.small-model').find('.modal-title').text('Warning');
      $('.small-model').find('.modal-body').html('<div class="text-warning text-center"><i class="zmdi zmdi-alert-triangle"></i> Invalid image format</div>');
      $('.dropify-clear').click();
    }
});
$(document).on('change','input[type=file]',function()
{
  $(this).removeClass('is-invalid').addClass('is-valid').parent().find('.feedback').removeClass('invalid-feedback').addClass('valid-feedback').html('Filename: '+this.files[0].name);
});


$(document).on('click','.del-data',function(e)
{
  e.preventDefault();
  var el=$(this);
  $('.delete-model').modal({show:true});
  $('.delete-model').find('.modal-title').text('Confirm');
  $('.delete-model').find('.modal-body').html('<div class="text-warning text-info text-center"><i class="fa fa-alert-triangle"></i> Confirm deleting item .</div> <div class="text-center"><button class="btn btn-secondary cancelBtn" >cancel</button><button data-host="'+el.data('host')+'" data-url="'+el.attr('href')+'" class="btn btn-danger confirmBtn">confirm</button></div>');
});

$(document).on('click','.cancelBtn',function()
{
  $(this).parents('.modal').find('.close').click();
});

$(document).on('click','.confirmBtn',function()
{
  var el=$(this),
  url=el.data('url');
  $.ajax(
      {
        url:url,
        dataType:'json',
        beforeSend:function()
        {
          el.html('<i class="spinner-border spinner-border-sm" role="status"></i> Please wait...');
        },
        success:function(callback)
        {
          el.html('confirm');
          refreshPage(el,el.data('host'),'table-results');
          $('.delete-model').modal('hide');
          if(callback.valid)
          {
            $('.small-model').modal('show');
            $('.small-model').find('.modal-title').text('Success');
            $('.small-model').find('.modal-body').html('<div class="text-success text-center"><i class="fa fa-check-circle"></i> '+callback.message+'.</div>');
          }
          else
          {
            $('.small-model').modal('show');
            $('.small-model').find('.modal-title').text('Warning');
            $('.small-model').find('.modal-body').html('<div class="text-warning text-center"><i class="fa fa-exclmation-circle"></i> '+callback.message+'</div>');
          }
        },
        error(err)
        {
          el.html('confirm');
          console.log(err.status+':'+err.statusText);
        }
      });
});

/*refreshPage*/
function refreshPage(wrapper,url, target)
{
    $.ajax(
    {
      url:url,
      context:this,
      dataType:'html',
      success:function(callback)
      {
        $(document).find('.'+target).html($(callback).find('.'+target).html());
        observerImages();
      },
      error:function(err)
      {
        console.log(err.status+':'+err.statusText);
      }
    });
}
