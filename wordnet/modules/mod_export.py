
import cPickle as pickle
import pymongo

import mod_util

lexname_map = {
	'adj.all': '00',
	'adj.pert': '01',
	'adv.all': '02',
	'noun.Tops': '03',
	'noun.act': '04',
	'noun.animal': '05',
	'noun.artifact': '06',
	'noun.attribute': '07',
	'noun.body': '08',
	'noun.cognition': '09',
	'noun.communication': '10',
	'noun.event': '11',
	'noun.feeling': '12',
	'noun.food': '13',
	'noun.group': '14',
	'noun.location': '15',
	'noun.motive': '16',
	'noun.object': '17',
	'noun.person': '18',
	'noun.phenomenon': '19',
	'noun.plant': '20',
	'noun.possession': '21',
	'noun.process': '22',
	'noun.quantity': '23',
	'noun.relation': '24',
	'noun.shape': '25',
	'noun.state': '26',
	'noun.substance': '27',
	'noun.time': '28',
	'verb.body': '29',
	'verb.change': '30',
	'verb.cognition': '31',
	'verb.communication': '32',
	'verb.competition': '33',
	'verb.consumption': '34',
	'verb.contact': '35',
	'verb.creation': '36',
	'verb.emotion': '37',
	'verb.motion': '38',
	'verb.perception': '39',
	'verb.possession': '40',
	'verb.social': '41',
	'verb.stative': '42',
	'verb.weather': '43',
	'adj.ppl': '44'
}

pointers = {
	'!' : 'antonyms',
	'@' : 'hypernyms',
	'@i': 'instance_hypernyms',
	'~' : 'hyponyms',
	'~i': 'instance_hyponyms',
	'#m': 'member_holonyms',
	'#s': 'substance_holonyms',
	'#p': 'part_holonyms',
	'%m': 'member_meronyms',
	'%s': 'substance_meronyms',
	'%p': 'part_meronyms',
	'=' : 'attributes',
	'+' : 'drf',
	';c': 'topic_domains',
	'-c': 'members_of_topic_domain',
	';r': 'region_domains',
	'-r': 'members_of_region_domain',
	';u': 'usage_domains',
	'-u': 'members_of_usage_domain',

	'*' : 'entailments',
	'>' : 'causes',
	'^' : 'also_see',
	'$' : 'verb_groups',

	'&' : 'similar',
	'<' : 'praticiple_of_verb',
	'\\': 'pertainym',
}

index_pointer_mapper = {
	'!' : '!',
	'@' : '@',
	'@i': '@',
	'~' : '~',
	'~i': '~',
	'#m': '#m',
	'#s': '#s',
	'#p': '#p',
	'%m': '%m',
	'%s': '%s',
	'%p': '%p',
	'=' : '=',
	';c': ';',
	';r': ';',
	';u': ';',
	'-c': '-',
	'-r': '-',
	'-u': '-',
	'*' : '*',
	'>' : '>',
	'^' : '^',
	'$' : '$',
	'&' : '&',
	'<' : '<',
	'\\' : '\\',
}

#==================================================================================================

data_file_names = {
	'noun': 'data.noun',
	'verb': 'data.verb',
	'adj': 'data.adj',
	'adv': 'data.adv',
}

index_file_names = {
	'noun': 'index.noun',
	'verb': 'index.verb',
	'adj': 'index.adj',
	'adv': 'index.adv',
}

offset_mapper_names = {
	'noun': 'offset.noun.dict',
	'verb': 'offset.verb.dict',
	'adj': 'offset.adj.dict',
	'adv': 'offset.adv.dict',
}

#==================================================================================================

#==================================================================================================
def export(folder_name=None):
	import sys,os
	sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	import settings

	db = mod_util.connect_db(settings)
	synsets_db = db['synsets']

	print 'Connected'

	synset_nouns = list(synsets_db.find({'pos': 'n'}))
	synset_verbs = list(synsets_db.find({'pos': 'v'}))
	synset_adjs = list(synsets_db.find({'pos': {'$in': ['a', 's']}}))
	synset_advs = list(synsets_db.find({'pos': 'r'}))

	synset_nouns = sorted(synset_nouns, key=lambda k: k['offset'])
	synset_verbs = sorted(synset_verbs, key=lambda k: k['offset'])
	synset_adjs = sorted(synset_adjs, key=lambda k: k['offset'])
	synset_advs = sorted(synset_advs, key=lambda k: k['offset'])

	print 'Got Synsets'

	if not os.path.exists(folder_name):
		os.makedirs(folder_name)

	# Nouns
	noun_offset_mapper = make_offset_mapper(synset_nouns, file_name=os.path.join(folder_name, offset_mapper_names['noun']))
	export_pos(synset_nouns, os.path.join(folder_name, data_file_names['noun']), noun_offset_mapper)
	index_pos(synset_nouns, os.path.join(folder_name, index_file_names['noun']), noun_offset_mapper)
	# Verbs
	verb_offset_mapper = make_offset_mapper(synset_verbs, file_name=os.path.join(folder_name, offset_mapper_names['verb']))
	export_pos(synset_verbs, os.path.join(folder_name, data_file_names['verb']), verb_offset_mapper)
	index_pos(synset_verbs, os.path.join(folder_name, index_file_names['verb']), verb_offset_mapper)
	# Adj
	adj_offset_mapper = make_offset_mapper(synset_adjs, file_name=os.path.join(folder_name, offset_mapper_names['adj']))
	export_pos(synset_adjs, os.path.join(folder_name, data_file_names['adj']), adj_offset_mapper)
	index_pos(synset_adjs, os.path.join(folder_name, index_file_names['adj']), adj_offset_mapper)
	# Adv
	adv_offset_mapper = make_offset_mapper(synset_advs, file_name=os.path.join(folder_name, offset_mapper_names['adv']))
	export_pos(synset_advs, os.path.join(folder_name, data_file_names['adv']), adv_offset_mapper)
	index_pos(synset_advs, os.path.join(folder_name, index_file_names['adv']), adv_offset_mapper)

#--------------------------------------------------------------------------------------------------
def make_offset_mapper(synset_pos, file_name=None):
	offset_mapper = {}

	senses = {}
	offset = 0
	
	for synset in synset_pos:
		make_line = []
		make_line.append(str(offset).rjust(8, '0'))
		make_line.append(lexname_map[synset['lexname']])
		make_line.append(synset['pos'])

		offset_mapper[str(synset['offset']).rjust(8, '0')] = str(offset).rjust(8, '0')

		# Check if is translated
		lemma_names = []
		final_translation = None
		if synset['is_translated']:
			final_translation = synset['final_translation']
			lemma_names = final_translation['lemma_names']
		else:
			lemma_names = synset['lemma_names']
		
		make_line.append(str(hex(len(lemma_names)).split('x')[1]).rjust(2, '0'))
			
		for lemma in lemma_names:
			lemma_cnt = senses.get(lemma, 0)
			senses[lemma] = senses.get(lemma, 0) + 1

			lemma_cnt = str(hex(lemma_cnt).split('x')[1])

			make_line.append(lemma + ' ' + lemma_cnt)

		pnt_cnt = 0
		pnt = []
		for k, v in pointers.iteritems():
			if v in synset:
				pnt_cnt += len(synset[v])

				for pos, synset_offset in synset[v]:
					pnt.append(k + ' ' + str(synset_offset).rjust(8, '0') + ' ' + pos + ' 0000')

		make_line.append(str(pnt_cnt).rjust(3, '0'))
		make_line.append(' '.join(pnt))
		make_line.append('|')

		gloss = ''
		sentences = []
		# If is translated
		if final_translation:
			gloss = final_translation['gloss']
			if len(final_translation.get('sentences', [])) != 0:
				gloss = gloss + ';'
			sentences = final_translation.get('sentences', [])
		else:
			gloss = synset['gloss']
			if len(synset['sentences']) != 0:
				gloss = gloss + ';'
			sentences = synset['sentences']

		make_line.append(gloss)

		if sentences != []:
			make_line.append('"' + '"; "'.join(sentences) + '"')
		make_line.append(' ')

		try:
			example = ' '.join(make_line)
			example = example.encode('utf-8')
			offset += len(example) + 1
		except:
			print example, type(example), len(example.encode('utf-8'))

	pickle.dump(offset_mapper, open(file_name, 'w'), 2)
	return offset_mapper

#--------------------------------------------------------------------------------------------------
def export_pos(synset_pos, file_name=None, offset_mapper=None):
	''' Exports all nouns to nouns.data '''
	''' 
			Line Format:
				synset_offset  lex_filenum  ss_type  w_cnt  word  lex_id  [word  lex_id...]  p_cnt  [ptr...] |   gloss 
	'''
	file_content = []

	senses = {}
	for synset in synset_pos:
		make_line = []
		make_line.append(offset_mapper.get(str(synset['offset']).rjust(8, '0'), '00000001'))
		make_line.append(lexname_map[synset['lexname']])
		make_line.append(synset['pos'])

		# Check if is translated
		lemma_names = []
		final_translation = None
		if synset['is_translated']:
			final_translation = synset['final_translation']
			lemma_names = final_translation['lemma_names']
		else:
			lemma_names = synset['lemma_names']
		
		make_line.append(str(hex(len(lemma_names)).split('x')[1]).rjust(2, '0'))
			
		for lemma in lemma_names:
			lemma_cnt = senses.get(lemma, 0)
			senses[lemma] = senses.get(lemma, 0) + 1

			lemma_cnt = str(hex(lemma_cnt).split('x')[1])

			make_line.append(lemma + ' ' + lemma_cnt)

		pnt_cnt = 0
		pnt = []
		for k, v in pointers.iteritems():
			if v in synset:
				pnt_cnt += len(synset[v])

				for pos, synset_offset in synset[v]:
					pnt.append(k + ' ' + offset_mapper.get(str(synset_offset).rjust(8, '0'), '00000001') + ' ' + pos + ' 0000')

		make_line.append(str(pnt_cnt).rjust(3, '0'))
		make_line.append(' '.join(pnt))
		make_line.append('|')

		gloss = ''
		sentences = []
		# If is translated
		if final_translation:
			gloss = final_translation['gloss']
			if len(final_translation.get('sentences', [])) != 0:
				gloss = gloss + ';'
			sentences = final_translation.get('sentences', [])
		else:
			gloss = synset['gloss']
			if len(synset['sentences']) != 0:
				gloss = gloss + ';'
			sentences = synset['sentences']

		make_line.append(gloss)

		if sentences != []:
			make_line.append('"' + '"; "'.join(sentences) + '"')
		make_line.append(' ')

		file_content.append(make_line)

	writer = open(file_name, 'w')

	for line in file_content:
		writer.write(' '.join(line).encode('utf-8'))
		writer.write('\n')

	writer.close()
	
	return file_content

#--------------------------------------------------------------------------------------------------
def index_pos(synset_pos, file_name=None, offset_mapper=None):
	''' Index all nouns to nouns.index '''
	'''
			Line format:
				lemma  pos  synset_cnt  p_cnt  [ptr_symbol...]  sense_cnt  tagsense_cnt   synset_offset  [synset_offset...] 
	'''
	file_content = []

	senses = {}
	for synset in synset_pos:
		offset = offset_mapper.get(str(synset['offset']).rjust(8, '0'), '00000001')
		pos = synset['pos']

		if pos == 's':
			pos = 'a'

		# Check if translated
		lemma_names = []
		final_translation = None
		if synset['is_translated']:
			final_translation = synset['final_translation']
			lemma_names = final_translation['lemma_names']
		else:
			lemma_names = synset['lemma_names']

		ptr_symbol = set()
		for k, v in pointers.iteritems():
			if v in synset:
				ptr_symbol.add(index_pointer_mapper[k])

		for lemma in lemma_names:
			lemma = lemma.lower()
			if lemma in senses:
				senses[lemma]['synset_cnt'] = senses[lemma].get('synset_cnt', 0) + 1
				senses[lemma]['ptr_symbol'] |= ptr_symbol
				senses[lemma]['synset_offset'].append(offset)
			else:
				senses[lemma] = {
					'pos': pos,
					'synset_cnt': 1,
					'ptr_symbol': ptr_symbol,
					'synset_offset': [offset],
				}

	for lemma, lemma_info in sorted(senses.items(), key=lambda k: k):
		make_line = []

		make_line.append(lemma)
		make_line.append(lemma_info['pos'])
		make_line.append(str(lemma_info['synset_cnt']))
		make_line.append(str(len(lemma_info['ptr_symbol'])))
		make_line.append(' '.join(lemma_info['ptr_symbol']))
		make_line.append(str(lemma_info['synset_cnt']))
		make_line.append('0')
		synset_offsets = sorted(lemma_info['synset_offset'], reverse=True)
		make_line.append(' '.join(synset_offsets))
		make_line.append(' ')

		file_content.append(make_line)
	
	writer = open(file_name, 'w')

	for line in file_content:
		writer.write(' '.join(line).encode('utf-8'))
		writer.write('\n')

	writer.close()

	return file_content

#==================================================================================================

if __name__=='__main__':
	export('Wordnet.V.1')