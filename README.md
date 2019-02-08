

<h1 align="center"> 
  <strong>Text Analyzor</strong>
</h1>

<div align="center">
  <img src="https://img.icons8.com/cotton/128/000000/document.png">
  A text analyzer that extracts useful features from documents in a corpus.
</div>

<div align="center">
  <a href="">Visit here</a>
</div>

## Introduction

In information retrieval, the search engine will use TF-IDF to rank the importance of a keyword to a document in a corpus.

TF-IDF is combined with the concept of TF and IDF.

Cosine Similarity is calculated to show the re

### TF Term Frequency

Term Frequency measures how frequently a term occurs in a document. Since every document is different in length, it is possible that a term would appear much more times in long documents than shorter ones. Thus, the term frequency is often divided by the document length (aka. the total number of terms in the document) as a way of normalization.

The term frequency (TF) of a word in a document **F** is defined as:

<img src="../../static/charts/tf-idf_3.png">

Term frequency of a word in a corpus of documents:

<div align="center">
C = {F1,F2,...,Fk}
</div>

is

<img src="../../static/charts/tf-idf_2.png">

### IDF Inverse Document Frequency

Inverse Document Frequency measures how important a term is. While computing TF, all terms are considered equally important. However it is known that certain terms, such as "is", "of", and "that", may appear a lot of times but have little importance. Thus we need to weigh down the frequent terms while scale up the rare ones.

Given a corpus of documents C = {F1 , F2 , . . . , Fk }, the inverse document frequency (IDF) of a word w is given by:

<img src="../../static/charts/tf-idf_1.png">

where |A| denotes the size of set A.

## TF-IDF

Given a corpus C, the TFIDF score of a word w in a document F ∈ C is given by:

<img src="../../static/charts/tf-idf_4.png">

## Cosine Similarity

Cosine similarity is a measure of similarity between two non-zero vectors of an inner product space that measures the cosine of the angle between them. Here we use Cosine similarity to measure similarity between any two documents in corpus.

The cosine similarity between two documents F , F ′ in corpus C is defined as:

<img src="../../static/charts/tf-idf_5.png">

where F ∩ F ′ indicates the set words present in both files. Note that, by definition, cos(F, F ′) = cos(F ′, F ).

## How to run

The program has a CLI that shows the usage of it

```sh
$ python TextAnalyzer.py -h

usage: TextAnalyzer.py [-h] [--master MASTER] [--idfvalues IDFVALUES]
                       [--other OTHER]
                       {TF,IDF,TFIDF,SIM,TOP} input output

Text Analysis through TFIDF computation

positional arguments:
  {TF,IDF,TFIDF,SIM,TOP}
                        Mode of operation
  input                 Input file or list of files.
  output                File in which output is stored

optional arguments:
  -h, --help            show this help message and exit
  --master MASTER       Spark Master (default: local[20])
  --idfvalues IDFVALUES
                        File/directory containing IDF values. Used in TFIDF
                        mode to compute TFIDF (default: idf)
  --other OTHER         Score to which input score is to be compared. Used in
                        SIM mode (default: None)
```

If TF option is given, the program will calculate the Term Frequency. For example:

```sh
$ python TextAnalyzer.py TF data/masc_500k_texts/written/fiction/hotel-california.txt hotel-california.tf --master local[8]
```

If TOP option is given, the program will output a file with the top 20 Term Frequency words in a document. For example:

```sh
$ python TextAnalyzer.py TOP face-to-face.tf face-to-face.top --master local[8]
```

If IDF option is given, the program will compute IDF of each term in the corpus. For example:

```sh
$ python TextAnalyzer.py IDF "masc_500k_texts/*/*" ans.idf
```

If TFIDF option is given, the program will compute TFIDF of each term in a document. For example:

```sh
$ python TextAnalyzer.py TFIDF hotel-california.tf hotel-california.tfidf --idfvalues anc.idf --master local[8]
```

If SIM option is given, the program will compute Cosine Similarity between two documents in the corpus. For example:

```sh
$ python TextAnalyzer.py SIM spam.tfidf spam-face-to-face.sim --other face-to-face.tfidf --master local[8]
```

## Reference

* http://www.tfidf.com/

* https://en.wikipedia.org/wiki/Cosine_similarity

<a href="https://icons8.com/icon/65355/document" style="display:none;">Document icon by Icons8</a>