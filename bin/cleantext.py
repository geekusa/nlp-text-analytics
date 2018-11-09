#!/opt/splunk/bin/python

import sys
import re
import os
import logging, logging.handlers

from string import punctuation, digits, maketrans

from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path
from splunk import setupSplunkLogger
from nltk import word_tokenize, pos_tag
from nltk.data import path as nltk_data_path
from nltk.corpus import wordnet, stopwords as stop_words
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.util import ngrams
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators

BASE_DIR = make_splunkhome_path(["etc","apps","nlp-text-analytics"])
CORPORA_DIR = os.path.join(BASE_DIR,'bin','nltk_data')
nltk_data_path.append(CORPORA_DIR)


@Configuration(local=True)
class CleanText(StreamingCommand):
    """ Counts the number of non-overlapping matches to a regular expression in a set of fields.

    ##Syntax

    .. code-block::
        cleantext textfield=<field> [default_clean=<bool>] [remove_urls=<bool>] [remove_stopwords=<bool>] 
            [base_word=<bool>] [base_type=<string>] [mv=<bool>] [force_nltk_tokenize=<bool>] 
            [pos_tagset=<string>] [custom_stopwords=<comma_separated_string_list>] [term_min_len=<int>] 
            [ngram_range=<int>-<int>] [ngram_mix=<bool>]

    ##Description

    Tokenize and normalize text (remove punctuation, digits, change to base_word)
    Different options result in better and slower cleaning. base_type="lemma_pos" being the
    slowest option, base_type="lemma" assumes every word is a noun, which is faster but still
    results in decent lemmatization. Many fields have a default already set, textfield is only
    required field. By default results in a multi-valued field which is ready for used with
    stats count by.

    ##Example

    .. code-block::
        * | cleantext textfield=sentence
    """

    textfield = Option(
        require=True,
        doc='''
        **Syntax:** **textfield=***<fieldname>*
        **Description:** Name of the field that will contain the text to search against''',
        validate=validators.Fieldname())
    keep_orig = Option(
        default=False,
        doc='''**Syntax:** **keep_orig=***<boolean>*
        **Description:** Maintain a copy of the original text for comparison or searching into field called
        orig_text''',
        validate=validators.Boolean()
        )
    default_clean = Option(
        default=True,
        doc='''**Syntax:** **default_clean=***<boolean>*
        **Description:** Change text to lowercase, remove punctuation, and removed numbers, defaults to true''',
        validate=validators.Boolean()
        ) 	
    remove_urls = Option(
        default=True,
        doc='''**Syntax:** **remove_urls=***<boolean>*
        **Description:** Remove html links as part of text cleaning, defaults to true''',
        validate=validators.Boolean()
        ) 	
    remove_stopwords = Option(
        default=True,
        doc='''**Syntax:** **remove_stopwords=***<boolean>*
        **Description:** Remove stopwords as part of text cleaning, defaults to true''',
        validate=validators.Boolean()
        ) 	
    base_word = Option(
        default=True,
        doc='''**Syntax:** **base_word=***<boolean>*
        **Description:** Convert words to a base form as part of text cleaning, defaults to true and subject to value of base_type setting''',
        validate=validators.Boolean()
        ) 	
    base_type = Option(
        default='lemma',
        doc='''**Syntax:** **base_type=***<string>*
        **Description:** Options are lemma, lemma_pos, or stem, defaults to lemma and subject to value of base_word setting being true''',
        ) 	
    mv = Option(
        default=True,
        doc='''**Syntax:** **mv=***<boolean>*
        **Description:** Returns words as multivalue otherwise words are space separated, defaults to true''',
        validate=validators.Boolean()
        ) 	
    force_nltk_tokenize = Option(
        default=False,
        doc='''**Syntax:** **force_nltk_tokenize=***<boolean>*
        **Description:** Forces use of better NLTK word tokenizer but is slower, defaults to false''',
        validate=validators.Boolean()
        ) 	
    pos_tagset = Option(
        default=None,
        doc='''**Syntax:** **pos_tagset=***<string>*
        **Description:** Options are universal, wsj, or brown; defaults to universal and subject to base_type set to "lemma_pos"''',
        ) 	
    custom_stopwords = Option(
        doc='''**Syntax:** **custom_stopwords=***<string>*
        **Description:** comma-separated list of custom stopwords, enclose in quotes''',
        )
    term_min_len = Option(
        default=0,
        doc='''**Syntax:** **term_min_len=***<int>*
        **Description:** Only terms greater than or equal to this number will be returned. Useful if data has a lot of HTML markup.''',
        validate=validators.Integer()
        ) 	
    ngram_range = Option(
        default='1-1',
        doc='''**Syntax:** **ngram_rane=***<int>-<int>*
        **Description:** Returns new ngram column with range of ngrams specified if max is greater than 1"''',
        ) 	
    ngram_mix = Option(
        default=False,
        doc='''**Syntax:** **ngram_mix=***<boolean>*
        **Description:** Determines if ngram output is combined or separate columns. Defaults to false which results in separate columns''',
        validate=validators.Boolean()
        ) 	

    #http://dev.splunk.com/view/logging/SP-CAAAFCN
    def setup_logging(self):
        logger = logging.getLogger('splunk.foo')    
        SPLUNK_HOME = os.environ['SPLUNK_HOME']
        
        LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
        LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
        LOGGING_STANZA_NAME = 'python'
        LOGGING_FILE_NAME = "nlp-text-analytics.log"
        BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
        LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
        splunk_log_handler = logging.handlers.RotatingFileHandler(
            os.path.join(
                SPLUNK_HOME,
                BASE_LOG_PATH,
                LOGGING_FILE_NAME
            ), mode='a') 
        splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        logger.addHandler(splunk_log_handler)
        setupSplunkLogger(
            logger,
            LOGGING_DEFAULT_CONFIG_FILE,
            LOGGING_LOCAL_CONFIG_FILE,
            LOGGING_STANZA_NAME
        )
        return logger

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

    def ngram(self, text, min_n, max_n):
        ngram_list = []
        for n in range(min_n,max_n):
            for ngram in ngrams(text, n):
                if len(ngram) > 1:
                    ngram_list.append((len(ngram),' '.join(ngram)))
        return ngram_list


    def stream(self, records):
        logger = self.setup_logging()
        logger.info('textfield set to: ' + self.textfield)
        if self.custom_stopwords:
            custom_stopwords = self.custom_stopwords.replace(' ','').split(',')
        for record in records:
            if self.keep_orig:
                record['orig_text'] = record[self.textfield]
            #URL removal
            if self.remove_urls:
                record[self.textfield] = self.f_remove_urls(
                    record[self.textfield]
                )
            #Tokenization
            if (self.base_word and self.base_type == 'lemma_pos') or self.force_nltk_tokenize:
                #lemma_pos - if option is lemmatization with POS tagging do cleaning and stopword options now
                if (self.base_word and self.base_type == 'lemma_pos'):
                    record['pos_tuple'] = pos_tag(
                        word_tokenize(
                            record[self.textfield].decode('utf-8').encode('ascii', 'ignore')
                        ),
                        tagset=self.pos_tagset
                    )
                    if self.default_clean and self.remove_stopwords:
                        if self.custom_stopwords:
                            stopwords = set(stop_words.words('english') + custom_stopwords)
                        else:
                            stopwords = set(stop_words.words('english'))
                        record['pos_tuple'] = [
                            [
                            re.sub(r'[\W\d]','',text[0]).lower(),
                            text[1]
                            ]
                            for text in
                            record['pos_tuple']
                            if re.sub(r'[\W\d]','',text[0]).lower() not in stopwords
                            and not re.search(r'[\W]',text[0])
                        ]
                    elif self.default_clean and not self.remove_stopwords:
                        record['pos_tuple'] = [
                            [
                            re.sub(r'[\W\d]','',text[0]).lower(),
                            text[1]
                            ]
                            for text in
                            record['pos_tuple']
                            if not re.search(r'[\W]',text[0])
                        ]
                elif self.force_nltk_tokenize:
                    record[self.textfield] = word_tokenize(
                        record[self.textfield]
                    )
            elif self.default_clean or (self.base_word and self.base_type == 'lemma'):
                #https://stackoverflow.com/a/1059601
                record[self.textfield] = re.split('\W+', record[self.textfield])
            else:
                record[self.textfield] = record[self.textfield].split()
            #Default Clean
            if self.default_clean and not self.base_type == 'lemma_pos':
                record[self.textfield] = [
                    re.sub(r'[\W\d]','',text).lower()
                    for text in
                    record[self.textfield]
                ]
            #Lemmatization with POS tagging
            if self.base_word and self.base_type == 'lemma_pos':
                    lm = WordNetLemmatizer()
                    tuple_list = []
                    tag_list = []
                    record[self.textfield] = []
                    record['pos_tag'] = []
                    for text in record['pos_tuple']:
                        keep_text = lm.lemmatize(
                                text[0],
                                self.get_wordnet_pos(text[1])
                            )
                        if keep_text:
                            record[self.textfield].append(keep_text)
                            tuple_list.append((keep_text,text[1]))
                            tag_list.append(text[1])
                            record['pos_tag'] = tag_list
                            record['pos_tuple'] = tuple_list
            #Lemmatization or Stemming with stopword removal
            if self.remove_stopwords and self.base_word and self.base_type != 'lemma_pos':
                if self.custom_stopwords:
                    stopwords = set(stop_words.words('english') + custom_stopwords)
                else:
                    stopwords = set(stop_words.words('english'))
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
            #Lemmatization or Stemming without stopword removal
            if not self.remove_stopwords and self.base_word:
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
                if self.custom_stopwords:
                    stopwords = set(stop_words.words('english') + custom_stopwords)
                else:
                    stopwords = set(stop_words.words('english'))
                record[self.textfield] = [
                    text 
                    for text in
                    record[self.textfield]
                    if text not in stopwords
                    ]
            #Minimum term length
            if self.term_min_len > 0:
                record[self.textfield] = [
                     i
                     for i in record[self.textfield]
                     if len(i) >= self.term_min_len
                     ]
            #ngram column creation
            (min_n,max_n) = self.ngram_range.split('-')
            if max_n > 1 and max_n >= min_n:
                max_n = int(max_n) + 1
                ngram_extract = self.ngram(
                    filter(None, record[self.textfield]),
                    int(min_n),
                    max_n
                )
                if ngram_extract:
                    for i in ngram_extract:
                        if not self.ngram_mix:
                            if 'ngrams_' + str(i[0]) not in record:
                                record['ngrams_' + str(i[0])] = []
                            record['ngrams_' + str(i[0])].append(i[1])
                        else:
                            if 'ngrams' not in record:
                                record['ngrams'] = []
                            record['ngrams'].append(i[1])
                else:
                    if not self.ngram_mix:
                        for n in range(int(min_n),int(max_n)):
                            if n!=1:
                                record['ngrams_' + str(n)] = []
                    else:
                        if 'ngrams' not in record:
                            record['ngrams'] = []
            #Final Multi-Value Output
            if not self.mv:
                record[self.textfield] = ' '.join(record[self.textfield])
                try:
                    record['pos_tag'] = ' '.join(record['pos_tag'])
                except:
                    pass

            yield record

dispatch(CleanText, sys.argv, sys.stdin, sys.stdout, __name__)
