# ACE-Annotated Corpora for online Exercises 

This project aims at generating self-correcting exercises and activities based on annotated corpora. The target platform is Moodle, for the moment. The target language is French.

Here, you will find the following elements:
  - a processing chain, in python, to generate Moodle quizzes based on CONLL-U annotations
  - a set of quizzes, in the GIFT format, that can be integrated into a Moodle "question bank"
  - a set of H5P and Hot Potatoes activities and templates, that can be integrated into a Moodle course, or reused elsewhere

## Corpus2Quiz processing chain: from corpus to quiz

The script takes as input a CONLL-U formatted corpus and generates part-of-speech quizzes based on the following parameters: 
  - questionTemplate: a template in markdown that will be used as a header for each question
  - suffixFilter: a regex filter on the desired suffix (eg.: nouns in -ment)
  - lemmaSuffix: if defined, applies the suffix filter
  - conlluField: which part-of-speech set to use
  - moodleCategory: a basic Moodle category header
  - table: a conversion table to transpose parts-of-speech used in annotated corpora into student-friendly names

## H5P/Hot Potatoes activities and templates to be used to generate new sets of exercises based on the Corpus2Quiz processing chain
  - H5P "mark the words" template 
  - Hot Potatoes "mark the words" and "categorize" templates
