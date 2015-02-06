#Macedonian WordNet
___
->__Martin Ivanovski__, 
__Dimitar Venov__, 
__Jovan Andonov__<-



##Abstract

Living in a world striving to automate every fragment of our lives, we often encounter roadblocks in the process. This is mainly due to the vast complexity of human civilization, natural language(s) in particular. As we all know, computers are not known for their ability to deal with ambiguity. Every rule in every natural language has an exception and that exception has an exception and so on. To battle this we have taketh upon ourselves to enrich the toolbox for natural language processing by creating WordNet for the Macedonian language, without having to spend millions, or employ countless linguists and experts from every field and every subject.

===

##Method
The way we want to achieve our goal is quite simple.

1. Get an already established lexical database. 
   * WordNet (English)
2. Translate all the synonym sets (synsets).
3. Export an NLTK friendly format for later use.

===

##Translation platform

Since there are about 120 000 synsets in the English language WordNet, translation is a tedeous task and machine translation is only sufficient for less than 20% of the synsets, with questionable accuracy. For now the best processor for dealing with language ambiguity is the human brain, so we decided to employ it's power :).


###Frontend
The interface to the translation platform is a web application that picks a synset and presents it for translation. On the left-hand side there is basic information about the synset in question such as lemmas, gloss (definition), Part-of-speech and optional sentences in which the synset is used.
On the right hand side there is a form populated with possible translations for all the lemmas in the synset, a field to write a coresponding gloss and optional fields to add sentences.

###Backend

####DB Structure


```python

db.synsets=
        {
             'synset'     ,  # name(),   str,
             'synset_name',  # '.'.join(synset.name().split('.')[:-2]).replace('_',' '), str,   
             'offset'     ,  # offset(), int, int(8), synset_offset      
             'lexname'    ,  # lexname(),str, map to int(2), lex_filenum
             'pos'        ,  # pos(),    str, str, ss_type
             'lemma_names',  # lemma_names(), list formatted..
             'pointers'   ,  # for each type seperate key
             'gloss'      ,  # description()
             'sentences'  ,  # list
             
             'translated_lemma_names': [{lemma_names_mk}],
             'GT_gloss': '',
             'frequency': int(),

             'user_translations': [{username: 'user_name', lemma_names: [list_of_translated_lemmas], gloss: 'Translated glossary', sentences: [list_of_translated_sentences]}],
             'num_translations': int(),
             'is_translated': True or False,
             'final_translations': {username: 'user_name', lemma_names: [list_of_translated_lemmas], gloss: 'Translated glossary', sentences: [list_of_translated_sentences]},
        }
```
For our database we have used mongodb which is document database. For every synsets in the english Wordnet, we have a document in our database. The document structure is as it follows:

1. synset - This is a unique identifier for the given synsets. This string is in the form of lemma.pos.lemma_cnt. Lemma is the first lemma in the synset, POS is the type of the synset and can be N for Noun, V for Verb, A for Adjective, S for  Adjective Satellite and R for Adverb. Lemma_cnt is the the number of occurrence of that particular lemma.
2. synset_name - This is lemma from synset.
3. offset - Byte offset in the Wordnet File Database. It is needed for exporting the database in Wordnet and NLTK friendly format.
4. lexname - Two digit integer. It maps to one of the lexicographer files. More info http://wordnet.princeton.edu/wordnet/man/lexnames.5WN.html
5. pos - The type of the synset. Can be N for Noun, V for Verb, A for Adjective, S for  Adjective Satellite and R for Adverb.
6. lemma_names - The lemmas which are part of this synset.
7. pointers - A pointers from this synset to another. This is dictionary with values of form [pos_of_synset, synset_offset], where pos_of_synset is the type of the synset and synset_offset is the offset in that file. The types of pointers are discussed later on.
8. gloss - Glossary of the synset.
9. sentences - Examples sentences where lemmas of the synsets are used.
10. translated_lemma_names - Translations of the lemmas in this synset.
11. GT_gloss - Google translation of the glossary of the synset to Macedonian.
12. frequency - Frequency of the synset. This is disscussed later on.
13. user_translations - Translations of the synset by a human being. This is in the form of [{username: 'user_name', lemma_names: [list_of_translated_lemmas], gloss: 'Translated glossary', sentences: [list_of_translated_sentences]}].
14. num_translations - Number of times this synset is translated.
15. is_translated: True/False - Is this synset translation approved by Admin.
16. final_translations - Final translation of the synset, It is in the of {username: 'user_name', lemma_names: [list_of_translated_lemmas], gloss: 'Translated glossary', sentences: [list_of_translated_sentences]}.

###Wordnet Pointers
####Noun Pointers
```python
    '!'  : antonyms                   #       opposite in meaning
    '@'  : hypernyms                  #       parents
    '@!' : instance_hypernyms         #       \
    '~'  : hyponyms                   #       childs
    '~!' : instance_hyponyms          #       \
    '#m' : member_holonyms            #       is_part_of as member
    '#s' : substance_holonyms         #       is_part_of as substance
    '#p' : part_holonyms              #       is_part_of as part
    '%m' : member_meronyms            #       y is_part_of x where x is the synset
    '%s' : substance_meronyms         #       y is_part_of x where x is the synset
    '%p' : part_meronyms              #       y is_part_of x where x is the synset
    '='  : attributes                 #       is base for these attributes
    '+'  : drf                        #       Derivationally related form 
    ';c' : topic_domains              #       Domain of synset - TOPIC 
    '-c' : members_of_topic_domain    #       Other synsets of topic domain
    ';r' : region_domains             #       Domain of synset - REGION
    '-r' : members_of_region_domain   #       Other synsets of region domain
    ';u' : usage_domains              #       Domain of synset - USAGE
    '-u' : members_of_usage_domain    #       Other synsets of usage domain
```
####Verb Pointers
```python
    '!'  : antonyms                   #       opposite in meaning
    '@'  : hypernyms                  #       parents
    '~'  : hyponyms                   #       childs
    '*'  : entailments                #       implies
    '>'  : causes                     #       causes
    '^'  : also_see                   #       \
    '$'  : verb_groups                #       verb group
    '+'  : drf                        #       Derivationally related form 
    ';c' : topic_domains              #       Domain of synset - TOPIC 
    ';r' : region_domains             #       Domain of synset - REGION
    ';u' : usage_domains              #       Domain of synset - USAGE
```
####Adjective Pointers
```python
    '!'  : antonyms                   #       opposite in meaning
    '&'  : similar                    #       similar to
    '<'  : participle_of_verb         #       formed from a verb
	'\\'  : pertainym			       #       formed from a noun
```
####Adverb Pointers
```python
    '\\'  : pertainym                  #       derived from adjective
```


###Calculating possible translations
For this we used a dictionary from time.mk (thanks!)

The results of simply geting a list of possible translations from a dictionary espacially for a single word with no context whatsoever are quite bad.

To improve this we normalized a very large dataset consisted of news articles crawled by time.mk (thanks again!) in macedonian and counted all the unigrams, bigrams and trigrams.

Later we used normalized every token from every translation and added weight to those translations where their english translation is equal to the primary query.

Each lemma was translated this way, the results were ranked by relevance using this formula:
```python
score = math.log(freq/3.0) * abs(math.log(1.0/len(translation))) * mult * exact_find_mult

#freq : "number of occurences in the large dataset"
#translation: "macedonian word obtained from dictionary"
#mult : is the english translation of the macedonian word equal to the original query
#exact_find_mult : "is this a one-to-one translation"
```
Up to 10 results are returned.

###Calculate synset importance
For this we tried a couple of methods

First we used a large english dataset and just sorted the synsets based on the frequency of appearence of the first lemma.

Later we experimented with 2 algorithms

1.
```python
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
```

and we setled on:

```python
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
```


###Database Export
We decided the Database Export to be files compatable with Wordnet Database Files and compatable with NLTK module for the Python Programming Language.

In the Database Export there are two different file types. This are

* data.pos files
* index.pos files

where pos is noun, verb, adjective and advert.

####data.pos files
All the lines in this files are in the following format:

    synset_offset  lex_filenum  ss_type  w_cnt  word  lex_id  [word  lex_id...]  p_cnt  [ptr...] | gloss

synset_offset

	Current byte offset in the file represented as an 8 digit decimal integer.
	
lex_filenum

	Two digit decimal integer corresponding to the lexicographer file name containing the synset. See http://wordnet.princeton.edu/wordnet/man/lexnames.5WN.html for more info.
	
ss_type

	One character code indicating the synset type:
	n    NOUN 
	v    VERB 
	a    ADJECTIVE 
	s    ADJECTIVE SATELLITE 
	r    ADVERB 

w_cnt

	Two digit hexadecimal integer indicating the number of words in the synset.
	
word

	Unicode form of a word as entered in the synset by the lexicographer, with spaces replaced by underscore characters (_ ). The text of the word is case sensitive.
	
lex_id

	One digit hexadecimal integer that, when appended onto lemma , uniquely identifies a sense within a lexicographer file. lex_id numbers usually start with 0 , and are incremented as additional senses of the word are added to the same file.
	
p_cnt

	Three digit decimal integer indicating the number of pointers from this synset to other synsets. If p_cnt is 000 the synset has no pointers.
	
ptr

	A pointer from this synset to another. ptr is of the form:
		pointer_symbol  synset_offset  pos  source/target 
	where synset_offset is the byte offset of the target synset in the data file corresponding to pos. source/target is left here for compatibility reasons. See above for pointer symbols.
	
gloss

	Each synset contains a gloss. A gloss is represented as a vertical bar (| ), followed by a text string that continues until the end of the line. The gloss may contain a definition, one or more example sentences, or both.
	
####index.pos files
All the lines in this files are in the following format:
	
	lemma  pos  synset_cnt  p_cnt  [ptr_symbol...]  sense_cnt  tagsense_cnt   synset_offset  [synset_offset...] 

lemma

    lower case Unicode text of word or collocation. Collocations are formed by joining individual words with an underscore (_ ) character.

pos

    Syntactic category: n for noun files, v for verb files, a for adjective files, r for adverb files.

synset_cnt

    Number of synsets that lemma is in. This is the number of senses of the word in mk-WordNet.

p_cnt

    Number of different pointers that lemma has in all synsets containing it.

ptr_symbol

    A space separated list of p_cnt different types of pointers that lemma has in all synsets containing it. See above for a list of pointers.

sense_cnt

    Same as sense_cnt above. This is redundant, but the field was preserved for compatibility reasons.

tagsense_cnt

    Number of senses of lemma that are ranked according to their frequency of occurrence in semantic concordance texts.

synset_offset

    Byte offset in data.pos file of a synset containing lemma.
