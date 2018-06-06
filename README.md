# NLP Text Analytics Splunk App

The intent of this app is to provide a simple interface for analyzing text in Splunk using python natural language processing libraries (currently just NLTK 3.3). The app provides custom commands and dashboards to show how to use. 

Available at:

[Github](https://github.com/geekusa/nlp-text-analytics)

Version: 0.1

##### Author: Nathan Worsham 
Created for MSDS692 Data Science Practicum I at Regis University, 2018 </br>
See [associated blog](https://github.com/geekusa/nlp-text-analytics/blob/master/PROJECT_FILES/blog.md) for detailed information on the project creation.

## Description and Use-cases

Have you ever wanted to perform advanced text analytics inside Splunk? Splunk has some ways to handle text but also lacks some more advanced features that NLP libraries can offer. This can also benefit use-cases that involve using Splunk’s ML Toolkit.

## Requirements
Splunk ML Toolkit 3.2 or greater [https://splunkbase.splunk.com/app/2890/](https://splunkbase.splunk.com/app/2890/)
Wordcloud Custom Visualization [https://splunkbase.splunk.com/app/3212/](https://splunkbase.splunk.com/app/3212/)
Parallel Coordinates Custom Visualization [https://splunkbase.splunk.com/app/3137/](https://splunkbase.splunk.com/app/3137/)

## How to use

### Install

Normal app installation can be followed from https://docs.splunk.com/Documentation/AddOns/released/Overview/AboutSplunkadd-ons. Essentially download app and install from Web UI or extract file in $SPLUNK\_HOME/etc/apps folder.

### Example Texts

The app comes with an example Gutenberg texts formatted as CSV lookups.

### Custom Commands

_cleantext_
> #### Description
> Tokenize and normalize text (remove punctuation, digits, change to base\_word). Different options result in better and slower cleaning. base\_type="lemma\_pos" being the slowest option, base\_type="lemma" assumes every word is a noun, which is faster but still results in decent lemmatization. Many fields have a default already set, textfield is only required field. By default results in a multi-valued field which is ready for used with stats count by.
> #### Syntax
> \* | cleantext textfield=\<field> [default\_clean=\<bool>] [remove\_urls=\<bool>] [remove\_stopwords=\<bool>] [base\_word=\<bool>] [base\_type=\<string>] [mv=\<bool>] [pos\_tagset=\<string>]
> ##### Required Arguments
> **textfield** </br>
>     **Syntax:** textfield=\<field> </br>
>     **Description:** The search field that contains the text that is the target of the analysis. </br>
>     **Usage:** Option only takes a single field
> ##### Optional Arguments
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
>     **Description:** Sets the value for the type of word base to use, dependant on base\_word being set to True. Lemmatization without POS tagging (option lemma) assumes every word is a noun but results in a comprable but faster output. Lemmatization with POS tagging (lemma\_pos) is slower but more precice, also adds a new field of `pos_tag`. Porter Stemmer is used when the option is set to stem.</br>
>     **Usage:** Possible values are lemma, lemma\_pos, stem</br>
>     **Default:** True
> 
>**mv** </br>
>     **Syntax:** mv=\<bool> </br>
>     **Description:** Returns the output as a multi-value field (ready for use with mvexpand), otherwise returns as a space seperated string. </br>
>     **Usage:** Boolean value. True or False; true or false, t or f, 0 or 1</br>
>     **Default:** True
> 
>**pos\_tagset** </br>
>     **Syntax:** pos\_tagset=\<string> </br>
>     **Description:** Sets the option for the tagset used--Advanced Perceptron tagger (None) or universal. </br>
>     **Usage:** None or universal</br>
>     **Default:** None

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

### Support
Support will be provided through Splunkbase (click on Contact Developer) or Splunk Answers or [submit an issue in Github](https://github.com/geekusa/nlp-text-analytics/issues/new). Expected responses will depend on issue and as time permits, but every attempt will be made to fix within 2 weeks. 

### Documentation
This README file constitutes the documenation for the app and will be kept upto date on [Github](https://github.com/geekusa/nlp-text-analytics/blob/master/README.md) as well as on the Splunkbase page.

### Known Issues
Version 7.0.0 introduced an issue that causes errors in the ML Toolkit when using free or developer's license see [https://answers.splunk.com/answers/654411/splunk-710-upgrade-of-free-version-finalizes-searc.html](https://answers.splunk.com/answers/654411/splunk-710-upgrade-of-free-version-finalizes-searc.html). Has not been fixed as of 7.1.1.

### Release Notes
Initial Beta Release
