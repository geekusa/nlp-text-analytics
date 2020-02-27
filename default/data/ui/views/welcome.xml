<form hideEdit="true">
  <label>Welcome</label>
  <fieldset submitButton="false"></fieldset>
  <row>
    <panel>
      <title>NLP Terminology</title>
      <input id="long_link_input" type="link" token="nlp">
        <label></label>
        <fieldForLabel>Terminology</fieldForLabel>
        <fieldForValue>Terminology</fieldForValue>
        <search>
          <query>| inputlookup nlp_terminology.csv</query>
        </search>
        <default>NLP</default>
        <initialValue>NLP</initialValue>
      </input>
      <single>
        <search>
          <query>| inputlookup nlp_terminology.csv 
| where Terminology=="$nlp$"
| table Explanation Link</query>
          <earliest>-24h@h</earliest>
          <latest>now</latest>
        </search>
        <option name="colorMode">block</option>
        <option name="drilldown">all</option>
        <option name="height">56</option>
        <option name="rangeColors">["0x53a051","0x0877a6","0xf8be34","0xf1813f","0xdc4e41"]</option>
        <option name="refresh.display">progressbar</option>
        <option name="useColors">1</option>
        <drilldown>
          <link target="_blank">https://en.wikipedia.org/wiki/$row.Link$</link>
        </drilldown>
      </single>
    </panel>
  </row>
  <row>
    <panel>
      <html>
        <div>
          The intent of this app is to provide a simple interface for analyzing text in Splunk using python natural language processing libraries (currently just NLTK 3.4.5). The app provides custom commands (currently 4), additional ML algorithms (currently 7) to use with Splunk's ML Toolkit, and dashboards to show how to use. The app is also packaged with Gutenberg texts (currenlty 3) and the "20 newsgroups" dataset formatted as CSV lookups. 
        </div>
        <h1>Requirements</h1>
        <div>
<a href="https://splunkbase.splunk.com/app/2890/">Splunk ML Toolkit 3.2 or greater</a>
          <br/>
<a href="https://splunkbase.splunk.com/app/3212/">Wordcloud Custom Visualization</a> (preferred) OR <a href="https://splunkbase.splunk.com/app/1603/">Splunk Dashboard Examples</a>
          <br/>
<a href="https://splunkbase.splunk.com/app/3137/">Parallel Coordinates Custom Visualization</a>
          <br/>
<a href="https://splunkbase.splunk.com/app/3767/">Force Directed App For Splunk</a>
          <br/>
<a href="https://splunkbase.splunk.com/app/3514/">Halo - Custom Visualization</a>
          <br/>
<a href="https://splunkbase.splunk.com/app/3112/">Sankey Diagram - Custom Visualization</a>
          <br/>
        </div>
        <h1>Example Texts</h1>
        <div>The app comes with example Gutenberg texts formatted as CSV lookups along with the popular "20 newsgroups" dataset. Load them with the syntax <pre>| inputlookup &lt;filename.csv&gt;</pre>
        </div>
        <h3>Text Names</h3>
        <pre>20newsgroups.csv
moby_dick.csv
peter_pan.csv
pride_prejudice.csv</pre>
        <h1>Custom Commands</h1>
        <h2>bs4</h2>
        <div> A wrapper for BeautifulSoup4 to extract html/xml tags and text from them to use in Splunk. A wrapper script to bring some functionality from BeautifulSoup to Splunk. Default is to get the text and send it to a new field 'get\_text', otherwise the selection is returned in a field named 'soup'. Default is to use the 'lxml' parser, though you can specify others, 'html5lib' is not currently included. The find methods can be used in conjuction, their order of operation is find &gt; find\_all &gt; find\_child &gt; find children. Each option has a similar named option appended '\_attrs' that will accept inner and outer quoted key:value pairs for more precise selections.
        </div>
        <h3>Syntax</h3>
        <pre>* | bs4 textfield=&lt;field&gt; [get_text=&lt;bool&gt;] [get_text_label=&lt;string&gt;] [parser=&lt;string&gt;] [find=&lt;tag&gt;] [find_attrs=&lt;quoted_key:value_pairs&gt;] [find_all=&lt;tag&gt;] [find_all_attrs=&lt;quoted_key:value_pairs&gt;] [find_child=&lt;tag&gt;] [find_child_attrs=&lt;quoted_key:value_pairs&gt;] [find_children=&lt;tag&gt;] [find_children_attrs=&lt;quoted_key:value_pairs&gt;]</pre>
        <h2>cleantext</h2>
        <div>Tokenize and normalize text (remove punctuation, digits, change to base_word). Different options result in better and slower cleaning. base_type="lemma_pos" being the slowest option, base_type="lemma" assumes every word is a noun, which is faster but still results in decent lemmatization. Many fields have a default already set, textfield is only required field. By default results in a multi-valued field which is ready for used with stats count by. Optionally return special fields for analysis--pos_tags and ngrams as well as the original text.
        </div>
        <h3>Syntax</h3>
        <pre>* | cleantext textfield=&lt;field&gt; [keep_orig=&lt;bool&gt;] [default_clean=&lt;bool&gt;] [remove_urls=&lt;bool&gt;] [remove_stopwords=&lt;bool&gt;] [base_word=&lt;bool&gt;] [base_type=&lt;string&gt;] [mv=&lt;bool&gt;] [force_nltk_tokenize=&lt;bool&gt;] [pos_tagset=&lt;string&gt;] [custom_stopwords=&lt;comma_separated_string_list&gt;] [term_min_len=&lt;int&gt;] [ngram_range=&lt;int&gt;-&lt;int&gt;] [ngram_mix=&lt;bool&gt;]
	</pre> 
        <h2>similarity</h2>
        <div>A wrapper for NTLK distance metrics for comparing text to use in Splunk. Similarity (and distance) metrics can be used to tell how far apart to pieces of text are and in some algorithms return also the number of steps to make the text the same. These do not extract meaning, but are often used in text analytics to discover plagurism, conduct fuzzy searching, spell checking, and more. Defaults to using the Levenshtein distance algorithm but includes several other algorithms, include some set based algorithms. Can handle multi-valued comparisons with an option to limit to a given number of top matches. Multi-valued output can be zipped together or returned seperately.
        </div>
        <h3>Syntax</h3>
        <pre>* | similarity textfield=&lt;field&gt; comparefield=&lt;field&gt; [algo=&lt;string&gt;] [limit=&lt;int&gt;] [mvzip=&lt;bool&gt;]</pre>
        <h2>vader</h2>
        <div>Sentiment analysis using Valence Aware Dictionary and sEntiment Reasoner. Using option full_output will return scores for neutral, positive, and negative which are the scores that make up the compound score (that is just returned as the field "sentiment". Best to feed in uncleaned data as it takes into account capitalization and punctuation.
        </div>
        <h3>Syntax</h3>
        <pre>* | vader textfield=&lt;field&gt; [full_output=&lt;bool&gt;]</pre>
        <h1>ML Algorithms</h1>
        <h2>TruncantedSVD</h2>
        <div>From sklearn. Used for dimension reduction (especially on a TFIDF). This is also known in text analytics as Latent Semantic Analysis or LSA. Returns fields prepended with "SVD_". See <a href="http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html">http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html</a>
        </div>
        <h3>Syntax</h3>
        <pre>* | fit TruncantedSVD &lt;fields&gt; [into &lt;model name&gt;] k=&lt;int&gt;</pre>
        <h2>LatentDirichletAllocation</h2>
        <div>From sklearn. Used for dimension reduction. This is also known as LDA. Returns fields prepended with "LDA_". See <a href="http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html">http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html</a>
        </div>
        <h3>Syntax</h3>
        <pre>* | fit LatentDirichletAllocation &lt;fields&gt; [into &lt;model name&gt;] k=&lt;int&gt;</pre>
        <h2>NMF</h2>
        <div>From sklearn. Used for dimension reduction. This is also known as Non-Negative Matrix Factorization. Returns fields prepended with "NMF_". See <a href="http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.NMF.html">http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.NMF.html</a>
        </div>
        <h3>Syntax</h3>
        <pre>* | fit NFM &lt;fields&gt; [into &lt;model name&gt;] [k=&lt;int&gt;]</pre>
        <h2>TFBinary</h2>
        <div>A modified implemenation of TfidfVectorizer from sklearn. The current MLTK version has TfidfVectorizer but it does not allow the option of turning off IDF or setting `binary` to True. This is to create a document-term matrix of whether the document has the given term or not. In this implementation, the following settings are already set in order to create a binary output: `use_idf` is set to False, `binary` has been set to True, and `norm` has been set to None. The rest of the settings and options are exactly like the current MLTK (3.4) implementation. See <a href="http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html">http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html</a>
        </div>
        <h3>Syntax</h3>
        <pre>* | fit TFBinary &lt;fields&gt; [into &lt;model name&gt;] [max_features=&lt;int&gt;] [max_df=&lt;int&gt;] [min_df=&lt;int&gt;] [ngram_range=&lt;int&gt;-&lt;int&gt;] [analyzer=&lt;str&gt;] [norm=&lt;str&gt;] [token_pattern=&lt;str&gt;] [stop_wordsenglish] [use_idf=&lt;true|false&gt;] [binary=&lt;true|false&gt;]</pre>
        <h2>MinMaxScaler</h2>
        <div>From sklearn. Transforms each feature to a given range. Returns fields prepended with "MMS_". See <a href="http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html">http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html</a>
        </div>
        <h3>Syntax</h3>
        <pre>* | fit MinMaxScaler &lt;fields&gt; [into &lt;model name&gt;] [copy=&lt;true|false&gt;] [feature_range=&lt;int&gt;-&lt;int&gt;]</pre>
        <h2>LinearSVC</h2>
        <div>From sklearn. Similar to SVC with parameter kernel=’linear’, but implemented in terms of liblinear rather than libsvm, so it has more flexibility in the choice of penalties and loss functions and should scale better to large numbers of samples. See <a href="http://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html">http://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html</a>
        </div>
        <h3>Syntax</h3>
        <pre>* | fit LinearSVC &lt;fields&gt; [into &lt;model name&gt;] [gamma=&lt;int&gt;] [C=&lt;int&gt;] [tol=&lt;int&gt;] [intercept_scaling=&lt;int&gt;] [random_state=&lt;int&gt;] [max_iter=&lt;int&gt;] [penalty=&lt;l1|l2&gt;] [loss=&lt;hinge|squared_hinge&gt;] [multi_class=&lt;ovr|crammer_singer&gt;] [dual=&lt;true|false&gt;] [fit_intercept=&lt;true|false&gt;]</pre>
        <h2>ExtraTreesClassifier</h2>
        <div> From sklearn. This class implements a meta estimator that fits a number of randomized decision trees (a.k.a. extra-trees) on various sub-samples of the dataset and use averaging to improve the predictive accuracy and control over-fitting. See <a href="http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html">http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html</a>
        </div>
        <h3>Syntax</h3>
        <pre>* | fit ExtraTreesClassifier &lt;fields&gt; [into &lt;model name&gt;] [random_state=&lt;int&gt;] [n_estimators=&lt;int&gt;] [max_depth=&lt;int&gt;] [max_leaf_nodes=&lt;int&gt;] [max_features=&lt;int|auto|sqrt|log|None&gt;] [criterion=&lt;gini|entropy&gt;]</pre>
        <h1>Known Issues</h1>
	<div>Version 7.0.0 introduced an issue that causes errors in the ML Toolkit when using free or developer's license see <a href="https://answers.splunk.com/answers/654411/splunk-710-upgrade-of-free-version-finalizes-searc.html">https://answers.splunk.com/answers/654411/splunk-710-upgrade-of-free-version-finalizes-searc.html</a>. Issue was fixed in version 7.1.2.</div>
<div>Splunk SDK crashes when too much data is sent through it, gets a buffer error. See <a href="https://github.com/splunk/splunk-sdk-python/issues/150">https://github.com/splunk/splunk-sdk-python/issues/150</a>. Workaround would be to used the sample command to down sample the data until it works.</div>
      </html>
    </panel>
  </row>
</form>
