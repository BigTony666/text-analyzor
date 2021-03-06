import sys
import argparse
import numpy as np
from pyspark import SparkContext

def toLowerCase(s):
    """ Convert a sting to lowercase. E.g., 'BaNaNa' becomes 'banana'
    """
    return s.lower()

def stripNonAlpha(s):
    """ Remove non alphabetic characters. E.g. 'B:a,n+a1n$a' becomes 'Banana' """
    return ''.join([c for c in s if c.isalpha()])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Text Analysis through TFIDF computation',formatter_class=argparse.ArgumentDefaultsHelpFormatter)    
    parser.add_argument('mode', help='Mode of operation',choices=['TF','IDF','TFIDF','SIM','TOP']) 
    parser.add_argument('input', help='Input file or list of files.')
    parser.add_argument('output', help='File in which output is stored')
    parser.add_argument('--master',default="local[20]",help="Spark Master")
    parser.add_argument('--idfvalues',type=str,default="idf", help='File/directory containing IDF values. Used in TFIDF mode to compute TFIDF')
    parser.add_argument('--other',type=str,help = 'Score to which input score is to be compared. Used in SIM mode')
    args = parser.parse_args()
  
    sc = SparkContext(args.master, 'Text Analysis')


    if args.mode=='TF':
        # Read text file at args.input, compute TF of each term, 
        # and store result in file args.output. All terms are first converted to
        # lowercase, and have non alphabetic characters removed
        # (i.e., 'Ba,Na:Na.123' and 'banana' count as the same term). Empty strings, i.e., "" 
        # are also removed
        # Parameters Example:
        #    TF data/masc_500k_texts/written/fiction/hotel-california.txt hotel-california.tf --master local[8]
        #    TF "data/masc_500k_texts/spoken/face-to-face/*" face-to-face.tf --master local[8]
        """
            Line 1: SparkContext will call the textFile() to read a file from the local system
            Line 2: It will split the words by the blank space delimiter from all lines and flat them;
            Line 3: It will lowercase each word first, and then strip all non-alphabet character, then 
            create a tuple for each word in this format, (word, 1);
            Line 4: It will filter all those word that are only empty string ""
            Line 5: It will reduce to add all the tuples' value by key
            Line 6: It will save the result to 'output' path
        """
        lines = sc.textFile(args.input)
        lines.flatMap(lambda s: s.split(' '))\
            .map(lambda word: (stripNonAlpha(toLowerCase(word)), 1)) \
            .filter(lambda (key, _): key != "") \
            .reduceByKey(lambda x, y: x + y)\
            .saveAsTextFile(args.output)

    if args.mode=='TOP':
        # Read file at args.input, comprizing strings representing pairs of the form (TERM,VAL), 
        # where TERM is a string and VAL is a numeric value. Find the pairs with the top 20 values,
        # and store result in args.output
        # Parameters example:
        #    TOP face-to-face.tf face-to-face.top --master local[8]

        """
            Line 1: SparkContext will call the textFile() to read a file from the local system
            Line 2: It will map the value to its original data structure.
            Line 3: It will exchange the sequence of the elements in tuple
            Line 4: It will pick the top 20 words
            Line 5-7: It will open a file with the given name and mode, and use a for loop to write the result into file
        """
        lines = sc.textFile(args.input)
        topWords = lines.map(eval)\
            .map(lambda x: (x[1], x[0]))\
            .top(20)
        with open(args.output, 'w') as file:
            for word in topWords:
                file.write("({0}, {1}){2}".format(word[1], word[0], '\n'))

    if args.mode=='IDF':
        # Read list of files from args.input, compute IDF of each term,
        # and store result in file args.output.  All terms are first converted to
        # lowercase, and have non alphabetic characters removed
        # (i.e., 'Ba,Na:Na.123' and 'banana' count as the same term). Empty strings ""
        # are removed
        """
            Line 1: SparkContext will call the wholeTextFiles() to read all files in a whole directory from the local system
            Line 2: It will cache the files to reduce the load time
            Line 3: It will count the number of documents in this corpus
            Line 4: It will split the words by the blank space delimiter from all lines in all files and flat them;
            Line 5: It will lowercase each word first, and then strip all non-alphabet character
            Line 6: It will unique the elements
            Line 7: It will create a tuple for each word in this format, (word, 1);
            Line 8: It will filter all those word that are only empty string ""
            Line 9: It will reduce to add all the tuples' value by key
            Line 10: It will calculate the IDF by given formula
            Line 11: It will save the result to files
        """
        files = sc.wholeTextFiles(args.input)
        files.cache()
        corpusDocsSize = files.count()
        files.flatMapValues(lambda s: s.split()) \
            .mapValues(lambda raw: stripNonAlpha(toLowerCase(raw))) \
            .distinct() \
            .map(lambda word: (word[1], 1)) \
            .filter(lambda (key, _): key != "") \
            .reduceByKey(lambda x, y: x + y)\
            .mapValues(lambda val: np.log(corpusDocsSize / (val * 1.))) \
            .saveAsTextFile(args.output)

    if args.mode=='TFIDF':
        # Read  TF scores from file args.input the IDF scores from file args.idfvalues,
        # compute TFIDF score, and store it in file args.output. Both input files contain
        # strings representing pairs of the form (TERM,VAL),
        # where TERM is a lowercase letter-only string and VAL is a numeric value.
        # Parameters example:
        #     TFIDF hotel-california.tf hotel-california.tfidf --idfvalues anc.idf --master local[8]
        #     TFIDF face-to-face.tf face-to-face.tfidf --idfvalues anc.idf --master local[8]
        """
            Line 1: SparkContext will call the textFile() to read input file from the local system, and map the value to
            original data structure.
            Line 2: SparkContext will call the textFile() to read idfvalues file from the local system, and map the value to
            original data structure.
            Line 3: It will return an RDD containing all pairs of elements with matching keys in TF and IDF, it looks
            like SQL join.
            Line 4: It will calculate the tf-idf for each k-v pairs.
            Line 5: It will sort the result in descending sequence.
            Line 6: It will save the result to files.
        """
        TF = sc.textFile(args.input).map(eval)
        IDF = sc.textFile(args.idfvalues).map(eval)
        TF_IDF = TF.join(IDF)\
            .mapValues(lambda (tf, idf): tf * idf)\
            .sortBy(lambda (_, val): -val)\
            .saveAsTextFile(args.output)

        
    if args.mode=='SIM':
        # Read  scores from file args.input the scores from file args.other,
        # compute the cosine similarity between them, and store it in file args.output. Both input files contain
        # strings representing pairs of the form (TERM,VAL), 
        # where TERM is a lowercase, letter-only string and VAL is a numeric value.
        # Parameters example:
        #      SIM spam.tfidf spam-face-to-face.sim --other face-to-face.tfidf --master local[8]

        """
            Line 1: SparkContext will call the textFile() to read input file from the local system, and map the value to
            original data structure.
            Line 2: SparkContext will call the textFile() to read other file from the local system, and map the value to
            original data structure.
            Line 3: It will return an RDD containing all pairs of elements with matching keys in TF_IDF1 and TF_IDF2, it looks
            like SQL join.
            Line 4: It will return the values of each tuple
            LIne 5: It will do the multiplication between two TF_IDF of each value tuple
            Line 6: It will calculate the sum
            Line 7: It will calculate the mode of TF_IDF1
            Line 8: It will calculate the mode of TF_IDF2
            Line 9: It will calculate the cosin similarity
            Line 10-11: It will open a file named with output value and write the result to the file
        """

        TF_IDF1 = sc.textFile(args.input).map(eval)
        TF_IDF2 = sc.textFile(args.other).map(eval)
        dot_product = TF_IDF1.join(TF_IDF2) \
            .values() \
            .map(lambda (v1, v2): v1 * v2)\
            .reduce(lambda x, y: x + y)
        mode1 = np.sqrt(TF_IDF1.values().map(lambda x: x ** 2).reduce(lambda x, y: x + y))
        mode2 = np.sqrt(TF_IDF2.values().map(lambda x: x ** 2).reduce(lambda x, y: x + y))
        similarity = dot_product / (mode1 * mode2)
        with open(args.output, 'w') as file:
            file.write("{0}, {1}, {2}\n".format(args.input, args.other, similarity))
        




