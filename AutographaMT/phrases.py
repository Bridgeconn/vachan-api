import psycopg2, re
import spacy
from spacy.matcher import Matcher
from gensim.models.phrases import Phrases

# the puctuations that are remved from text for getting a clean text
# "-" is left out intentionally in this list because, it is ofter used in text to show compund words
non_letters = [',', '"', '!', '.', '\n', '\\','“','”','“','*','।','?',';',"'","’","(",")","‘","—"]
non_letter_pattern = re.compile(r'['+''.join(non_letters)+']')
multi_space_pattern = re.compile(r'\s\s+')

# the stop words are functional words in Hindi, which are treated separately while generating phrases
hi_stop_words = [ "ओर", "कर", "करके", "करता", "करते", "करना", "करने", "करे", "करें", "करेगा", "करो", 
			  "का", "कि", "किया", "किस", "किसी", "की", "के", "को",  "तो", "था", "थी", "थे", "ने", "पर"
			  "भी", "में", "रहा", "रहे", "रहो", "से", "हर", "ही", "हुआ", "हुई", "हुए", "हुओं", "हूँ", "हे"
			  "है", "हैं", "हो", "होकर", "होगा", "होता", "होने" ]

def phrase_rank(phrase_freq,word_freqs):
	score = phrase_freq*len(word_freqs)*100
	for f in word_freqs:
		score /= (f/10)
	return score

def cleanNsplit(sent):
	try:
		sent = re.sub(non_letter_pattern," ",sent)
		sent = re.sub(multi_space_pattern," ",sent)
		sent = sent.strip()
		sent = sent.split(' ')
		
	except Exception as e:
		print('sent:',sent)
		raise e
	return sent


def train_bigram_gensimmodel(sentence_stream,stop_words):
	bigram_phrase_model = Phrases(sentence_stream, common_terms=frozenset(stop_words), min_count=5	, threshold=10)
	return bigram_phrase_model
def train_trigram_gensimmodel(sentence_stream,stop_words):
	bigram_phrase_model = train_bigram_gensimmodel(sentence_stream,stop_words)
	trigram_phrase_model = Phrases(bigram_phrase_model[sentence_stream], common_terms=frozenset(stop_words), min_count=3, threshold=10)
	return trigram_phrase_model
def gensimphrases_dict(model,sentence_stream):
	phrase_list = {}
	for phrase, score in model.export_phrases(sentence_stream):
		if phrase not in phrase_list:
			phrase = phrase.decode("utf-8")
			phrase_list[phrase] = {'freq' : 1, 'score':score}
		else:
			phrase_list[phrase]['freq'] += 1
	return phrase_list    


def extract_phrases_gensim(conn,lang,version):
	source_table = lang+'_'+version+'_bible_cleaned'

	cursor = conn.cursor()
	cursor.execute("select lid, verse from " + source_table + " order by lid;")
	verses = cursor.fetchall()
	text = [cleanNsplit(v[1])for v in verses]

	if lang == "hi" or lang == "hin":
		stop_words = hi_stop_words
	else:
		stop_words = []

	model = train_trigram_gensimmodel(text,stop_words)
	phrases = gensimphrases_dict(model,text)
	return phrases




def get_bigrams(sent):
	bigrams = []
	for i in range(len(sent)-1):
		bigrams.append((sent[i],sent[i+1]))
	return bigrams  
def get_trigrams(sent):
	trigrams = []
	for i in range(len(sent)-2):
		trigrams.append((sent[i],sent[i+1],sent[i+2]))
	return trigrams  
def ngramphrases_dict(sent_stream, word_dict):
	phrase_list = {}
	for verse in sent_stream:
		bigrams_in_verse = get_bigrams(verse)
		trigrams_in_verse = get_trigrams(verse)
		for bigram in bigrams_in_verse:
			if bigram in phrase_list:
				phrase_list[bigram] +=1
			else:
				phrase_list[bigram] = 1
		for trigram in trigrams_in_verse:
			if trigram in phrase_list:
				phrase_list[trigram] +=1
			else:
				phrase_list[trigram] = 1
	sorted_phrase_list = {k: phrase_list[k] for k in sorted(phrase_list, key=phrase_list.get, reverse=True)}

	phrase_score_dict = {" ".join(list(ph)):{'freq':phrase_list[ph],'score':phrase_rank(phrase_list[ph],[word_dict[w] for w in ph])} for ph in phrase_list}
	return phrase_score_dict



def extract_phrases_naivestat(conn,lang,version):
	source_table = lang+'_'+version+'_bible_cleaned'

	cursor = conn.cursor()
	cursor.execute("select lid, verse from " + source_table + " order by lid;")
	verses = cursor.fetchall()
	text = [cleanNsplit(v[1])for v in verses]

	word_dict = uniquewords_freq_dict(text)
	phrases = ngramphrases_dict(text,word_dict)
	return phrases







def add_rules_toDB(conn,lang,input_file):
	rules_table = lang+'_phrase_rules'
	cursor = conn.cursor()

	cursor.execute("select exists (select * from information_schema.tables where table_name= '" + rules_table + "')")
	tableExists = cursor.fetchone()[0]

	print('checking table')
	if not tableExists:
		cursor.execute("CREATE TABLE "+rules_table+"(ID INT NOT NUll, Rule TEXT NOT NULL)")
		conn.commit()
	else:
		print('table found')
		cursor.execute("DELETE FROM "+rules_table+";")
		print('truncated '+rules_table)
		conn.commit()

	with open(input_file,'r') as infile:
		for i,line in enumerate(infile):
			cursor.execute("INSERT INTO "+rules_table+" VALUES(%s,%s)",(i,line))
		conn.commit()




def get_spacyphrases(verse,nlp,matcher):
	doc = nlp(verse)
	matches = matcher(doc)
	phrases = []
	for match in matches:
		phrases.append(doc[match[1]:match[2]].text)
	return phrases

def spacyphrases_dict(sent_stream,nlp,matcher,word_dict):
	phrase_list = {}
	# for verse in sent_stream:
		# phrases_in_verse = get_spacyphrases(verse,nlp,matcher)
		# for phrase in phrases_in_verse:
	batches = [ ]
	for x in range(int(len(sent_stream)/5000)-1):
		batches.append(" ".join(sent_stream[x*5000:x*5000+5000]))
	batches.append(" ".join(sent_stream[-5000:]))
	for batch in batches:
		phrases_in_batch = get_spacyphrases(batch,nlp,matcher)
		for phrase in phrases_in_batch:
			if phrase in phrase_list:
				phrase_list[phrase] +=1
			else:
				phrase_list[phrase] = 1
	print('obtained phrases... now sorting and scoring them')
	sorted_phrase_list = {k: phrase_list[k] for k in sorted(phrase_list, key=phrase_list.get, reverse=True)}
	try:
		phrase_score_dict = {ph:{
						'freq':sorted_phrase_list[ph],
						'score':phrase_rank(sorted_phrase_list[ph],[word_dict[w] for w in ph.split(" ")])} 
						for ph in sorted_phrase_list }
		# pass
	except Exception as e:
		# print(sorted_phrase_list:,sorted_phrase_list)
		print('ph:',ph)
		raise e
	return phrase_score_dict

def uniquewords_freq_dict(sent_stream):
	word_list = {}

	for verse in sent_stream:
		for w in verse:
			if w in word_list:
				word_list[w] += 1
			else:
				word_list[w] = 1
	sorted_word_list = {k:word_list[k] for k in sorted(word_list,key=word_list.get,reverse=True)}
	return sorted_word_list

def extract_phrases_rulebased(conn,lang,version,start=None,end=None):
	source_table = lang+'_'+version+'_bible_cleaned'
	rules_table = lang+'_phrase_rules'

	cursor = conn.cursor()

	cursor.execute("select exists (select * from information_schema.tables where table_name= '" + rules_table + "')")
	tableExists = cursor.fetchone()[0]

	if not tableExists:
		print("!!!No Rules found in DB! Falls back to Gensim tokenizer")
		phrases = extract_phrases_gensim(conn,lang,version)
	else:
		nlp = spacy.load('models/model-final')
		matcher = Matcher(nlp.vocab)

		cursor.execute("SELECT ID,Rule from "+rules_table+" order by ID;")
		rules = cursor.fetchall()

		for row in rules:
			rul = eval(row[1])
			matcher.add('rule'+str(row[0]),None,rul)

		if start and end:
			cursor.execute("select lid, verse from " + source_table + " where lid>="+str(start)+" and lid<="+str(end)+" order by lid;")
		else:
			cursor.execute("select lid, verse from " + source_table + " order by lid;")
		verses = cursor.fetchall()
		text = [' '.join(cleanNsplit(v[1])) for v in verses]
		word_split_text = [cleanNsplit(v[1]) for v in verses]

		word_dict = uniquewords_freq_dict(word_split_text)
		phrases = spacyphrases_dict(text,nlp,matcher,word_dict)
	return phrases


book_id_lid_map = {
1: {"start":1	,	"end":1533	},
2: {"start":1534	,	"end":2746	},
3: {"start":2747	,	"end":3605	},
4: {"start":3606	,	"end":4893	},
5: {"start":4894	,	"end":5852	},
6: {"start":5853	,	"end":6510	},
7: {"start":6511	,	"end":7128	},
8: {"start":7129	,	"end":7213	},
9: {"start":7214	,	"end":8023	},
10: {"start":8024	,	"end":8718	},
11: {"start":8719	,	"end":9534	},
12: {"start":9535	,	"end":10253	},
13: {"start":10254	,	"end":11195	},
14: {"start":11196	,	"end":12017	},
15: {"start":12018	,	"end":12297	},
16: {"start":12298	,	"end":12703	},
17: {"start":12704	,	"end":12870	},
18: {"start":12871	,	"end":13940	},
19: {"start":13941	,	"end":16580	},
20: {"start":16581	,	"end":17332	},
21: {"start":17333	,	"end":17538	},
22: {"start":17539	,	"end":17675	},
23: {"start":17676	,	"end":18947	},
24: {"start":18948	,	"end":20345	},
25: {"start":20346	,	"end":20465	},
26: {"start":20466	,	"end":21738	},
27: {"start":21739	,	"end":22095	},
28: {"start":22096	,	"end":22451	},
30: {"start":22452	,	"end":22512	},
31: {"start":22513	,	"end":22532	},
32: {"start":22533	,	"end":22580	},
33: {"start":22581	,	"end":22698	},
34: {"start":22699	,	"end":22743	},
35: {"start":22744	,	"end":22788	},
36: {"start":22789	,	"end":22843	},
37: {"start":22844	,	"end":22887	},
38: {"start":22888	,	"end":23093	},
39: {"start":23094	,	"end":23145	},
40: {"start":23146 ,"end":24216 },
41: {"start":24217 ,"end":24894 },
42: {"start":24895 ,"end":26045 },
43: {"start":26046 ,"end":26924 },
44: {"start":26925 ,"end":27931 },
45: {"start":27932 ,"end":28364 },
46: {"start":28365 ,"end":28801 },
47: {"start":28802 ,"end":29058 },
48: {"start":29059 ,"end":29207 },
49: {"start":29208 ,"end":29362 },
50: {"start":29363 ,"end":29466 },
51: {"start":29467 ,"end":29561 },
52: {"start":29562 ,"end":29650 },
53: {"start":29651 ,"end":29697 },
54: {"start":29698 ,"end":29810 },
55: {"start":29811 ,"end":29893 },
56: {"start":29894 ,"end":29939 },
57: {"start":29940 ,"end":29964 },
58: {"start":29965 ,"end":30267 },
59: {"start":30268 ,"end":30375 },
60: {"start":30376 ,"end":30480 },
61: {"start":30481 ,"end":30541 },
62: {"start":30542 ,"end":30646 },
63: {"start":30647 ,"end":30659 },
64: {"start":30660 ,"end":30673 },
65: {"start":30674 ,"end":30698 },
66: {"start":30699 ,"end":31102 }}




def tokenize(conn,lang,version,book_id,algo='gensim-ngram'):
	start_lid = book_id_lid_map[book_id]['start']
	end_lid = book_id_lid_map[book_id]['end']
	if (algo == 'gensim'):
		phrases = extract_phrases_gensim(conn,lang,version)
	elif( algo == 'ngram'):
		phrases = extract_phrases_naivestat(conn,lang,version)
		# print(phrases.keys())
		# return
	elif( algo == 'rule-based'):
		phrases = extract_phrases_rulebased(conn,lang,version,start=start_lid,end=end_lid)
	elif( algo == 'single-word'):
		phrases = {}
	elif ( algo == 'gensim-ngram'):
		phrases = extract_phrases_gensim(conn,lang,version)
		phrases2 = extract_phrases_naivestat(conn,lang,version)
		for i,ph in enumerate(phrases2):
			if ph not in phrases:
				phrases[ph] = phrases2[ph]
			if i > 250:
				break


	
	# lid_book_map = load_book_lid_map(conn)
	cursor = conn.cursor()
	tw_table = lang+'_tw'
	cursor.execute("select exists (select * from information_schema.tables where table_name= '" + tw_table + "')")
	tableExists = cursor.fetchone()[0]
	if tableExists:
		cursor.execute('select wordforms from '+tw_table+' order by id;')
	tws = []
	for row in cursor.fetchall():
		wordforms = [x.strip() for x in row[0].split(',')]
		tws += wordforms
	
	for ph in tws:
		if ph not in phrases:
			phrases[ph] = {'freq':None,'score':None}

	source_table = lang+'_'+version+'_bible_cleaned'
	if start_lid and end_lid:
		query = "select lid, verse from " + source_table + " where lid>="+str(start_lid)+" and lid<="+str(end_lid)+" order by lid;"
	else:
		query = "select lid, verse from " + source_table + " order by lid;"
	cursor.execute(query)
	rows = cursor.fetchall()
	verses = [(r[0],cleanNsplit(r[1])) for r in rows]

	token_table =lang+'_'+version+'_bible_tokens'
	cursor.execute("select exists (select * from information_schema.tables where table_name= '" + token_table + "')")
	tableExists = cursor.fetchone()[0]

	if not tableExists:
		cursor.execute("CREATE TABLE "+token_table+"(book_id INT NOT NUll, token TEXT NOT NULL)")
		conn.commit()
	else:
		# in the assumption that tokenization would always be done for one book at a time
		cursor.execute("DELETE FROM "+token_table+" WHERE book_id="+str(book_id)+" ;")
		conn.commit()		

	tokens = []
	for row in verses:
		lid = row[0]
		word_split_text = row[1]
		N = len(word_split_text)
		taken = [False for i in range(N)]
		for n in range(N,1,-1):
			for i in range(N-n+1):
				chunk = word_split_text[i:i+n]
				if ' '.join(chunk) in phrases:
					taken_check = False
					for index in range(i,i+n):
						if taken[index]:
							taken_check = True
							break
					if taken_check == False:
						for index in range(i,i+n):
							taken[index] = True
						phrase = ' '.join(word_split_text[i:i+n])
						if phrase not in tokens: 
							tokens.append(phrase)
		for i,flag in enumerate(taken):
			if not flag:
				word_token = word_split_text[i]
				if word_token not in stop_words and word_token not in tokens:
					tokens.append(word_token)

	tokens = sorted(tokens)
	for tok in tokens:
		cursor.execute("INSERT INTO "+token_table+" VALUES(%s,%s)",(book_id,tok))
		# print(tok)
	conn.commit()
	cursor.close()




if __name__ == '__main__':
	db = psycopg2.connect(dbname='mt2414_local', user='postgres', password='password', host='localhost', port=5432)

	# tokenize(db,'hi','irv4',40,algo='gensim')
	# tokenize(db,'hi','irv4',40,algo='ngram')
	# tokenize(db,'hi','irv4',40,algo='rule-based')
	# tokenize(db,'hi','irv4',40,algo='single-word')
	tokenize(db,'hi','irv4',40,algo='gensim-ngram')

	# add_rules_toDB(db,"hi","rules_to_DB_draft2.txt")

	db.close()