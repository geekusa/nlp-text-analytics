#!/usr/bin/env python

import sys
import os
from ast import literal_eval

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
if sys.version_info >= (3, 0):
    sys.path.insert(0, os.path.join(BASE_DIR,'lib3'))
else:
    sys.path.insert(0, os.path.join(BASE_DIR,'lib2'))
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
    more precise selections.

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

    get_attr = Option(
        default=None,
        doc='''
        **Syntax:** **get_attr=***<attribute_name_string>*
        **Description:** If set, returns attribute value for given selection and places in field of the same name''',
        )

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
                if "," in self.find_all:
                    self.find_all = self.find_all.replace(' ','').split(',')
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
            if self.get_attr and not (self.find_all or self.find_children):
                record[self.get_attr] = \
                    soup.get(self.get_attr)
            elif self.get_attr and (self.find_all or self.find_children):
                record[self.get_attr] = [
                    i.get(self.get_attr)
                    for i in soup
                ]
            if self.get_text and not (self.find_all or self.find_children):
                if sys.version_info >= (3, 0):
                    record[self.get_text_label] = soup.get_text()
                else:
                    record[self.get_text_label] = \
                        soup.get_text().decode('unicode_escape').encode('ascii','ignore')
            elif self.get_text and (self.find_all or self.find_children):
                record[self.get_text_label] = [
                    i.get_text()
                    for i in soup
                ]
                if sys.version_info >= (3, 0):
                    record[self.get_text_label] = [
                        i.get_text()
                        for i in soup
                    ]
                else:
                    record[self.get_text_label] = [
                        i.get_text().decode('unicode_escape').encode('ascii','ignore')
                        for i in soup
                    ]
            else:
                if (self.find_all or self.find_children):
                    record['soup'] = [
                        str(i)
                        for i in soup
                    ]
                elif not (self.find_all or self.find_children):
                    record['soup'] = soup

            yield record

dispatch(Bs4, sys.argv, sys.stdin, sys.stdout, __name__)
