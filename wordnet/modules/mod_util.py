#coding=utf-8
import pymongo
from bson.objectid import ObjectId
import time

#from nltk.corpus import wordnet as wn
import pprint
import random
import re
import cPickle as pickle
import anydbm
import math
#import goslate

#==================================================================================================






#==================================================================================================
def connect_db(settings,db_name='mk_wordnet'):
  
  client  = pymongo.MongoClient(settings.DB_HOST,27017,fsync=True)
  db      = client[db_name]
  
  return db

#==================================================================================================




#==================================================================================================
def get_synset(params,local,d=None):
  settings  = params['settings']
  db        = params['db']['synsets']
  user      = local['request'].user
  if not d:
    
    db.update(  {'opened_by':user.username},
                {'$set':{'opened':1,'opened_by':''}},
                upsert=False, multi=True 
              )
    
    if settings.TRANSLATE_ONCE:  
      synset = db.find( { 'num_translations':0, 'is_translated':False, 'opened':{"$lt":time.time()-1800},
                          'skipped_by':{'$nin':[user.username]},'user_translations.username':{'$nin':[user.username]}
                        },
                        
                        {'synset': 1, 'offset': 1, 'pos': 1}
                      ).limit(1).sort('frequency',pymongo.DESCENDING).next()
    else:
      synset = db.find( { 'num_translations':{"$lte":3}, 'is_translated':False, 'opened':{"$lt":time.time()-1800},
                          'skipped_by':{'$nin':[user.username]},'user_translations.username':{'$nin':[user.username]}
                        },
                        {'synset': 1, 'offset': 1, 'pos': 1}
                      ).limit(1).sort('frequency',pymongo.DESCENDING).next()
      
    
    return str(synset['_id']), synset['synset'],str(synset['offset'])+'.'+synset['pos']
    

  if d.get('obj_id'):
    synset      = db.find_one({'_id': ObjectId(d['obj_id'])})
    
  elif d.get('synset'):
    synset      = db.find_one({'synset': d['synset']})
  
  elif d.get('offset_pos'):
    offset_pos  = d['offset_pos'].split('.')
    synset      = db.find_one({'offset': offset_pos[0], 'pos': offset_pos[1]})
  
  
  return synset


#==================================================================================================

def lock_synset(params,local,synset):
  db      = params['db']
  user    = local['request'].user
  now     = time.time()
  
  
  if synset['opened']>=now-1800 and synset['opened_by']!= user.username:
    return None
  
  set_fields =  { 'opened_by' : user.username,
                  'opened'    : now
                }
                
  db.synsets.update(  {'_id':synset['_id']},
                      {'$set':  set_fields},
                      upsert=False,  multi=False
                    )

  synset.update(set_fields)
  return synset


#==================================================================================================
def progress(db,local):
  if local['all']:
    d = {
    'fully translated': list(db.synsets.find({'is_translated':True}, {'synset':1,'frequency':1})),
    'need aproval': list(db.synsets.find({'num_translations':{'$gt':0},'is_translated':False }, {'synset':1,'frequency':1})),
    'not translated': list(db.synsets.find({'num_translations':0,'is_translated':False}, {'synset':1,'frequency':1})),
    }
    for kk,vv in d.iteritems():
      d[kk] = sorted(vv, key=lambda k: k['frequency'],reverse =True)
    
  else:
    d = {
    'fully translated': db.synsets.find({'is_translated':True}, {'synset':1}).limit(1000).sort('frequency',pymongo.DESCENDING),
    'need aproval': db.synsets.find({'num_translations':{'$gt':0},'is_translated':False }, {'synset':1}).limit(1000).sort('frequency',pymongo.DESCENDING),
    'not translated': db.synsets.find({'num_translations':0,'is_translated':False}, {'synset':1}).limit(1000).sort('frequency',pymongo.DESCENDING),
    }
    
  
  return d

#==================================================================================================
#=======================================       :)        ==========================================

def init_db():
  
  
  import sys,os
  sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
  import settings
  '''  Deletes the world. Use with caution.  '''
  print 'start inserting to db',
  db = connect_db(settings)
  db.drop_collection('synsets')
  print '  -- collection \'synsets\' dropped'
  
  db['synsets'].insert(pickle.load(open('../../data/synsets.pickle')))
  print 'done inserting'
  

#==================================================================================================

def extract_all_synsets():
  
    
  o = open('../../data/synsets.list','w')
  o.write('[\n')
  synsets = []
  progress=0
  for synset in wn.all_synsets():
    
    progress+=1
    
      #break
    
    s = { 'synset'                  : synset.name(),
          'synset_name'             : '.'.join(synset.name().split('.')[:-2]).replace('_',' '),
          'offset'                  : synset.offset(),
          'lexname'                 : synset.lexname(),
          'pos'                     : synset.pos(),
          #'w_cnt'       : len(synset.lemma_names()),
          #'lemmas'      : [(lemma.synset().pos(),lemma.synset().offset(),lemma.name()) for lemma in synset.lemmas()],
          'lemma_names'             : synset.lemma_names(),
          'translated_lemma_names'  : [],
          'gloss'                   : synset.definition(),
          'sentences'               : synset.examples(),
        }
    
    if not progress%500:
      print progress+1,'/ 117659','  (%0.2f' % (progress / 117659.0 *100),'%)' 
      print '='.ljust(50,'=')
      print s['pos']+',',s['lemma_names'][0].replace('_',' ')
      print s['gloss']
      
    for ll,lemma in enumerate(s['lemma_names']):
      
      s['translated_lemma_names'].append(translate(lemma))
      if not progress%500:
        print
        print '-'.ljust(50,'-')
        print ' '.join(lemma.split('_'))
        print '··················································'
      
        for translation in s['translated_lemma_names'][ll]:
          print ' '.join(translation.split('_'))
      
        print '-'.ljust(50,'-')
        
    if not progress%500: print '='.ljust(50,'=')
    
    for k,v in synset._pointers.iteritems():
      s[POINTERS[k]]  = list(v)
        
    
    
    
    o.write('\n\n#-----------------  ')
    o.write(s['synset_name'])
    o.write('  -----------------\n')
    o.write(pprint.pformat(s))
    o.write(',')
    synsets.append(s)
  
  o.write('\n]')
  o.close()
  pickle.dump(synsets,open('../../data/synsets.pickle','w'),2)
  
  
  init_db() 


#==================================================================================================


def translate(query,test=False):
  
  query   = query.split('_')
  q_len   = len(query)
  s_query = ' '.join(query) 
  
  translations = set()
  
  seperate_translations = []
  mk_en = {}
  for term in query:
    #term = term.decode('utf-8').lower().encode('utf-8')
    setwhere = pickle.loads(db_dict.get('where_' + term,b'\x80\x02].'))
    
    mk_translations = []
    for line in setwhere:
      line = pickle.loads(db_dict['line_' + str(line)])
      mk_translations.append(line[2])
      
      mk_en[line[2]] = mk_en.get(line[2],set()) | set([line[1]])
  
      
    
    seperate_translations.append(mk_translations)
    
  translations = set()
  for translation in seperate_translations:
    translations.update(translation)

  for translation in seperate_translations:
    translations.intersection_update(translation)
  
  translation_scores = {}
  
  for translation in translations:

    exact_find_mult = 1
    
    for x in mk_en.get(translation,[]):
      x = re.sub(strip_re,'',x)
      if x == s_query:
        exact_find_mult = 6
        break
        
    
    translation = translation.split()
    normalized_translation = []
    
    for term in translation:
      term = term.decode('utf-8').lower().encode('utf-8')
      normalized_translation.append(wfl.get(term,term))
    
    freq = int(n_gram_count.get('_'.join(normalized_translation),1))
      
    if q_len -1 <= len(translation) <= q_len+1: mult = 1+4-abs(q_len - len(translation))*2
    else:                                       mult = 1
    
    
    
    translation = '_'.join(translation)
    
    #if translation in wfl and wfl[translation]==translation: mult+=1 #ke vidime :)
    if not len(translation):
      score = -1
    else:
      score = math.log(freq/3.0) * abs(math.log(1.0/len(translation))) * mult * exact_find_mult

    if score>=0.0:
      translation_scores[translation] = score
  
  if test:
    return sorted(translation_scores.items(), key=lambda x: x[1], reverse=True)[:10]
  return sorted(translation_scores, key=translation_scores.get, reverse=True)[:10]

#==================================================================================================
def g_translate_gloss():
  i=0


  while i < len(synsets):

    gs = goslate.Goslate()
    tmp = gs.translate([s['gloss'] for s in synsets[i:]],'mk','en')

    while True:

      try:
        t = next(tmp)
        #start+=1

        if not i%1000:
          print('==================')
          print synsets[i]['synset_name']
          print synsets[i]['gloss'].ljust(100), t

        synsets[i]['GT_gloss'] = t
        i+=1

      except:
        print 'failed: ',i,'============================'
        print 'retrying from ', i
        break


  print 'start pickle'
  pickle.dump(synsets,open('../../data/synsets.pickle','w'),2)



#==================================================================================================
def test_translation():

  manual = None
  while True:
    #possible = translate(raw_input().strip().replace(' ','_'))
    if manual:
      synset = manual
    else:
      synset = synsets[random.randrange(len(synsets))]
      manual = None
    print
    print '='.ljust(50,'=')
    print synset['pos']+',',synset['lemma_names'][0].replace('_',' ')
    print synset['gloss']
    for lemma in synset['lemma_names']:
      possible = translate(lemma,True)
      print
      print '-'.ljust(50,'-')
      print ''.join(lemma)
      print '··················································'
      for k in possible:
        print k[0].decode('utf-8').ljust(30).encode('utf-8'),k[1]

      print '-'.ljust(50,'-')
      
    print '='.ljust(50,'=')
    command = raw_input()
    if command == '':
      continue
    elif command=='exit()':
      break
    else:
      manual =  { 'pos'        : '_',
                  'lemma_names' : [command],
                  'gloss'       : '____________'
                }
  #for word in translate_ngram('mad_house'):
  #  print word

#==================================================================================================
def calculate_frequency():
  pos_index = {'n': 1000, 'a':100, 's': 100, 'r': 100, 'v': 10}

  for i, synset in enumerate(synsets):
    first = synset['translated_lemma_names'][0]
    
    if len(first) > 0:
      trans = first[0]
    else:
      trans = ''
    
    trans = trans.split('_')
    for m, t in enumerate(trans):
      trans[m] = wfl.get(t, t)

    trans = '_'.join(trans)
    frequency = int(n_gram_count.get(trans, '0'))

    synsets[i]['frequency'] = frequency * pos_index[synset['pos']]
    #synsets[i] = synset

    if synset['synset'] == 'tell.n.01':
      print synsets[i]['frequency'], trans, n_gram_count.get(trans, 0)
      print "###########################" * 10

  pickle.dump(synsets, open('../../data/synsets.pickle', 'w'), 2)

#--------------------------------------------------------------------------------------------------
def calculate_frequency_v2():
  for i, synset in enumerate(synsets):
    translated_lemmas = {}
    
    for lemma_list in synset['translated_lemma_names']:
      for lemma in lemma_list:
        translated_lemmas[lemma] = translated_lemmas.get(lemma, 0) + 1

    set_lemma_names = set([])

    for l in synset['translated_lemma_names']:
      for k in l:
        if k not in set_lemma_names:
          set_lemma_names.add(k)
    set_lemma_names = list(set_lemma_names)

    sum_frequency = 0
    for lemma in translated_lemmas:
      trans = lemma
      trans = lemma.split('_')
      for m, t in enumerate(trans):
        trans[m] = wfl.get(t, t)

      trans = '_'.join(trans)
      lemma_frequency = int(n_gram_count.get(trans, '0')) * translated_lemmas[lemma] * 1.0/(set_lemma_names.index(lemma)+1) * len(set_lemma_names)

      sum_frequency += lemma_frequency

      #print lemma + ' ' + str(lemma_frequency) + ' ' + str(translated_lemmas[lemma])

    if len(translated_lemmas) != 0:
      sum_frequency = sum_frequency/len(translated_lemmas)

    synsets[i]['frequency'] = sum_frequency

    if i%1000 == 0:
      print synset['synset'] + ' ' + str(sum_frequency)


  pickle.dump(synsets, open('../../data/synsets.pickle', 'w'), 2)

#==================================================================================================
def make_en_frequency_pickle():
  en_frequency = {}

  for line in open('../../data/en_frequency.txt', 'r'):
    line = line.strip()
    line_list = line.split(' ')
    if len(line_list[0]) == 1:
     continue
    en_frequency[line_list[0]] = int(line_list[1])

  pickle.dump(en_frequency, open('../../data/en_frequency.pickle', 'w'), 2)
#--------------------------------------------------------------------------------------------------
def get_frequency(word, en_frequency):
  return en_frequency.get(word, 0) + 1
#--------------------------------------------------------------------------------------------------
def test_frequency():
  #synsets = pickle.load(open('../../data/synsets.pickle'))
  en_frequency = pickle.load(open('../../data/en_frequency.pickle'))

  synset_freq = {}
  for synset in synsets:
    synset_name = synset['synset_name']
    synset_freq[synset_name] = get_frequency(synset_name, en_frequency)

  for k, v in sorted(synset_freq.items(), key=lambda synset_freq: synset_freq[1]):
    print k, v
#--------------------------------------------------------------------------------------------------
def add_frequency_to_synsets():
  synsets = pickle.load(open('../../data/synsets.pickle'))
  en_frequency = pickle.load(open('../../data/en_frequency.pickle'))

  for synset in synsets:
    synset['frequency'] = get_frequency(synset['synset_name'], en_frequency)

  pickle.dump(synsets, open('../../data/synsets.pickle', 'w'), 2)

#==================================================================================================
def add_fields_to_synsets():
  
  fields  = { 'user_translations' : [], #{'username':'', 'lemma_names':[''], 'gloss':'', 'sentences':['']}
              'num_translations'  : 0,
              'is_translated'     : False,
              'opened'            : 1,
              'opened_by'         : '',
              'skipped_by'        : [], #usernames
            }
  
  for i,s in enumerate(synsets):
    
    for k,v in fields.iteritems():
      s[k] = v
    
    synsets[i] = s
  
  
  pickle.dump(synsets, open('../../data/synsets.pickle', 'w'), 2)    
  
#==========================================================================================================================================

def convert_u(inp):
  if isinstance(inp, dict):
    return {convert_u(key): convert_u(value) for key, value in inp.iteritems()}
  elif isinstance(inp, list):
    return [convert_u(element) for element in inp]
  elif isinstance(inp, unicode):
    return inp.encode('utf-8')
  else:
    return inp

#==========================================================================================================================================  
  
#==================================================================================================
#==================================================================================================

if __name__ == '__main__':
  #print "dictionary"
  #db_dict       = pickle.load(open('../../data/dictionary.pickle'))
  
  #print "wfl"
  #wfl           = pickle.load(open('../../data/wfl-mk.pickle'))
  
  #print "n-grams"
  #n_gram_count  = anydbm.open('../../data/mk_n-gram.anydbm')
  #n_gram_count = pickle.load(open('../../data/mk_n-gram.pickle'))
  
  #print 'synsets'
  #synsets       = pickle.load(open('../../data/synsets.pickle'))
  
  #print '\n################################################\n'
  
  #strip_re = re.compile(r'(?:(?:[^\w]|^).\.|(?:[^\w]|^)\w{1}\b(?:[^\w]|$))')
  
  #---------------------------------------
  #test_translation()
  #generate_possible_translations()
  #extract_all_synsets()
  
  #g_translate_gloss()
  #make_en_frequency_pickle()
  #test_frequency()
  #add_frequency_to_synsets()
  #add_fields_to_synsets()
  #init_db()
  #calculate_frequency()

  #calculate_frequency_v2()
  #init_db()
  #---------------------------------------

  
  #n_gram_count.close()
  print 'bye.'
  pass
