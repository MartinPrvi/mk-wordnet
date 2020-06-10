#coding=utf-8

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate,login, logout
from django.utils.html import escape

from django.middleware import csrf
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from modules import mod_html,mod_util

import pprint


params  = { 'db'        : mod_util.connect_db(settings),
            'settings'  : settings,
            'reverse'   : reverse
          }

nav     = [ { 'name':'Translate',  'pattern':'synset'},
{ 'name':'Overview',  'pattern':'overview'}
          ]

params['nav'] = nav


#==================================================================================================
@login_required()
def overview(request,obj_id=None, offset_pos=None, synset_synset=None, complete=''):
  db = params['db']
  
  if request.user.is_staff:
    pass
  else:
    return HttpResponseRedirect(reverse('index'))
  
  local = { 'request'     : request,
            'csrf_token'  : csrf.get_token(request),
            'active_nav'  : nav[1],
            'all'         : complete=='all'
          }

  
  HTML = []
  
  HTML.extend(mod_html.header(params,local))
  if not (obj_id or offset_pos or synset_synset):
    HTML.extend(mod_html.overview(params,local))
  else:
    
    
    synset = params['db'].synsets.find_one({'synset':synset_synset})
    
    if request.method == "POST":
    
      if not synset:
        return HttpResponse('<h1>Hehehe, ne sme od vcera :)</h1>')

      final_translation =  { 'username'   : request.user.username,
                            'lemma_names' : request.POST.getlist('translated_lemmas'),
                            'sentences'   : [],
                          }
    
      
      for lemma in request.POST.getlist('extra_translate_lemmas'):
        if lemma:     final_translation['lemma_names'].append(lemma.replace(' ', '_'))
      
      for sentence in request.POST.getlist('sentences'):
        if sentence: final_translation['sentences'].append(sentence)
      
      gloss = request.POST.get('gloss', '')
      if gloss: final_translation['gloss'] = gloss
      
      db.synsets.update(  {'_id':synset['_id']},
                          {'$set': {'final_translation': final_translation, 'is_translated': True}},
                          upsert=True, multi=False
                        )
      return HttpResponseRedirect(reverse('overview'))
    #------------------------------------------------------------  
    
    if not synset['num_translations']:
      return HttpResponseRedirect(reverse('synset_synset',args=[synset_synset]))
    
    HTML.extend(mod_html.synset_info(params, local, synset))
   
  HTML.extend(mod_html.footer())
  
  return HttpResponse(''.join(HTML))
  
#==================================================================================================
def index(request):
  local = { 'request'     : request,
            'csrf_token'  : csrf.get_token(request),
            
          }
  
  
  HTML = []
  
  HTML.extend(mod_html.header(params,local))
  
  HTML.append('<center><img height="600px" style="margin-top:10px" src="/wordnet_static/images/similartos.png" />')
  HTML.append('<h1><a href="')
  HTML.append(reverse('login'))
  HTML.append('">Log in</a></h1></center>')
  
  HTML.extend(mod_html.footer())
  
  return HttpResponse(''.join(HTML))
  
#==================================================================================================

def user_present(username, email):

  if User.objects.filter(username=username).count() or User.objects.filter(email=email).count():
    return True

  return False

#==================================================================================================

def register_user(request):

  local = { 'request'     : request,
            'csrf_token'  : csrf.get_token(request),

          }

  if request.user.is_authenticated():
    return HttpResponseRedirect(params['http_base'])
    
  form={'username':'','email':'','firstname':'','lastname':''}
  
  if request.method == 'POST':
    form['username'] = escape(request.POST['username'])
    form['email'] = escape(request.POST['email'])
    form['password'] = escape(request.POST['password'])
    form['password2'] = escape(request.POST['password2'])
    form['firstname']=escape(request.POST['firstname'])
    form['lastname']=escape(request.POST['lastname'])
    
    if form['password']==form['password2'] and not user_present(form['username'],form['email']):#break up to find problem and display
      user = User.objects.create_user(form['username'],form['email'], form['password'])
      user.is_active=False
      if form['firstname']!='': user.first_name=form['firstname']
      if form['lastname']!='': user.last_name=form['lastname']
      user.save()
      return HttpResponseRedirect(reverse('login'))
  
  
  params['request']=request
  params['form']=form

  params['csrf_token']=csrf.get_token(request)
  request.META['CSRF_COOKIE'] = params['csrf_token']

  params['active']='Create account'
  HTML=[]
  HTML.extend(mod_html.header(params, local))
  
  HTML.extend(mod_html.register(local))
  
  HTML.extend(mod_html.footer())

  return HttpResponse(''.join(HTML))

#==================================================================================================

@login_required()
def synset(request, obj_id=None, offset_pos=None, synset_synset=None):
  
  db = params['db']
  
  local = { 'request'     : request,
            'csrf_token'  : csrf.get_token(request),
            'active_nav'  : nav[0],
            'seperate'    : False
          }

  
  if request.method == "POST":
    synset = db.synsets.find_one({'opened_by':request.user.username, 'synset':synset_synset})
    
    if not synset:
      return HttpResponse('<h1>Hehehe, ne sme od vcera :)</h1>')
    
    if request.POST.get('skip'):
      db.synsets.update(  {'_id':synset['_id']},
                          {'$push':{'skipped_by':request.user.username}},
                          upsert = False, multi = False
                        )
      return HttpResponseRedirect(reverse('synset'))
    

    user_translation =  { 'username'    : request.user.username,
                          'lemma_names' : [],
                          'sentences'   : [],
                        }
                        
    if local['seperate']:
      en_i = -1
      for en_lemma in synset['lemma_names']:
        en_i +=1
        current_lemma_translation = int(request.POST.get(str(en_i),'-1'))
        if current_lemma_translation == -1:
          user_translation['lemma_names'].append('')
        if current_lemma_translation < len(synset['translated_lemma_names'][en_i]):
          user_translation['lemma_names'].append(synset['translated_lemma_names'][en_i][current_lemma_translation])
        elif current_lemma_translation == len(synset['translated_lemma_names'][en_i]):
          user_translation['lemma_names'].append(request.POST[str(en_i)+'.'+str(current_lemma_translation)])
        
        else: return HttpResponse('<h1>Hehehe, ne sme od vcera :)</h1>')

    else:
      for lemma in request.POST.getlist('translated_lemmas'):
        user_translation['lemma_names'] = request.POST.getlist('translated_lemmas')
      for extra_lemma in request.POST.getlist('extra_translate_lemmas'):
        if extra_lemma:
          user_translation['lemma_names'].append(extra_lemma.replace(' ','_'))
    for sentence in request.POST.getlist('sentences'):
      if sentence:
        user_translation['sentences'].append(sentence)
    
    gloss = request.POST.get('gloss','')
    if gloss: user_translation['gloss'] = gloss
    
    db.synsets.update(  {'_id':synset['_id']},
                        {'$push':{'user_translations':user_translation}, '$inc':{'num_translations':1}, '$set':{'opened_by':'','opened':1}},
                        upsert=False, multi = False
                      )
    
    HTML = []
    local['redirect'] = reverse('synset')
    HTML.extend(mod_html.header(params,local))
    HTML.append('<center><h1 style="color:green">Translated :)</h1><p>you will be given annother synset in 3 seconds</p></center>')
    HTML.extend(mod_html.footer())
    
    
    return HttpResponse(''.join(HTML))
      
    



  if not (obj_id or offset_pos or synset_synset):
    synset = mod_util.get_synset(params,local)
    return HttpResponseRedirect(reverse('synset_synset',args=[synset[1]]))
  
  
  synset = mod_util.get_synset(params,local,{'obj_id':obj_id, 'offset_pos':offset_pos, 'synset':synset_synset})
  
  if synset:
    synset = mod_util.lock_synset(params,local,synset)
  
  if not synset:
    return HttpResponseRedirect(reverse('synset'))

    
    
  HTML = []
  
  HTML.extend(mod_html.header(params,local))
  
  HTML.extend(mod_html.synset_info(params,local,synset))
  
  HTML.extend(mod_html.footer())
  
  return HttpResponse(''.join(HTML))
  
  
#==================================================================================================

def log_in(request):
  #if not request.is_secure():
  #  return HttpResponseRedirect(request.build_absolute_uri().replace('http://','https://'))
  if request.user.is_authenticated():
    return HttpResponseRedirect(reverse('index'))
  if request.method == 'POST':
    username = escape(request.POST['username'])
    password = escape(request.POST['password'])
    
    user = authenticate(username=username, password=password)
    if user is not None:
      if user.is_active:
        login(request, user)
        #return HttpResponse('braos, se logira '+user.usernames)
        if 'next' in request.GET:
          resp =  HttpResponseRedirect(request.GET['next'])
          resp.set_cookie('the_current_user',username,max_age=9999999999)
          return resp
        resp =  HttpResponseRedirect(reverse('index'))
        resp.set_cookie('the_current_user',username,max_age=9999999999)
        return resp
      else:
        return HttpResponse('<h1>Account Not Active</h1>')
    else:
      return HttpResponseRedirect(reverse('login'))  #nema takov

  
  local={ 'request'     : request,
          'csrf_token'  : csrf.get_token(request),
        }
  
  
  HTML=[]
  
  HTML.extend(mod_html.header(params,local))
  
  HTML.extend(mod_html.login(params,local))
  
  HTML.extend(mod_html.footer())
  
  return HttpResponse(''.join(HTML))

#==========================================================================================================================================

@login_required()
def log_out(request):
  logout(request)
  return HttpResponseRedirect(reverse('index'))

#==========================================================================================================================================