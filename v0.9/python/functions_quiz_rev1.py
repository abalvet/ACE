import pyconll
import pyconll.util
import argparse
import re
import sys
from random import shuffle
import os


#TODO: make this script way better: check whether output **tokens** are duplicated (eg. "**nous** **nous** demandons", "**en** **en** parlant")
#TODO: for iobj (pronouns) in French: restrict questions to indirect object pronouons: "me, te, lui, nous, vous, leur, se" + "en, y, dont", and discard cases like "où" (rel. pron.), "ce", "pron-même"
#TODO: for obl:arg, restrict questions to indirect objects which depend on a verbal root (no adjectives as controllers)

parser = argparse.ArgumentParser(
                    prog = 'functions_quiz_generator',
                    description = 'This program generates a Moodle quiz formatted in GIFT, based on a dependency-annotated corpus in CONNL-U format.',
                    epilog = 'python3 script [file] [dependency_relation]')

parser.add_argument("-f", "--file", dest="file", help="CoNNL-U formatted file", required=True)
parser.add_argument("-d", "--deprel", dest="deprel", help="dependency relation to use (eg.: obj, iobj, obl:arg, nmod...)", required=True)
parser.add_argument("-n", "--number-of-distractors",default=5, type=int, dest="nbDistractors", help="number of distractors for each question", required=True)


args = parser.parse_args()

head, tail = os.path.split(args.file)
corpus = pyconll.load_from_file(args.file)




functions = []
functions  = "acl acl:rel advcl advcl:cleft advmod appos ccomp cop csubj csubj:pass dep dep:comp iobj iobj:agent nmod nsubj nsubj:caus nsubj:pass nummod obj obj:agent obj:lvc obl obl:agent obl:arg root xcomp".split(" ");

reduced_functions  = "advmod ccomp csubj dep iobj iobj:agent nmod nsubj obj obj:agent obl:agent obl:arg obl:mod".split(" ");

functionCorrespondence = {'advmod': 'MOD:adv', 'ccomp': 'COD:sub', 'csubj': 'SUJ:sub', 'dep': 'DEP', 'iobj': 'COI:pron', 'iobj:agent': 'AGT', 'nmod': 'MOD:nom', 'nsubj': 'SUJ', 'obj': 'COD', 'obj:agent':'AGT', 'obl:agent':'AGT', 'obl:arg': 'COI', 'obl:mod': 'MOD:prép'}


questionTemplate = "\n:: Fonctions ::[markdown]   Donner la fonction de l'élément figurant en gras, dans la phrase:"


match_sentences = []
matches = []


sys.stderr.write("corpus: " + tail + "\n")

nb_questions = 0

for sentence in corpus:
    distractors = []


    for token in sentence:

        if token.deprel == args.deprel:
            shuffle(reduced_functions)
            distractors = reduced_functions

            shuffle(distractors)
            final_distractors = distractors[0:args.nbDistractors]
            final_distractors.append(args.deprel)

        

            output = []


            print(questionTemplate)

            for t in sentence:
                if(t.form == token.form):#if current token is the match
                    output.append("**" + t.form + "**")#surround token with ** (bold)
                    #TODO: restrict **x** to the token that matches the target deprel
                else:
                    output.append(t.form)#else just add the token        


            out = ' '.join(output)
            #renormalize agglomerated tokens
            out = re.sub("au à le", "au", out)
            out = re.sub("aux à les", "aux", out)
            out = re.sub("du de le", "du", out)                                    
            out = re.sub("des de les", "des", out)
          
            print(out)                    

            corr = []
            print("{")#set up quiz question    
            shuffle(final_distractors)
            
            for d in final_distractors:
                if(d != args.deprel):#if this is a distractor
                    corr.append("~" + functionCorrespondence[d])#mark it so moodle knows it is a distractor
     
                if(d == args.deprel):#if this is the correct answer
                    corr.append("=" + functionCorrespondence[d])#mark it so moodle knows it is the correct answer


            set_out = set(corr)
            for e in set_out:
                print(e)



            nb_questions += 1                                 
            print("}")            
                

sys.stderr.write("nb of questions: " + str(nb_questions) + "\n")

