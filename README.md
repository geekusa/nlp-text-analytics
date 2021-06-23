# NLP Text Analytics Splunk App

The intent of this app is to provide a simple interface for analyzing text in Splunk using python natural language processing libraries (currently just NLTK 3.4.5). The app provides custom commands and dashboards to show how to use. 

Available at:
[Github](https://github.com/geekusa/nlp-text-analytics)

Splunk App Available at:
[https://splunkbase.splunk.com/app/4066/](https://splunkbase.splunk.com/app/4066/)

Version: 1.1.2

##### Author: Nathan Worsham 
Created for MSDS692 Data Science Practicum I at Regis University, 2018 </br>
See [associated blog](https://github.com/geekusa/nlp-text-analytics/blob/master/PROJECT_FILES/blog.md) for detailed information on the project creation.

Update:
Additional content (combined features algorithms) created for MSDS696 Data Science Practicum II at Regis University, 2018 </br>
See [associated blog](https://github.com/geekusa/combined-feature-classifier) for detailed information on the project creation.
This app was part of the basis for a breakout session at Splunk Conf18 I was lucky enough to present at--[Extending Splunk MLTK using GitHub Community](https://conf.splunk.com/conf-online.html?search=fn1409#/).
[Session Slides](https://static.rainfocus.com/splunk/splunkconf18/sess/1523381218451001Aj1y/finalPDF/FN1409_GitHubCollaboration_Final_1538799477337001rcTB.pdf)
[Session Recording](https://conf.splunk.com/files/2018/recordings/extending-splunk-mltk-using-fn1409.mp4)

## Description and Use-cases

Have you ever wanted to perform advanced text analytics inside Splunk? Splunk has some ways to handle text but also lacks some more advanced features that NLP libraries can offer. This can also benefit use-cases that involve using Splunk’s ML Toolkit.

## Requirements
Splunk ML Toolkit 3.2 or greater [https://splunkbase.splunk.com/app/2890/](https://splunkbase.splunk.com/app/2890/) </br>
Wordcloud Custom Visualization [https://splunkbase.splunk.com/app/3212/](https://splunkbase.splunk.com/app/3212/) (preferred) OR Splunk Dashboard Examples [https://splunkbase.splunk.com/app/1603/](https://splunkbase.splunk.com/app/1603/) </br>
Parallel Coordinates Custom Visualization [https://splunkbase.splunk.com/app/3137/](https://splunkbase.splunk.com/app/3137/) </br>
Force Directed App For Splunk [https://splunkbase.splunk.com/app/3767/](https://splunkbase.splunk.com/app/3767/)
Halo - Custom Visualization [https://splunkbase.splunk.com/app/3514/](https://splunkbase.splunk.com/app/3514/)
Sankey Diagram - Custom Visualization [https://splunkbase.splunk.com/app/3112/](https://splunkbase.splunk.com/app/3112/)

## How to use

### Install

Normal app installation can be followed from https://docs.splunk.com/Documentation/AddOns/released/Overview/AboutSplunkadd-ons. Essentially download app and install from Web UI or extract file in $SPLUNK\_HOME/etc/apps folder.

### Example Texts

The app comes with example Gutenberg texts formatted as CSV lookups along with the popular "20 newsgroups" dataset. Load them with the syntax `| inputlookup <filename.csv>` 

##### Text Names
`20newsgroups.csv` <br/>
`moby_dick.csv` <br/>
`peter_pan.csv` <br/>
`pride_prejudice.csv` <br/>

### Custom Commands

_bs4_
> #### Description
> A wrapper for BeautifulSoup4 to extract html/xml tags and text from them to use in Splunk. A wrapper script to bring some functionality from BeautifulSoup to Splunk. Default is to get the text and send it to a new field 'get\_text', otherwise the selection is returned in a field named 'soup'. Default is to use the 'lxml' parser, though you can specify others, 'html5lib' is not currently included. The find methods can be used in conjuction, their order of operation is find > find\_all > find\_child > find children. Each option has a similar named option appended '\_attrs' that will accept inner and outer quoted key:value pairs for more precise selections.
> #### Syntax
> \*| bs4 textfield=<field> [get\_text=<bool>] [get\_text\_label=<string>] [parser=<string>] [find=<tag>] [find\_attrs=<quoted\_key:value\_pairs>] [find\_all=<tag>] [find\_all\_attrs=<quoted\_key:value\_pairs>] [find\_child=<tag>] [find\_child\_attrs=<quoted\_key:value\_pairs>] [find\_children=<tag>] [find\_children\_attrs=<quoted\_key:value\_pairs>]
> ##### Required Arguments
> **textfield** </br>
>     **Syntax:** textfield=\<field> </br>
>     **Description:** The search field that contains the text that is the target. </br>
>     **Usage:** Option only takes a single field
> ##### Optional Arguments
> **get\_text** </br>
>     **Syntax:** get\_text=\<bool> </br>
>     **Description:** If true, returns text minus html/xml formatting for given selection and places in field `get_text` otherwise returns the selection in a field called `soup1`. </br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1</br>
>     **Default:** True
> 
> **get\_text\_label** </br>
>     **Syntax:** get\_text\_label=\<string> </br>
>     **Description:** If get_text is set, sets the label for the return field. </br>
>     **Usage:** String value</br>
>     **Default:** get_text
> 
> **get\_attr** </br>
>     **Syntax:** get\_attr=\<attribute_name_string> </br>
>     **Description:** If set, returns attribute value for given selection and places in field of the same name. </br>
>     **Usage:** String value</br>
> 
> **parser** </br>
>     **Syntax:** parser=\<string> </br>
>     **Description:** Corresponds to parsers listed [here](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser) (currently html5lib not packaged with so not an option). </br>
>     **Usage:** Possible values are html.parser, lxml, lxml-xml, or xml
>     **Default:** lxml
> 
>**find** </br>
>     **Syntax:** find=\<tag> </br>
>     **Description:** Corresponds to the name attribute of BeautifulSoup's find method. </br>
>     **Usage:** HTML or XML element name
> 
>**find\_attrs** </br>
>     **Syntax:** find\_attrs=\<quoted_key:value_pairs> </br>
>     **Description:** Corresponds to the attrs attribute of BeautifulSoup's find method. Expects inner and outer quoted key:value pairs comma-separated but contained in outer quotes.
>     **Usage:** "'key1':'value1','key2':'value2'"
> 
>**find\_all** </br>
>     **Syntax:** find\_all=\<tag(s)> </br>
>     **Description:** Corresponds to the name attribute of BeautifulSoup's find_all method. Order of operation is find > find_all > find_child > find_children so can be used in conjunction. Can find one or more tags by comma separating tags (also quote entire option) i.e. find_all="div, a".</br>
>     **Usage:** HTML or XML element name
> 
>**find\_all\_attrs** </br>
>     **Syntax:** find\_all\_attrs=\<quoted_key:value_pairs> </br>
>     **Description:** Corresponds to the attrs attribute of BeautifulSoup's find_all method. Expects inner and outer quoted key:value pairs comma-separated but contained in outer quotes.
>     **Usage:** "'key1':'value1','key2':'value2'"
> 
>**find\_child** </br>
>     **Syntax:** find\_child=\<tag> </br>
>     **Description:** Corresponds to the name attribute of BeautifulSoup's find_child method. Order of operation is find > find_all > find_child > find_children so can be used in conjunction. </br>
>     **Usage:** HTML or XML element name
> 
>**find\_child\_attrs** </br>
>     **Syntax:** find\_child\_attrs=\<quoted_key:value_pairs> </br>
>     **Description:** Corresponds to the attrs attribute of BeautifulSoup's find_child method. Expects inner and outer quoted key:value pairs comma-separated but contained in outer quotes.
>     **Usage:** "'key1':'value1','key2':'value2'"
> 
>**find\_children** </br>
>     **Syntax:** find\_children=\<tag> </br>
>     **Description:** Corresponds to the name attribute of BeautifulSoup's find_children method. Order of operation is find > find_all > find_child > find_children so can be used in conjunction. </br>
>     **Usage:** HTML or XML element name
> 
>**find\_children\_attrs** </br>
>     **Syntax:** find\_children\_attrs=\<quoted_key:value_pairs> </br>
>     **Description:** Corresponds to the attrs attribute of BeautifulSoup's find_children method. Expects inner and outer quoted key:value pairs comma-separated but contained in outer quotes.
>     **Usage:** "'key1':'value1','key2':'value2'"
> 
_cleantext_
> #### Description
> Tokenize and normalize text (remove punctuation, digits, change to base\_word). Different options result in better and slower cleaning. base\_type="lemma\_pos" being the slowest option, base\_type="lemma" assumes every word is a noun, which is faster but still results in decent lemmatization. Many fields have a default already set, textfield is only required field. By default results in a multi-valued field which is ready for used with stats count by. Optionally return special fields for analysis--pos\_tags and ngrams.
> #### Syntax
> \* | cleantext textfield=<field> [keep\_orig=<bool>] [default\_clean=<bool>] [remove\_urls=<bool>] [remove\_stopwords=<bool>] [base\_word=<bool>] [base\_type=<string>] [mv=<bool>] [force\_nltk\_tokenize=<bool>] [pos\_tagset=<string>] [custom\_stopwords=<comma\_separated\_string\_list>] [term\_min\_len=<int>] [ngram\_range=<int>-<int>] [ngram\_mix=<bool>]
> ##### Required Arguments
> **textfield** </br>
>     **Syntax:** textfield=\<field> </br>
>     **Description:** The search field that contains the text that is the target of the analysis. </br>
>     **Usage:** Option only takes a single field
> ##### Optional Arguments
> **keep\_orig** </br>
>     **Syntax:** keep\_orig=\<bool> </br>
>     **Description:** Maintain a copy of the original text for comparison or searching into field called orig_text</br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1</br>
>     **Default:** False
> 
> **default\_clean** </br>
>     **Syntax:** default\_clean=\<bool> </br>
>     **Description:** Perform basic text cleaning--lowercase, remove punctuation and digits, and tokenization. </br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1</br>
>     **Default:** True
> 
> **remove\_urls** </br>
>     **Syntax:** remove\_urls=\<bool> </br>
>     **Description:** Before cleaning remove html links. </br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1</br>
>     **Default:** True
> 
>**remove\_stopwords** </br>
>     **Syntax:** remove\_stopwords=\<bool> </br>
>     **Description:** Remove stopwords (i.e. common words like "the" and "I"), currently only supports english. </br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1</br>
>     **Default:** True
> 
>**base\_word** </br>
>     **Syntax:** base\_word=\<bool> </br>
>     **Description:** Turns on lemmatization or stemming, dependant on the value of base\_type. </br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1</br>
>     **Default:** True
> 
>**base\_type** </br>
>     **Syntax:** base\_type=\<string> </br>
>     **Description:** Sets the value for the type of word base to use, dependant on base\_word being set to True. Lemmatization without POS tagging (option lemma) assumes every word is a noun but results in a comprable but faster output. Lemmatization with POS tagging (lemma\_pos) is slower but more precice, also adds a new field of `pos_tag`. When set to lemma\_pos this automatically sets force_nltk\_tokenize argument to true. Porter Stemmer is used when the option is set to stem.</br>
>     **Usage:** Possible values are lemma, lemma\_pos, stem</br>
>     **Default:** True
> 
>**mv** </br>
>     **Syntax:** mv=\<bool> </br>
>     **Description:** Returns the output as a multi-value field (ready for use with stats count), otherwise returns as a space seperated string. </br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1</br>
>     **Default:** True
> 
>**pos\_tagset** </br>
>     **Syntax:** pos\_tagset=\<string> </br>
>     **Description:** Sets the option for the tagset used--Advanced Perceptron tagger (None) or universal. </br>
>     **Usage:** None or universal</br>
>     **Default:** None
> 
>**term\_min\_len** </br>
>     **Syntax:** term\_min\_len=\<int> </br>
>     **Description:** Only terms greater than or equal to this number will be returned. </br>
>     **Usage:** Interger value of minimum length of terms to return</br>
>     **Default:** 0
> 
>**ngram\_range** </br>
>     **Syntax:** ngram\_range=\<int>-<int> </br>
>     **Description:** Returns new ngram column with range of ngrams specified if max is greater than 1. </br>
>     **Usage:** Generally values like 1-2 (same as 2-2), 2-3, 2-4 are used, ngrams above 4 may not provide much value</br>
>     **Default:** 1-1
> 
>**ngram\_mix** </br>
>     **Syntax:** mv=\<bool> </br>
>     **Description:** Determines if ngram output is combined or separate columns. Defaults to false which results in separate columns</br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1</br>
>     **Default:** False

_similarity_
> #### Description
> A wrapper for NTLK distance metrics for comparing text to use in Splunk. Similarity (and distance) metrics can be used to tell how far apart to pieces of text are and in some algorithms return also the number of steps to make the text the same. These do not extract meaning, but are often used in text analytics to discover plagurism, conduct fuzzy searching, spell checking, and more. Defaults to using the Levenshtein distance algorithm but includes several other algorithms, include some set based algorithms. Can handle multi-valued comparisons with an option to limit to a given number of top matches. Multi-valued output can be zipped together or returned seperately.
> #### Syntax
> \*| similarity textfield=<field> comparefield=<field> [algo=<string>] [limit=<int>] [mvzip=<bool>]
> ##### Required Arguments
> **textfield** </br>
>     **Syntax:** textfield=\<field> </br>
>     **Description:** Name of the field that will contain the source text to compare against. Field can be multi-valued.</br>
>     **Usage:** Option only takes a single field </br>
>
> **comparefield** </br>
>     **Syntax:** comparefield=\<field> </br>
>     **Description:** Name of the field that will contain the target text to compare against. Field can be multi-valued.</br>
>     **Usage:** Option only takes a single field </br>
> ##### Optional Arguments
> **algo** </br>
>     **Syntax:** algo=\<string> </br>
>     **Description:** Algorithm used for determining text similarity. Options are levenshtein, damerau, jaro, jaro_winkler, jaccard, and masi. Defaults to levenshtein. See included dashboard for explanation of each algorithm</br>
>     **Usage:** Algorithm name, options are levenshtein, damerau, jaro, jaro_winkler, jaccard, and masi.</br>
>     **Default:** levenshtein<br/>
>     **Algorithm Explanations:** 
>     levenshtein = Levenshtein Distance - Also known as edit distance, this algorithm is a measurement of how many steps (or operations) it takes to make one string into another. The steps include insertions, deletions and substitutions.
>     damerau = Damerau-Levenshtein Distance - Also known as edit distance with transposition in that it is different from the traditional Levenshtein distance by also allowing transpositions (of two neighboring characters) as one of the edits. This can result in less steps for some comparisons, for example 'brain' and 'brian' would be 2 steps in the traditional Levenshtein algorithm but 1 step in the Damerau-Levenshtein. 
>     jaro = Jaro Similarity - Similarity algorithm that takes into account the length of the text comparisons, the number of characters that match (within a certain amount of positions based on length), as well as the number of transpositions. 
>     jaro_winkler = Like the Jaro similarity algorithm, this algorithm also takes into account the length of the text comparisons, the number of characters that match (within a certain amount of positions based on length), as well as the number of transpositions. However the Jaro-Winkler algorithm also gives higher precedence for matching a quantity of the beginning characters.
>     jaccard = Jaccard Distance - A set based distance algorithm, measures shared members of each set. Because this is set based and example such as 'brain' and 'brian' would match completely because the set of each do not differentiate order. However set based algorithms can do well with sentences as any space separated words will be compared at the word level rather than the character level (a good place to use the cleartext command first with lemmatization). 
>     masi = MASI Distance - A set based distance algorithm whose name means Measuring Agreement on Set-Valued Items (MASI) for Semantic and Pragmatic Annotation. This algorithm is an implementation of the Jaccard Distance but gives weight to "monotonicity" (essentially repeating members). Because this is set based and example such as 'brain' and 'brian' would match completely because the set of each do not differentiate order. However set based algorithms can do well with sentences as any space separated words will be compared at the word level rather than the character level (a good place to use the cleartext command first with lemmatization).
> 
>**limit** </br>
>     **Syntax:** limit=\<int> </br>
>     **Description:** When using multi-valued comparisons, this value limits the number of top matches returned.
>     **Usage:** Interger value of minimum top matches to return</br>
>     **Default:** 10
> 
> **mvzip** </br>
>     **Syntax:** mvzip=\<bool> </br>
>     **Description:** When using multi-valued comparisons, when this option is true the output is similar to using Splunk's mvzip option. Output is value:top_match_target for single-valued to multi-valued comparision and value:top_match_source>top_match_target for multi-valued to multi-valued comparision.</br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1</br>
>     **Default:** False

_vader_
> #### Description
> Sentiment analysis using Valence Aware Dictionary and sEntiment Reasoner. Using option full_output will return scores for neutral, positive, and negative which are the scores that make up the compound score (that is just returned as the field "sentiment". Best to feed in uncleaned data as it takes into account capitalization and punctuation.
> #### Syntax
> \* | vader textfield=sentence [full_output=<bool>]
> ##### Required Arguments
> **textfield** </br>
>     **Syntax:** textfield=\<field> </br>
>     **Description:** The search field that contains the text that is the target of the analysis. </br>
>     **Usage:** Option only takes a single field
> ##### Optional Arguments
> **full_output** </br>
>     **Syntax:** full_output=\<bool> </br>
>     **Description:** Return scores for neutral, positive, and negative which are the scores that make up the compound score. </br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1</br>
>     **Default:** False

### ML Algorithms

_TruncantedSVD_
> #### Description
> From sklearn. Used for dimension reduction (especially on a TFIDF). This is also known in text analytics as Latent Semantic Analysis or LSA. Returns fields prepended with "SVD_". See [http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html](http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html)
> #### Syntax
> ```fit TruncatedSVD <fields> [into <model name>] k=<int>```</br><br>
> The `k` option sets the number of components to change the data into. It is important that the value is less than the number of features or documents. The documentation on the algorithm recommends to be set to at least 100 for LSA.

_LatentDirichletAllocation_
> #### Description
> From sklearn. Used for dimension reduction. This is also known as LDA. Returns fields prepended with "LDA_". See [http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html](http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html)
> #### Syntax
> ```fit LatentDirichletAllocation <fields> [into <model name>] k=<int>```</br><br>
> The `k` option sets the number of components (topics) to change the data into. It is important that the value is less than the number of features or documents. 
 
_NMF_
> #### Description
> From sklearn. Used for dimension reduction. This is also known as Non-Negative Matrix Factorization. Returns fields prepended with "NMF_". See [http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.NMF.html](http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.NMF.html)
> #### Syntax
> ```fit NMF <fields> [into <model name>] [k=<int>]```</br><br>
> The `k` option sets the number of components (topics) to change the data into. It is important that the value is less than the number of features or documents. 

_TFBinary_
> #### Description
> A modified implemenation of TfidfVectorizer from sklearn. The current MLTK version has TfidfVectorizer but it does not allow the option of turning off IDF or setting `binary` to True. This is to create a document-term matrix of whether the document has the given term or not. See [http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html](http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
> #### Syntax
> ```fit TFBinary <fields> [into <model name>] [max_features=<int>] [max_df=<int>] [min_df=<int>] [ngram_range=<int>-<int>] [analyzer=<str>] [norm=<str>] [token_pattern=<str>] [stop_words=english] [use_idf=<true|false>] [binary=<true|false>]```</br><br> 
> In this implementation, the following settings are already set in order to create a binary output: `use_idf` is set to False, `binary` has been set to True, and `norm` has been set to None. The rest of the settings and options are exactly like the current MLTK (3.4) implementation.

_MinMaxScaler_
> #### Description
> From sklearn. Transforms each feature to a given range. Returns fields prepended with "MMS_". See [http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html](http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html)
> #### Syntax
> ```fit MinMaxScaler <fields> [into <model name>] [copy=<true|false>] [feature_range=<int>-<int>]```</br><br>
> Default `feature_range=0-1` `copy=true`.

_LinearSVC_
> #### Description
> From sklearn. Similar to SVC with parameter kernel=’linear’, but implemented in terms of liblinear rather than libsvm, so it has more flexibility in the choice of penalties and loss functions and should scale better to large numbers of samples. See [http://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html](http://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html)
> #### Syntax
> ```fit LinearSVC <fields> [into <model name>] [gamma=<int>] [C=<int>] [tol=<int>] [intercept_scaling=<int>] [random_state=<int>] [max_iter=<int>] [penalty=<l1|l2>] [loss=<hinge|squared_hinge>] [multi_class=<ovr|crammer_singer>] [dual=<true|false>] [fit_intercept=<true|false>]```</br><br>
> The `C` option sets the penalty parameter of the error term.

_ExtraTreesClassifier_
> #### Description
> From sklearn. This class implements a meta estimator that fits a number of randomized decision trees (a.k.a. extra-trees) on various sub-samples of the dataset and use averaging to improve the predictive accuracy and control over-fitting. See [http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html](http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html)
> #### Syntax
> ```fit ExtraTreesClassifier <fields> [into <model name>] [random_state=<int>] [n_estimators=<int>] [max_depth=<int>] [max_leaf_nodes=<int>] [max_features=<int|auto|sqrt|log|None>] [criterion=<gini|entropy>]```</br><br>
> The `n_estimators` option sets the number of trees in the forest, defaults to 10.

### Support
Support will be provided through Splunkbase (click on Contact Developer) or Splunk Answers or [submit an issue in Github](https://github.com/geekusa/nlp-text-analytics/issues/new). Expected responses will depend on issue and as time permits, but every attempt will be made to fix within 2 weeks. 

### Documentation
This README file constitutes the documenation for the app and will be kept upto date on [Github](https://github.com/geekusa/nlp-text-analytics/blob/master/README.md) as well as on the Splunkbase page.

### Known Issues
Version 7.0.0 introduced an issue that causes errors in the ML Toolkit when using free or developer's license see [https://answers.splunk.com/answers/654411/splunk-710-upgrade-of-free-version-finalizes-searc.html](https://answers.splunk.com/answers/654411/splunk-710-upgrade-of-free-version-finalizes-searc.html). Fixed as of 7.1.2.
Splunk SDK crashes when too much data is sent through it, gets a buffer error. See [https://github.com/splunk/splunk-sdk-python/issues/150](https://github.com/splunk/splunk-sdk-python/issues/150). Workaround would be to used the sample command to down sample the data until it works. 

### Release Notes
Upgraded splunklib to 1.6.16. Updated to local jquery 3.6.0 for Splunk 8.2 compatibility.
