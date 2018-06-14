#!/opt/splunk/bin/python

import sys
import os
import logging, logging.handlers
from ast import literal_eval

from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path
from splunk import setupSplunkLogger
from bs4 import BeautifulSoup
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators

@Configuration(local=True)
class Bs4(StreamingCommand):
    """ A wrapper for BeautifulSoup4 to extract html/xml tags and text from them to use in Splunk.

    ##Syntax

    .. code-block::
       bs4 textfield=<field> [get_text=<bool>] [get_text_label=<string>] [parser=<string>] [find=<tag>] [find_attrs=<quoted_key:value_pairs>] [find_all=<tag>] [find_all_attrs=<quoted_key:value_pairs>] [find_child=<tag>] [find_child_attrs=<quoted_key:value_pairs>] [find_children=<tag>] [find_children_attrs=<quoted_key:value_pairs>]

    ##Description

    A wrapper script to bring some functionality from BeautifulSoup to Splunk. Default is to 
    get the text and send it to a new field 'get_text', otherwise the selection is returned 
    in a field named 'soup'. Default is to use the 'lxml' parser, though you can specify others, 
    'html5lib' is not currently included. The find methods can be used in conjuction, their order 
    of operation is find > find_all > find_child > find children. Each option has a similar
    named option appended '_attrs' that will accept inner and outer quoted key:value pairs for
    more precise selections.attrs dictionary to the methods.

    ##Example

    .. code-block::
        * | bs4 textfield=_raw find="div" get_text=t
    """

    textfield = Option(
        require=True,
        doc='''
        **Syntax:** **textfield=***<fieldname>*
        **Description:** Name of the field that will contain the text to search against''',
        validate=validators.Fieldname())

    parser = Option(
        default='lxml',
        doc='''
        **Syntax:** **parser=***<string>*
        **Description:** Corresponds to parsers listed here https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser (currently html5lib not packaged with so not an option)''',
        )
 
    find = Option(
        default=False,
        doc='''
        **Syntax:** **find=***<tag>*
        **Description:** Corresponds to the name attribute of BeautifulSoup's find method''',
        )
 
    find_attrs = Option(
        default=None,
        doc='''
        **Syntax:** **find_attrs=***<quoted_key:value_pairs>*
        **Description:** Corresponds to the attrs attribute of BeautifulSoup's find method. Expects inner and outer quoted "'key1':'value1','key2':'value2'" pairs comma-separated but contained in outer quotes.''',
        )
 
    find_all = Option(
        default=False,
        doc='''
        **Syntax:** **find_all=***<tag>*
        **Description:** Corresponds to the name attribute of BeautifulSoup's find_all method. Order of operation is find > find_all > find_child > find_children so can be used in conjunction''',
        )
 
    find_all_attrs = Option(
        default=None,
        doc='''
        **Syntax:** **find_all_attrs=***<quoted_key:value_pairs>*
        **Description:** Corresponds to the attrs attribute of BeautifulSoup's find_all method. Expects inner and outer quoted "'key1':'value1','key2':'value2'" pairs comma-separated but contained in outer quotes.''',
        )
 
    find_child = Option(
        default=False,
        doc='''
        **Syntax:** **find_child=***<tag>*
        **Description:** Corresponds to the name attribute of BeautifulSoup's find_child method. Order of operation is find > find_all > find_child > find_children so can be used in conjunction''',
        )

    find_child_attrs = Option(
        default=None,
        doc='''
        **Syntax:** **find_child_attrs=***<quoted_key:value_pairs>*
        **Description:** Corresponds to the attrs attribute of BeautifulSoup's find_child method. Expects inner and outer quoted "'key1':'value1','key2':'value2'" pairs comma-separated but contained in outer quotes.''',
        )
 
    find_children = Option(
        default=False,
        doc='''
        **Syntax:** **find_children=***<tag>*
        **Description:** Corresponds to the name attribute of BeautifulSoup's find_children method. Order of operation is find > find_all > find_child > find_children so can be used in conjunction''',
        )

    find_children_attrs = Option(
        default=None,
        doc='''
        **Syntax:** **find_children_attrs=***<quoted_key:value_pairs>*
        **Description:** Corresponds to the attrs attribute of BeautifulSoup's find_children method. Expects inner and outer quoted "'key1':'value1','key2':'value2'" pairs comma-separated but contained in outer quotes.''',
        )
 
    get_text = Option(
        default=True,
        doc='''
        **Syntax:** **get_text=***<bool>*
        **Description:** If true, returns text minus html/xml formatting for given selection and places in field `get_text` otherwise returns the selection in a field called `soup1`''',
        validate=validators.Boolean())

    get_text_label = Option(
        default='get_text',
        doc='''
        **Syntax:** **get_text_label=***<string>*
        **Description:** If get_text is true, sets the label for the return field''',
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

    def stream(self, records):
        for record in records:
            soup = BeautifulSoup(record[self.textfield], self.parser)
            if self.find:
                if self.find_attrs is not None:
                    soup = soup.find(
                        self.find, 
                        literal_eval('{'+self.find_attrs+'}')
                    )
                else:
                    soup = soup.find(self.find)
            if self.find_all:
                if self.find_all_attrs is not None:
                    soup = soup.find_all(
                        self.find_all, 
                        literal_eval('{'+self.find_all_attrs+'}')
                    )
                else:
                    soup = soup.find_all(self.find_all)
            if self.find_child:
                if self.find_child_attrs is not None:
                    soup = soup.findChild(
                        self.find_child, 
                        literal_eval('{'+self.find_child_attrs+'}')
                    )
                else:
                    soup = soup.findChild(self.find_child)
            if self.find_children:
                if self.find_children_attrs is not None:
                    soup = soup.findChildren(
                        self.find_children, 
                        literal_eval('{'+self.find_children_attrs+'}')
                    )
                else:
                    soup = soup.findChildren(self.find_children)
            if self.get_text and not (self.find_all or self.find_children):
                record[self.get_text_label] = soup.get_text()
            elif self.get_text and (self.find_all or self.find_children):
                record[self.get_text_label] = [
                    i.get_text()
                    for i in soup
                ]
            else:
                record['soup'] = soup

            yield record

dispatch(Bs4, sys.argv, sys.stdin, sys.stdout, __name__)
