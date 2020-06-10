#coding=utf-8
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import mod_util
import math
#--------------------------------------------------------------------------------------------------

def csrf_token(local):
  return ['<input type="hidden" name="csrfmiddlewaretoken" value="', local['csrf_token'] , '" />']

#==================================================================================================
def header(params,local):
  HTML = ['<!DOCTYPE html><html><head><link href="/wordnet_static/css/stylesheet.css" rel="stylesheet" type="text/css">']
  HTML.append('<meta charset="utf-8">')
  if 'redirect' in local:
    HTML.append('<meta http-equiv="refresh" content="3;url=')
    HTML.append(local['redirect'])
    HTML.append('" />')
  HTML.append('</head><body>')
  
  """HTML.append('''<script>
      window.fbAsyncInit = function() {
        FB.init({
          appId      : '760003160750945',
          xfbml      : true,
          status : true, // check login status
          cookie : true,
          version    : 'v2.1'
        });
        
        //if(FB.getSession() != null) {
          FB.api('/me', function(response) 
              {
                  alert ("Your UID is " + response.id); 
              });
         // }
      };

      (function(d, s, id){
         var js, fjs = d.getElementsByTagName(s)[0];
         if (d.getElementById(id)) {return;}
         js = d.createElement(s); js.id = id;
         js.src = "//connect.facebook.net/en_US/sdk.js";
         fjs.parentNode.insertBefore(js, fjs);
       }(document, 'script', 'facebook-jssdk'));
       
       
       
       
    </script>''')"""
  
  HTML.append('<header>')
  HTML.append('<nav>')
  for n in params['nav']:
    HTML.append('<a href="')
    HTML.append(reverse(n['pattern']))
    if local.get('active_nav') == n:
      HTML.append('" id="selected">')
    else:
      HTML.append('">')
    HTML.append(n['name'])
    HTML.append('</a>')
  HTML.append('</nav>')
  HTML.append('<a href="')
  HTML.append(reverse('index'))
  HTML.append('"class="logo"></a>')

  
  
  HTML.append('<div class="auth">')
  user=local['request'].user
  if user is not None and user.is_authenticated():
    username=user.username
    
    HTML.append('<a class="logout" href="')
    HTML.append(params['reverse']('logout'))
    HTML.append('">logout</a>')
    HTML.append('<a class="user">')
    db_user = User.objects.get(username=username)
    if db_user.first_name:
      HTML.append(db_user.first_name)
      if db_user.last_name:
        HTML.append(' ')
        HTML.append(db_user.last_name)
    else:
      HTML.append(username)
    
    #if username in user_map:
    #  HTML.append('</a><a class="profile-img" style="background-image:url(\'//graph.facebook.com/'+user_map[username]+'/picture?type=square\')"></a>')
    #else:
    
  else:
    HTML.append('<a href="')
    HTML.append(reverse("register"))
    HTML.append('" class="user">Request Account</a>')

  HTML.append('</a><a class="profile-img" style="background-image:url(\'//lh3.googleusercontent.com/uFp_tsTJboUY7kue5XAsGA=s148\')"></a>')
      
    
    

  HTML.append('</div>')
  
  HTML.append('</header>')
  
  return HTML
  
#==================================================================================================  
def synset_info(params,local,synset):
  
  pos_map = { 'n' : 'noun',
              'v' : 'verb',
              'a' : 'adjective',
              'r' : 'adverb',
              's' : 'adjective <i>satelite</i>'
            }
  
  HTML = []
  HTML.append('<section><div class="synset_info serif">')
  HTML.append('<div id="ripped"></div>')
  HTML.append('<p class="lemma_names">')

  lemma_names = []
  for lemma in synset['lemma_names']:
    lemma_names.append('<span>'+lemma+'</span>')

  HTML.append(', '.join(lemma_names).replace('_','&nbsp;'))
  HTML.append('</p>')
  HTML.append('<h1>')
  HTML.append(synset['synset_name'])
  HTML.append('</h1><h2>')
  HTML.append(pos_map[synset['pos']])
  HTML.append('</h2>')
  HTML.append('<p class="gloss" id="en_gloss">|')
  
  HTML.append(synset['gloss'])
  
  HTML.append('|</p><p class="gloss" id="gt_gloss">|')
  
  HTML.append(synset['GT_gloss'].lower())
  
  HTML.append('|</p><ul class="sentences">')
  
  for sentence in synset['sentences']:
    HTML.append('<li>')
    HTML.append(sentence)
    HTML.append('</li>')
    
  HTML.append('</ul>')
  
  
  HTML.append('<div id="bottom"></div></div>')


  HTML.extend(translate_panel(local,synset))


  return HTML

#==================================================================================================
def translate_panel(local,synset):
  seperate = local.get('seperate',False)
  active_nav = local.get('active_nav')['name']
  HTML = []
  
  HTML.append('<div class="right_panel"><form method="POST"><div class="translate_lemmas')

  final_translation = synset.get('final_translation', None)

  lemmas_length = len(synset['lemma_names'])

  if active_nav == 'Overview':
    HTML.append(' all">')

    lemma_names_dict = {}
    gloss_dict = {}
    sentences_dict = {}
    for user in synset['user_translations']:

      if len(user['lemma_names'])<=lemmas_length:
        user['relevant'] = len(user['lemma_names'])/float(lemmas_length)
      else:
        user['relevant'] = float(lemmas_length)/len(user['lemma_names'])

      if 'gloss' in user:
        gloss_dict[user['gloss']] = gloss_dict.get(user['gloss'], 0) + 1

      for lemma in user['lemma_names']:
        lemma_names_dict[lemma] = lemma_names_dict.get(lemma, 0) + 1

      for sentence in user['sentences']:
        sentences_dict[sentence] = sentences_dict.get(sentence, 0) + 1




    lemma_names_sorted = sorted(lemma_names_dict.items(), key=lambda x: x[1], reverse=True)
    gloss_sorted = sorted(gloss_dict.items(), key=lambda x: x[1], reverse=True)
    sentences_sorted = sorted(sentences_dict.items(), key=lambda x: x[1], reverse=True)
 
    translated_lemma_names = set([])

    max_lemma = 0
    for i, lemma in enumerate(lemma_names_sorted):
      lemma_names_sorted[i] = list(lemma_names_sorted[i])
      lemma_names_sorted[i].append(0)
      if lemma_names_sorted[i][1] > max_lemma:
        max_lemma = lemma_names_sorted[i][1]

      for user in synset['user_translations']:
        if lemma_names_sorted[i][0] in user['lemma_names']:
          lemma_names_sorted[i][2] += user['relevant']

      print lemma_names_sorted[i]

    lemma_names_sorted = sorted(lemma_names_sorted, key=lambda x: x[2], reverse=True)

    checked = math.ceil(lemmas_length * 1.5)

    if not final_translation:
      for lemma in lemma_names_sorted:
        HTML.append('<span>')
        HTML.append('<input id="'+lemma[0]+'" type="checkbox" name="translated_lemmas" value="')
        HTML.append(lemma[0])
        if max_lemma - lemma[1] <=2 and checked>0:
          chk='checked'
          checked-=1
        else:
          chk=''
          checked-=1

        HTML.append('"'+chk+'><label for="'+lemma[0]+'">'+lemma[0].replace('_','&nbsp;')+ '&nbsp;(' +str(lemma[1])+')</label>')
        HTML.append('</span>')
    else:
      final_translated_lemmas = final_translation['lemma_names']

      for lemma in final_translated_lemmas:
        HTML.append('<span>')
        HTML.append('<input id="'+lemma+'" type="checkbox" name="translated_lemmas" value="')
        HTML.append(lemma)
        HTML.append('" checked><label for="' + lemma + '">' + lemma.replace('_','&nbsp;') + '</label>')
        HTML.append('</span>')
      for lemma in lemma_names_sorted:
        if lemma[0] not in final_translated_lemmas:
          HTML.append('<span>')
          HTML.append('<input id="'+lemma[0]+'" type="checkbox" name="translated_lemmas" value="')
          HTML.append(lemma[0])
          HTML.append('"><label for="'+lemma[0]+'">'+lemma[0].replace('_','&nbsp;')+ '&nbsp;(' +str(lemma[1])+')</label>')
          HTML.append('</span>')
          
    HTML.append('<hr><span id="add_field" onclick="add_lemma()">+</span>')



  elif seperate:
    HTML.append('">')
    for i,lemma in enumerate(synset['lemma_names']):
      HTML.append('<div><h1>')
      HTML.append(lemma.replace('_',' '))
      HTML.append('</h1>')
    
      j=-1
      for translation in synset['translated_lemma_names'][i]:
        j+=1
        HTML.extend(['<input type="radio" name="', str(i), '" value="', str(j), '" id="',str(i),'.',str(j), '"><label for="',str(i),'.',str(j),'">' ])
        HTML.append(translation.replace('_',' '))
        HTML.append('</label>')
        HTML.append('<br>')
    
      HTML.extend(['<input type="radio" name="',str(i),'" value="',str(j+1),'"><input type="text" name="',str(i),'.',str(j+1),'">'])
  
     
      HTML.append('</div>')
      
      
  else:
    HTML.append(' all">')
 
    translated_lemma_names = set([])

    for l in synset['translated_lemma_names']:
      for k in l:
        if k not in translated_lemma_names:
          translated_lemma_names.add(k)
          HTML.append('<span>')
          HTML.append('<input id="'+k+'" type="checkbox" name="translated_lemmas" value="')
          HTML.append(k)
          HTML.append('"><label for="'+k+'">'+k.replace('_','&nbsp;')+'</label>')
          HTML.append('</span>')
          
    HTML.append('<hr><span id="add_field" onclick="add_lemma()">+</span>')
    
    
  HTML.append('''</div><script>
	var count = 0;
	var translate_lemmas_div = document.getElementsByClassName("translate_lemmas")[0];

	function add_lemma() {
		var node = document.getElementById(count-1);

		if (node && node.value=="")
		{
			return;
		}

		//translate_lemmas_div.removeChild(translate_lemmas_div.getElementsByTagName("hr")[0]);
		translate_lemmas_div.removeChild(document.getElementById("add_field"));
		
		var span = document.createElement("SPAN");
		var input = document.createElement("INPUT");
		input.id = count;
    input.type = 'text'
    input.name = 'extra_translate_lemmas';
    
		span.appendChild(input);
		translate_lemmas_div.appendChild(span);

		//var hr = document.createElement("HR");
		var add_span = document.createElement("SPAN");
		add_span.id = "add_field";
		add_span.innerHTML = "+";
		add_span.addEventListener("click", add_lemma);

		//translate_lemmas_div.appendChild(hr);
		translate_lemmas_div.appendChild(add_span);

		count += 1;
	}
  
	function add_sentence(t) {
    var parent = t.parentNode
    var inputs =  t.parentNode.getElementsByTagName('input')
		var node = inputs[inputs.length-1]
    
		if (node && node.value=="")
		{
			return;
		}

		//translate_lemmas_div.removeChild(translate_lemmas_div.getElementsByTagName("hr")[0]);
		
		var span = document.createElement("SPAN");
		var input = document.createElement("INPUT");
    input.name = 'sentences';
        input.type = 'text'
    
		parent.appendChild(input);
	}
	</script>''')
  
  if active_nav != 'Overview':
    HTML.append('<div class="translate_optional"><div><h1>gloss</h1><textarea name="gloss"></textarea></div><div>')
    HTML.append('<div><h1>sentences</h1><input type="text" name="sentences" value=""><span onclick="add_sentence(this)">+</span></div>')
    HTML.append('</div></div>')
    
  else:
    HTML.append('<div class="translate_optional"><div><h1>gloss</h1><div>')
    
    if final_translation:
      final_gloss = final_translation.get('gloss', '')
      HTML.append('<input type="text" name="gloss" value="'+final_gloss+'">')
      HTML.append('<hr>')

    g_count = 0
    for gloss in gloss_sorted:
      if gloss[0] != '':
        g_count+=1
        HTML.append('<input type="text" name="gloss" value="'+gloss[0]+'">')
        
    if not final_translation and not g_count:
      HTML.append('<input type="text" name="gloss" value="">')


    HTML.append('<span onclick="add_sentence(this)">+</span></div>')

    HTML.append('</div><div>')

    HTML.append('<div><h1>sentences</h1>')

    if final_translation:
      final_sentences = final_translation.get('sentences', [])

      for sentence in final_sentences:
        HTML.append('<input type="text" name="sentences" value="'+sentence+'">')
      HTML.append('<hr>')

    for sentence in sentences_sorted:
      HTML.append('<input type="text" name="sentences" value="'+sentence[0]+'">')

    HTML.append('<span onclick="add_sentence(this)">+</span></div>')
    HTML.append('</div></div>')
    
  HTML.extend(csrf_token(local))
  HTML.append('<input type="submit" value="submit" class="btn submit">')
  
  if active_nav != 'Overview': HTML.append('<input type="submit" name="skip" value="skip" class="btn skip">')
    
  HTML.append('</form></div></section>')
    
  
  return HTML

#==================================================================================================  
def overview(params,local):
  db      = params['db']

  HTML    = []
  
  progress = mod_util.progress(db,local)
  
  color_map={'fully translated':'green','need aproval':'orange','not translated':'red'}
  HTML.append('<section class="overview">')
  for k in ('need aproval','fully translated','not translated'):
    HTML.append('<h1>'+k+'</h1>')
    for v in progress[k]:
      HTML.append('<a href="'+reverse('overview',args=[v['synset']])+'" style="color:'+color_map[k]+'">')
      HTML.append(v['synset']+'</a> ')
  HTML.append('</section>')
  return HTML
    

#==================================================================================================  
def login(params,local):
  HTML = []

  HTML.append('<form class="login_form" method="POST">')  
  HTML.extend(csrf_token(local))
  HTML.append('<input type="text" name="username" required>')
  HTML.append('<input type="password" name="password" required>')
  HTML.append('<input type="submit">')
  HTML.append('</form>')

  return HTML

#==================================================================================================

def register(local):
  HTML=[]
  
  HTML.append('<section class="panel">')
    
  HTML.append('<div class="panel-right">')
  HTML.append('<form class="register_form" action="register" method="POST">')
  HTML.append('<input type="hidden" name="csrfmiddlewaretoken" value="' + local['csrf_token'] + '" />')
  
  HTML.append('<fieldset><legend><i>*</i> <strong>Choose your user name</strong></legend>')
  HTML.append('<input type="text" value="" name="username" id="username" spellcheck="false" autofocus required>')
  HTML.append('</fieldset><fieldset>')
          
  HTML.append('<legend><i>*</i> <strong>E-mail</strong></legend>')
  HTML.append('<input type="email" value="" name="email" id="email" spellcheck="false" placeholder="example@example.com" required>')
  HTML.append('</fieldset><div class="space"></div><fieldset>')
  
  HTML.append('<legend><i>*</i> <strong>Create a password</strong></legend>')
  HTML.append('<input type="password" value="" name="password" id="password" spellcheck="false" required>')
  HTML.append('</fieldset><fieldset>')
  
  HTML.append('<legend><i>*</i> <strong>Confirm your password</strong></legend>')
  HTML.append('<input type="password" value="" name="password2" id="password2" spellcheck="false" required>')
  HTML.append('</fieldset><div class="space"></div><fieldset>')
  
  HTML.append('<legend><strong>Name</strong></legend>')
  HTML.append('<input type="text" value="" name="firstname" id="firstname" spellcheck="false" placeholder="First">')
  HTML.append('<input type="text" value="" name="lastname" id="lastname" spellcheck="false" placeholder="Last">')
  HTML.append('</fieldset><div class="space"></div>')
  
  HTML.append('<input type="submit" value="Register" class="button blue-button" href="#"></input>')
  HTML.append('<div class="space"></div>')
  HTML.append('</form> </div>')
  HTML.append('</section>')
  
  return HTML

#==================================================================================================

def footer():
  HTML = ['</body></html>']
  return HTML
  
#==================================================================================================


"""
"""