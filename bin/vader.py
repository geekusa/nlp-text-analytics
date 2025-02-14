"""
Valence Aware Dictionary and sEntiment Reasoner
Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for
Sentiment Analysis of Social Media Text. Eighth International Conference on
Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.
"""

#!/usr/bin/env python
import exec_anaconda
exec_anaconda.exec_anaconda()

import sys
import os

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.data import path as nltk_data_path
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CORPORA_DIR = os.path.join(BASE_DIR,'nltk_data')
nltk_data_path.append(CORPORA_DIR)


@Configuration(local=True)
class Vader(StreamingCommand):
    """ Returns sentiment score between -1 and 1, can also return detailed sentiment values.

    ##Syntax

    .. code-block::
        vader textfield=<field>

    ##Description

    Sentiment analysis using Valence Aware Dictionary and sEntiment Reasoner
    Using option full_output will return scores for neutral, positive, and negative which
    are the scores that make up the compound score (that is just returned as the field
    "sentiment". Best to feed in uncleaned data as it takes into account capitalization
    and punctuation.

    ##Example

    .. code-block::
        * | vader textfield=sentence
    """

    textfield = Option(
        require=True,
        doc='''
        **Syntax:** **textfield=***<fieldname>*
        **Description:** Name of the field that will contain the text to search against''',
        validate=validators.Fieldname())

    full_output = Option(
        default=False,
        doc='''
        **Syntax:** **full_output=***<fieldname>*
        **Description:** If true, returns full sentiment values--neutral, positive, and negative--otherwise only compound is reutrned''',
        validate=validators.Boolean())

    def stream(self, records):
        sentiment_analyzer = SentimentIntensityAnalyzer()
        for record in records:
            polarity = sentiment_analyzer.polarity_scores(record[self.textfield])
            record['sentiment'] = polarity['compound']
            if self.full_output:
                record['sentiment_neutral'] = polarity['neu']
                record['sentiment_negative'] = polarity['neg']
                record['sentiment_positive'] = polarity['pos']

            yield record

dispatch(Vader, sys.argv, sys.stdin, sys.stdout, __name__)
