#!/opt/splunk/bin/python

import sys
import os
import logging, logging.handlers

from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path
from splunk import setupSplunkLogger
from bs4 import BeautifulSoup
from splunklib.searchcommands import dispatch, StreamingCommand, Configuration, Option, validators

@Configuration(local=True)
class Bs4(StreamingCommand):
    """ A wrapper for BeautifulSoup4 to extract html/xml tags and text from them to use in Splunk.

    ##Syntax

    .. code-block::
       bs4 textfield=<field> [get_text=<bool>] [parser=<string>] [find=<tag>] [find_all=<tag>] [find_child=<tag>] [find_children=<tag>]

    ##Description

    A wrapper script to bring some functionality from BeautifulSoup to Splunk. Default is to 
    get the text and send it to a new field 'get_text', otherwise the selection is returned 
    in a field named 'soup'. Default is to use the 'lxml' parser, though you can specify others, 
    'html5lib' is not currently included. The find methods can be used in conjuction, their order 
    of operation is find > find_all > find_child > find children. Currently only supports 
    specifying the tag name from those methods, future TODO will be to provide way to specify 
    attrs dictionary to the methods.

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
 
    find_all = Option(
        default=False,
        doc='''
        **Syntax:** **find_all=***<tag>*
        **Description:** Corresponds to the name attribute of BeautifulSoup's find_all method. Order of operation is find > find_all > find_child > find_children so can be used in conjunction''',
        )
 
    find_child = Option(
        default=False,
        doc='''
        **Syntax:** **find_child=***<tag>*
        **Description:** Corresponds to the name attribute of BeautifulSoup's find_child method. Order of operation is find > find_all > find_child > find_children so can be used in conjunction''',
        )

    find_children = Option(
        default=False,
        doc='''
        **Syntax:** **find_children=***<tag>*
        **Description:** Corresponds to the name attribute of BeautifulSoup's find_children method. Order of operation is find > find_all > find_child > find_children so can be used in conjunction''',
        )

    get_text = Option(
        default=True,
        doc='''
        **Syntax:** **get_text=***<bool>*
        **Description:** If true, returns text minus html/xml formatting for given selection and places in field `get_text` otherwise returns the selection in a field called `soup1`''',
        validate=validators.Boolean())

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
                soup = soup.find(self.find)
            if self.find_all:
                soup = soup.find_all(self.find_all)
            if self.find_child:
                soup = soup.findChild(self.find_child)
            if self.find_children:
                soup = soup.findChildren(self.find_children)
            if self.get_text:
                record['get_text'] = soup.get_text()
            else:
                record['soup'] = soup

            yield record

dispatch(Bs4, sys.argv, sys.stdin, sys.stdout, __name__)