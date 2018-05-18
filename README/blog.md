# NLP Text Analytics Splunk App - Blog
##### Author: Nathan Worsham
##### Created for MSDS692 Data Science Practicum I at Regis University, 2018

Most projects for the Data Science Practicum revolved around collecting a dataset, cleaning it, exploring it, and then using machine learning algorithms on it to perform some sort of prediction or classification. I decided to go a bit outside the box and instead build a Splunk App for my project.

## Inspiration
I have built a few Splunk Apps previously so I was at least familiar with the practice and just before this class took a class on text analytics. I am fascinated with the subject and already had a few (internal) dashboards trying to do some text analytics. After I took the text analytics course though, I realized some of the shortcommings that Splunk had. Granted system logs are not something you think of immediately having natural language but that is not the only source of text in Splunk as it can consume anything human readable. In my own place of work, one immediate example that stood out in my mind was support ticket summaries and descriptions but I'm sure sources do not stop there. 

## Description

So given that information, the intent of this app is to provide a simple interface for analyzing text in Splunk using python natural language processing libraries (currently just NLTK 3.3). The app provides custom commands and dashboards to show how to use it.
