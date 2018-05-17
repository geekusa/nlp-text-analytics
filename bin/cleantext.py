#!/opt/splunk/bin/python

#from splunklib.searchcommands import *
#import sys
#import csv

#from __future__ import absolute_import, division, print_function, unicode_literals
#import app
#import logging
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators
import sys
import re
import os
#import nltk
from nltk import word_tokenize, pos_tag
from nltk.data import path as nltk_data_path
from nltk.corpus import wordnet, stopwords as stop_words
from nltk.stem import WordNetLemmatizer, PorterStemmer
from splunklib import six
from string import punctuation, digits, maketrans
from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path

#logger = logging.getLogger('splunk')

BASE_DIR = make_splunkhome_path(["etc","apps","nlp-text-analytics"])
CORPORA_DIR = os.path.join(BASE_DIR,'bin','nltk_data')
nltk_data_path.append(CORPORA_DIR)


@Configuration()
class CleanText(StreamingCommand):
    """ Counts the number of non-overlapping matches to a regular expression in a set of fields.

    ##Syntax

    .. code-block::
        cleantext lowercase=<boolean> pattern=<regular_expression> <field-list>

    ##Description

    A count of the number of non-overlapping matches to the regular expression specified by `pattern` is computed for
    each record processed. The result is stored in the field specified by `fieldname`. If `fieldname` exists, its value
    is replaced. If `fieldname` does not exist, it is created. Event records are otherwise passed through to the next
    pipeline processor unmodified.

    ##Example

    Count the number of words in the `text` of each tweet in tweets.csv and store the result in `word_count`.

    .. code-block::
        | inputlookup tweets | countmatches fieldname=word_count pattern="\\w+" text
    """

    textfield = Option(
        require=True,
        doc='''
        **Syntax:** **textfield=***<fieldname>*
        **Description:** Name of the field that will contain the text to search against''',
        validate=validators.Fieldname())
    default_clean = Option(
        default=True,
        doc='''**Syntax:** **lowercase=***<boolean>*
        **Description:** Change text to lowercase, remove punctuation, and removed numbers, defaults to true''',
        validate=validators.Boolean()
        ) 	
    remove_urls = Option(
        default=True,
        doc='''**Syntax:** **remove_punct=***<boolean>*
        **Description:** Remove html links as part of text cleaning, defaults to true''',
        validate=validators.Boolean()
        ) 	
    remove_stopwords = Option(
        default=True,
        doc='''**Syntax:** **remove_punct=***<boolean>*
        **Description:** Remove stopwords as part of text cleaning, defaults to true''',
        validate=validators.Boolean()
        ) 	
    base_word = Option(
        default=True,
        doc='''**Syntax:** **remove_punct=***<boolean>*
        **Description:** Convert words to a base form as part of text cleaning, defaults to true and subject to value of base_type setting''',
        validate=validators.Boolean()
        ) 	
    base_type = Option(
        default='lemma',
        doc='''**Syntax:** **remove_punct=***<boolean>*
        **Description:** Options are lemma, lemma_pos, or stem, defaults to lemma and subject to value of base_word setting being true''',
        ) 	
    mv = Option(
        default=True,
        doc='''**Syntax:** **remove_punct=***<boolean>*
        **Description:** Returns words as multivalue otherwise words are space seperated, defaults to true''',
        validate=validators.Boolean()
        ) 	
    force_nltk_tokenize = Option(
        default=False,
        doc='''**Syntax:** **remove_punct=***<boolean>*
        **Description:** Forces use of better NLTK word tokenizer but is slower, defaults to false''',
        validate=validators.Boolean()
        ) 	
    pos_tagset = Option(
        default=None,
        doc='''**Syntax:** **remove_punct=***<boolean>*
        **Description:** Options are universal, wsj, or brown; defaults to universal and subject to base_type set to "lemma_pos"''',
        ) 	
    #https://stackoverflow.com/a/15590384
    def get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return 'n'
    
    def f_remove_urls(self, text):
        return re.sub(
            'https?://[^\b\s<]+',
            '',
            text
        )

    def stream(self, records):
        #self.logger.debug('CleanTextCommand: %s', self)  # logs command line
        for record in records:
            #URL removal
            if self.remove_urls:
                record[self.textfield] = self.f_remove_urls(
                    record[self.textfield]
                )
            #Tokenization
            if (self.base_word and self.base_type == 'lemma_pos') or self.force_nltk_tokenize:
                if (self.base_word and self.base_type == 'lemma_pos'):
                    record[self.textfield] = word_tokenize(
                        record[self.textfield]
                    )
                    record['pos_tag'] = pos_tag(
                        record[self.textfield],
                        tagset=self.pos_tagset
                    )
                elif self.force_nltk_tokenize:
                    record[self.textfield] = word_tokenize(
                        record[self.textfield]
                    )
            elif self.default_clean or (self.base_word and self.base_type == 'lemma'):
                #https://stackoverflow.com/a/1059601
                #record[self.textfield] = re.split('\W+', six.text_type(record[self.textfield].decode("utf-8")))
                record[self.textfield] = re.split('\W+', record[self.textfield])
            else:
                record[self.textfield] = record[self.textfield].split()
            #Default Clean
            if self.default_clean:
                record[self.textfield] = [
                    re.sub(r'[\W\d]','',text).lower()
                    #text.lower().translate(
                    #    None,
                    #    punctuation + digits
                    #)
                    for text in
                    #six.text_type(record[self.textfield].decode("utf-8"))
                    record[self.textfield]
                ]
            #Lemmatization, Lemmatization with POS tagging, or Stemming with stopword removal
            if self.remove_stopwords and self.base_word:
                stopwords = set(stop_words.words('english'))
                if self.base_type == 'lemma_pos':
                    lm = WordNetLemmatizer()
                    record[self.textfield] = [
                        lm.lemmatize(
                            #text[0],
                            re.sub(r'[\W\d]','',text[0]).lower(),
                            self.get_wordnet_pos(text[1])
                        )
                        for text in
                        record['pos_tag']
                        #if text[0] not in stopwords
                        if re.sub(r'[\W\d]','',text[0]).lower() not in stopwords
                    ]
                    record['pos_tag'] = [ 
                        text[1]
                        for text in
                        record['pos_tag']
                        if re.sub(r'[\W\d]','',text[0]).lower() not in stopwords
                        and not re.search(r'[\W]',text[0])
                    ]
                if self.base_type == 'lemma':
                    lm = WordNetLemmatizer()
                    record[self.textfield] = [
                        lm.lemmatize(text)
                        for text in
                        record[self.textfield]
                        if text not in stopwords
                    ]
                if self.base_type == 'stem':
                    ps = PorterStemmer()
                    record[self.textfield] = [
                        ps.stem(text)
                        for text in
                        record[self.textfield]
                        if text not in stopwords
                    ]
            #Lemmatization, Lemmatization with POS tagging, or Stemming without stopword removal
            if not self.remove_stopwords and self.base_word:
                if self.base_type == 'lemma_pos':
                    lm = WordNetLemmatizer()
                    record[self.textfield] = [
                        lm.lemmatize(
                            text[0],
                            self.get_wordnet_pos(text[1])
                        )
                        for text in
                        record['pos_tag']
                    ]
                if self.base_type == 'lemma':
                    lm = WordNetLemmatizer()
                    record[self.textfield] = [
                        lm.lemmatize(text)
                        for text in
                        record[self.textfield]
                    ]
                if self.base_type == 'stem':
                    ps = PorterStemmer()
                    record[self.textfield] = [
                        ps.stem(text)
                        for text in
                        record[self.textfield]
                    ]
            #Stopword Removal
            if self.remove_stopwords and not self.base_word:
                stopwords = set(stop_words.words('english'))
                record[self.textfield] = [
                    text 
                    for text in
                    record[self.textfield]
                    if text not in stopwords
                    ]
            #Final Multi-Value Output
            if not self.mv:
                record[self.textfield] = ' '.join(record[self.textfield])
                record['pos_tag'] = ' '.join(record['pos_tag'])
                    
            yield record

dispatch(CleanText, sys.argv, sys.stdin, sys.stdout, __name__)
