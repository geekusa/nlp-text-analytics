#!/opt/splunk/bin/python

from __future__ import division
import sys
import os

from collections import OrderedDict
from nltk.metrics.distance import edit_distance
from nltk.metrics.distance import jaro_similarity
from nltk.metrics.distance import jaro_winkler_similarity
from nltk.metrics.distance import jaccard_distance
from nltk.metrics.distance import masi_distance
from nltk.data import path as nltk_data_path
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CORPORA_DIR = os.path.join(BASE_DIR,'nltk_data')
nltk_data_path.append(CORPORA_DIR)


@Configuration(local=True)
class Similarity(StreamingCommand):
    """ Returns distance and similarity scores between 0 and 1. Some algorithms also return number of steps to make text the same. Can handle multi-valued fields. 

    ##Syntax

    .. code-block::
        similarity textfield=<field> comparefield=<field> algo=<algorithm>

    ##Description

    Similarity (and distance) metrics can be used to tell how far apart to pieces of text
    are and in some algorithms return also the number of steps to make the text the same. 
    These do not extract meaning, but are often used in text analytics to discover 
    plagurism, conduct fuzzy searching, spell checking, and more. Defaults to using the 
    Levenshtein distance algorithm but includes several other algorithms, include some set 
    based algorithms. Can handle multi-valued comparisons with an option to limit to a 
    given number of top matches. Multi-valued output can be zipped together or returned 
    seperately.  

    ##Example

    .. code-block::
        * | similarity textfield=text comparefield=compare algo=damerau
    """

    textfield = Option(
        require=True,
        doc='''
        **Syntax:** **textfield=***<fieldname>*
        **Description:** Name of the field that will contain the source text to compare against. Field can be multi-valued.''',
        validate=validators.Fieldname()
        )
    comparefield = Option(
        require=True,
        doc='''
        **Syntax:** **comparefield=***<fieldname>*
        **Description:** Name of the field that will contain the target text to compare against. Field can be multi-valued.''',
        validate=validators.Fieldname()
        )
    algo = Option(
        default='levenshtein',
        doc='''**Syntax:** **base_type=***<string>*
        **Description:** Algorithm used for determining text similarity. Options are levenshtein, damerau, jaro, jaro_winkler, jaccard, and masi. Defaults to levenshtein. See included dashboard for explanation of each algorithm''',
        ) 	
    limit = Option(
        default=10,
        doc='''**Syntax:** **limit=***<int>*
        **Description:** When using multi-valued comparisons, this value limits the number of top matches returned. Defaults to 10.''',
        validate=validators.Integer()
        ) 	
    mvzip = Option(
        default=False,
        doc='''**Syntax:** **mvzip=***<boolean>*
        **Description:** When using multi-valued comparisons, when this option is true the output is similar to using Splunk's mvzip option. Output is value:top_match_target for single-valued to multi-valued comparision and value:top_match_source>top_match_target for multi-valued to multi-valued comparision''',
        validate=validators.Boolean()
        ) 	

    def distance_to_ratio(self, distance_steps, len1, len2):
        '''convert distance steps to distance ratio'''
        len_list = [len1, len2]
        len_max = max(len_list)
        return distance_steps/len_max

    def algo_select(self, text, compare, transposition, set_algo, algo):
        if set_algo:
            if ' ' in text and ' ' in compare:
                results = eval(algo+'(set("'+text+'".split()), set("'+compare+'".split()))')
            else:
                results = eval(algo+'(set("'+text+'"), set("'+compare+'"))')
        else:
            results = eval(algo+'("'+text+'", "'+compare+'"'+transposition+')')
        return results

    def conversion(self, distance=None, similarity=None):
        '''convert distance ratio to similarity ratio and vice-versa'''
        if distance or distance==0:
            if distance > 1:
                similarity = 1 / (1 + distance)
            else:
                similarity = 1 - distance
            return similarity
        if similarity or similarity==0:
            if similarity > 1:
                distance = (1 / similarity) - 1
            else:
                distance = 1 - similarity
            return distance

    def mvzip_out(self, record, text, top_matches, mvzip, single, algo):
        if mvzip:
            if 'edit' in algo:
                record['distance_steps'] = [
                    str(v[0])+':'+k
                    for k, v in top_matches.items()
                ]
                record['distance'] = [
                    str(v[1])+':'+k
                    for k, v in top_matches.items()
                ]
                record['similarity'] = [
                    str(self.conversion(distance=v[1]))+':'+k
                    for k, v in top_matches.items()
                ]
            elif 'distance' in algo:
                record['distance'] = [
                    str(v)+':'+k
                    for k, v in top_matches.items()
                ]
                record['similarity'] = [
                    str(self.conversion(distance=v))+':'+k
                    for k, v in top_matches.items()
                ]
            elif 'similarity' in algo:
                record['similarity'] = [
                    str(v)+':'+k
                    for k, v in top_matches.items()
                ]
                record['distance'] = [
                    str(self.conversion(similarity=v))+':'+k
                    for k, v in top_matches.items()
                ]
        else:
            if 'distance' in algo:
                if 'edit' in algo:
                    record['distance_steps'] = [ v[0] for k, v in top_matches.items() ]
                    record['distance'] = [ v[1] for k, v in top_matches.items() ]
                else:
                    record['distance'] = [ v for k, v in top_matches.items() ]
                record['similarity'] = [ 
                    self.conversion(distance=i) 
                    for i in record['distance']
                ]
            elif 'similarity' in algo:
                record['similarity'] = [ v for k, v in top_matches.items() ]
                record['distance'] = [
                    self.conversion(similarity=i)
                    for i in record['similarity']
                ]
            if single:
                record['top_match_target'] = [ k for k, v in top_matches.items() ]
            else:
                record['top_match_source'] = [ k.split('>')[0] for k, v in top_matches.items() ]
                record['top_match_target'] = [ k.split('>')[1] for k, v in top_matches.items() ]
        return record

    def single_to_single(self, record, text, compare, transposition, set_algo, algo):
        if record[text] == record[compare] and not set_algo:
            if 'edit' in algo:
                record['distance_steps'] = 0
            record['distance'] = 0
            record['similarity'] = 1
        else:
            results = self.algo_select(record[text], record[compare], transposition, set_algo, algo)
            if 'edit' in algo:
                record['distance_steps'] = results
                record['distance'] = self.distance_to_ratio(record['distance_steps'], len(record[text]), len(record[compare]))
                record['similarity'] = self.conversion(distance=record['distance'])
            elif 'distance' in algo:
                record['distance'] = results
                record['similarity'] = self.conversion(distance=record['distance'])
            elif 'similarity' in algo:
                record['similarity'] = results
                record['distance'] = self.conversion(similarity=record['similarity'])
        return record
        
    def single_to_multi(self, record, text, compare, reverse, transposition, limit, mvzip, set_algo, algo):
        compare_dict = {}
        for c in record[compare]:
            if record[text] != c:
                result = self.algo_select(record[text], c, transposition, set_algo, algo)
                if 'edit' in algo:
                    compare_dict[c] = (
                        result,
                        self.distance_to_ratio(result, len(record[text]), len(c))
                    )
                else:
                    compare_dict[c] = result
        if 'edit' in algo:
            top_matches = OrderedDict()
            for k,v in sorted(compare_dict.items(), key=lambda x: x[1][1], reverse=reverse)[:limit]:
                top_matches[k] = compare_dict[k]
        else: 
            top_matches = OrderedDict()
            for k in sorted(compare_dict, key=compare_dict.get, reverse=reverse)[:limit]:
                top_matches[k] = compare_dict[k]
        single=True
        record = self.mvzip_out(record, text, top_matches, mvzip, single, algo)
        return record

    def multi_to_multi(self, record, text, compare, reverse, transposition, limit, mvzip, set_algo, algo):
        compare_dict = {}
        for t in record[text]:
            for c in record[compare]:
                if t != c:
                    result = self.algo_select(t, c, transposition, set_algo, algo)
                    if 'edit' in algo:
                        compare_dict[t+'>'+c] = (
                            result,
                            self.distance_to_ratio(result, len(t), len(c))
                        )
                    else:
                        compare_dict[t+'>'+c] = result
        if 'edit' in algo:
            top_matches = OrderedDict()
            for k,v in sorted(compare_dict.items(), key=lambda x: x[1][1], reverse=reverse)[:limit]:
                top_matches[k] = compare_dict[k]
        else:
            top_matches = OrderedDict()
            for k in sorted(compare_dict, key=compare_dict.get, reverse=reverse)[:limit]:
                top_matches[k] = compare_dict[k]
        single=False
        record = self.mvzip_out(record, text, top_matches, mvzip, single, algo)
        return record

    def stream(self, records):
        text = self.textfield
        compare = self.comparefield
        transposition=''
        reverse = False
        set_algo = False
        if self.algo.lower() == 'levenshtein':
            algo = 'edit_distance'
        if self.algo.lower() == 'damerau':
            algo = 'edit_distance'
            transposition=', transpositions=True'
        elif self.algo.lower() == 'jaro':
            algo = 'jaro_similarity'
            reverse = True
        elif self.algo.lower() == 'jaro_winkler' or self.algo.lower() == 'jaro-winkler':
            algo = 'jaro_winkler_similarity'
            reverse = True
        elif self.algo.lower() == 'jaccard':
            algo = 'jaccard_distance'
            set_algo = True
        elif self.algo.lower() == 'masi':
            algo = 'masi_distance'
            set_algo = True
        for record in records:
            #single-valued to single-valued comparison
            if not isinstance(record[text], list) and not isinstance(record[compare], list):
                record = self.single_to_single(record, text, compare, transposition, set_algo, algo)
            #single-valued to multi-valued comparison
            if not isinstance(record[compare], list) and isinstance(record[text], list):
                record = self.single_to_multi(record, compare, text, reverse, transposition, self.limit, self.mvzip, set_algo, algo)
            if not isinstance(record[text], list) and isinstance(record[compare], list):
                record = self.single_to_multi(record, text, compare, reverse, transposition, self.limit, self.mvzip, set_algo, algo)
            #mulit-valued to multi-valued comparison
            if isinstance(record[text], list) and isinstance(record[compare], list):
                record = self.multi_to_multi(record, text, compare, reverse, transposition, self.limit, self.mvzip, set_algo, algo)

            yield record

dispatch(Similarity, sys.argv, sys.stdin, sys.stdout, __name__)
