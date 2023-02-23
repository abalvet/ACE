import configparser
import argparse
from conllu import parse #pip3 install conllu
from io import open
from random import shuffle
import re
import sys#AB:pour afficher sur STD ERR

# Moodle : https://docs.moodle.org/400/en/GIFT_format
# https://stackoverflow.com/questions/64362772/switching-python-version-installed-by-homebrew

connlTagset = {}
connlTagset["xpos"] = "ADJ ADJWH ADV ADVWH CC CLO CLR CLS CS DET DETWH ET I NC NPP P P+D P+PRO PREF PRO PROREL PROWH V VIMP VINF VPP VPR VS".split(" ");
#connlTagset_upos  = "ADJ ADP ADV AUX CCONJ DET INTJ NOUN NUM PART PRON PROPN PUNCT SCONJ SYM VERB X".split(" "); #https://www.sketchengine.eu/tagsets/universal-pos-tags/
connlTagset["upos"]  = "P V D N P+D C CL PONCT PRO A ADV ET".split(" ");

# Pas de support English pour le moment
connlTagset_EN = "ADJ ADP AUX CD DT DET HYPH IN JJ MD NN NNS NNP NOUN NUM PART PRON PROPN PRP PUNCT RP SCONJ TO VB VBD VBG VBN VBZ VERB - : , . -LRB- -RRB-".split(" ");

output = sys.stdout;




questionTemplate = ":: Parties du Discours ::[markdown]   Donner la partie du discours du mot **{}** dans la phrase:"
posfield = "upos" # choix du jeu d'étiquettes
maxchoix = 9
etiquettesAcceptees = {}
tagMap = {}
for t in connlTagset[posfield]:
	#par défaut : identité
	tagMap[t]=t


parser = argparse.ArgumentParser( prog = 'pos_qgen',
                    description = "Génération de quizz sur les parties du discours au format GIFT-Moodle à partir d'un fichier CoNNL-U",
                    epilog = 'Exemple : python3 pos_qgen.py test.conll --table tagmap.txt --filtre "C Y N" --maxchoix 2 --categorie "Test/partie 1"')
parser.add_argument("fichier", help="Fichier au format CoNNL-U")
parser.add_argument("-k", "--konfig", dest="konfigFile", help="Utilisation d'un fichier de configuration : -k params.ini")
parser.add_argument("-f", "--filtre", dest="posFilter", help="Filtre inclusif sur les parties du discours à cibler. Si --table est actif le filtre est défini sur les étiquettes cibles. Exemple : -f filtre.txt")
parser.add_argument("-i", "--inline", dest="inline", action="store_true", help='A utiliser en combinaison avec -f : permet de déclarer le filtre sur la ligne de commande, exemple -f "ADV V" -i')
parser.add_argument("-t", "--table", dest="table", help="Table de normalisation des étiquettes des parties du discours")
parser.add_argument("-p", "--champ", dest="posfield", help="Champ utilisé pour la partie du discours : valeurs habituelles : xpos, upos")
parser.add_argument("-m", "--maxchoix", default=9, type=int, dest="maxchoix", help="Nombre de choix maximum par question, en excluant la bonne réponse. Si maxchoix=1 alors il y aura 2 réponses possibles, dont la bonne.")
parser.add_argument("-q", "--question", dest="questionTemplate", help="Modèle de la question du quizz au format markdown. Valeur par défaut :\n :: Parties du Discours ::[markdown]   Donner la partie du discours du mot **{}** dans la phrase:")
parser.add_argument("-c", "--categorie", dest="moodleCategory", help="Catégorie ciblée dans le cours Moodle. Exemple : cat ou cat/subcat/subsubcat")
parser.add_argument("-s", "--suffixe", dest="suffixe", help="Filtrage simple sur le suffixe de la graphie non lemmatisée: exemple : -s ment")
parser.add_argument("-l", "--lemme", action="store_true", help="Combinable avec --suffixe : filtrage simple sur le suffixe du lemme: exemple : -s ment -l ")
parser.add_argument("-o", "--output", dest="outputFile", help="Ecrire dans un fichier plutôt que sur la sortie standard")
args = parser.parse_args()


if(args.konfigFile):
	# Les paramètres sont lus dans un fichier externe plutôt qu'en ligne de commande
	config = configparser.ConfigParser()
	config.read(args.konfigFile)

	sections = config.sections()
	
	if('PARAMS' in config):
		if(config.has_option("PARAMS", "conllufield")):
			posfield = config.get('PARAMS', 'conllufield')
			for t in connlTagset[posfield]:
				tagMap[t]=t

		if(config.has_option("PARAMS", "maxchoix")):
			maxchoix = int(config.get('PARAMS','maxchoix'))
			maxchoix = min(maxchoix,9)
		
		if(config.has_option("PARAMS", "questiontemplate")):
			questionTemplate = config.get('PARAMS','questiontemplate')

		if(config.has_option("PARAMS", "suffixefilter")):
			args.suffixe = config.get('PARAMS','suffixefilter')

		if(config.has_option("PARAMS", "lemmesuffixe")):
			args.lemme =  config.getboolean('PARAMS','lemmesuffixe')

		if(config.has_option("PARAMS", "moodlecategory")):
			args.moodleCategory = config.get('PARAMS','moodlecategory')

		if(config.has_option("PARAMS", "table")):
			mapStr = config.get('PARAMS','table')
			lines = mapStr.split("\n")
			for line in lines :
				pair = line.split(":")
				tagMap[pair[0]]=pair[1].strip()

		if(config.has_option("PARAMS", "filtre")):
			mapStr = config.get('PARAMS','filtre')
			retenir = mapStr.split(" ")
			for t in retenir:
				etiquettesAcceptees[t]=1

else:
	if(args.questionTemplate):
		questionTemplate = args.questionTemplate

	if(args.posfield):
		posfield = args.posfield
		for t in connlTagset[posfield]:
			tagMap[t]=t

	if(args.maxchoix):
		maxchoix = min(args.maxchoix,9) # Dans moodle, un maximum de 10 choix (9+1 bonne réponse)

	if(args.table):
		# Lecture fichier d'équivalence des étiquettes, une par ligne :  conllutag \t targettag
		mapFile = open(args.table, "r", encoding="utf-8")
		for line in mapFile:
			pair = line[:-1].split(":")
			tagMap[pair[0]]=pair[1].strip()
		mapFile.close()

	if(args.posFilter):
		if(args.inline):
			retenir = args.posFilter.split(" ")
			for t in retenir:
				etiquettesAcceptees[t]=1
		else:
			filterFile = open(args.posFilter, "r", encoding="utf-8")
			buf = filterFile.read()
			filterFile.close()
			itags = re.split('\s+',buf)
			for t in itags:
				etiquettesAcceptees[t]=1


if(args.outputFile):
		output = open(args.outputFile, "w", encoding="utf-8")

# Etape 1 : Charger tout l'échantillon CoNNL-U (On suppose qu'il contient les phrases que l'on souhaite traiter)

connlFile = open(args.fichier, "r", encoding="utf-8")
connlData = connlFile.read()
connlFile.close()
sentences = parse(connlData)


if(args.moodleCategory):
	print("$CATEGORY: " + args.moodleCategory, file=output)

# Etape 2 : Pour chaque phrase, générer autant d'exercices de QCM de choix de la bonne partie du discours en tenant compte du filtre optionnel
# La ponctuation est exclue
nbQuestions = 0#AB:compte le nb de questions générées
for sent in sentences:
		punctIdx = []
		# Parcours de la phrase
		for i in range(0,len(sent)):
			if(len(etiquettesAcceptees)>0):
				checkTag = tagMap[sent[i][posfield]]
				if(checkTag not in etiquettesAcceptees):
					continue
			if(args.suffixe):
				if(args.lemme):
					if(not sent[i]["lemma"].endswith(args.suffixe)):
						continue
				else:
					if(not sent[i]["form"].endswith(args.suffixe)):
						continue
			if(re.match("[\!\?,,\.;\/:#&\"\)\(\-\]\[]", sent[i]["form"])):
				punctIdx.append(i)
				continue
			question = questionTemplate.format(sent[i]["form"])
			nbQuestions = nbQuestions + 1
			print(question, file=output)
			# Assemblage de la phrase
			answer = "";
			for idx in range(0,len(sent)):
				
				# Il y a deux cas pour lesquels on ne souhaite pas ajouter un espace après une graphie : 
				# a)Cette graphie se termine par une apostrophe. Exemple : d'habitude 
				# b)La graphie suivante est une ponctuation
				insererEspace = True
				if(idx+1<len(sent)):
					if(re.match("[\!\?,,\.;\/:#&\"\)\(\-\]\[]", sent[idx+1]["form"])):
						insererEspace=False
					else:
						if(sent[idx]["form"].endswith("'")):
							insererEspace=False
				
				if(idx==i):
					print("**{}**".format(sent[idx]["form"]), end="", file=output)
					answer = sent[idx][posfield]
				else:
					print(sent[idx]["form"], end="", file=output)
					
				if(insererEspace):	print(" ", end="", file=output)

			print("\n{", file=output)
			# assemblage des choix multiples
			answers = [];
			for t in connlTagset[posfield]:
				s = "\t~"+tagMap[t]
				deja = 0
				try:
					if(answers.index(s)>=0):
						deja=1
				except:
					pass
				if(t!=answer and deja==0):
					answers.append(s)
			shuffle(connlTagset[posfield])
			answers = answers[:maxchoix]; # max 9+1=10 réponses dans Moodle
			answers.append("\t="+tagMap[answer])
			shuffle(answers)
			for r in answers:
				print(r, file=output)
			print("}\n\n", file=output)

if(args.outputFile):
	output.close()
#AB:Afficher le nb de questions générées
sys.stderr.write('Nb Questions: ' + str(nbQuestions) + "\n")			