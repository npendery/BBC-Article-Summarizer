######################################################################################
# THis example is based on this blog post
# http://glowingpython.blogspot.in/2014/09/text-summarization-with-nltk.html
# Thanks to TheGlowingPython
######################################################################################


from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
import urllib.request
from bs4 import BeautifulSoup

class ArticleSummarizer:
    def __init__(self, min_cut=0.1, max_cut=0.9):
        self._min_cut = min_cut
        self._max_cut = max_cut
        self._stopwords = set(stopwords.words('english') + list(punctuation))

    def get_text_from_url(self, url):
        page = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(page, "html.parser")
        paragraphs = soup.find('div', property="articleBody").find_all('p')
        text = ' '.join(map(lambda p: p.text, paragraphs))
        return soup.title.text, text

    def summarize(self, text, number_of_top_sentences):
        sentences = sent_tokenize(text)
        assert number_of_top_sentences <= len(sentences)

        word_sent_list = [word_tokenize(sentence.lower()) for sentence in sentences]

        frequencies = self._compute_frequencies(word_sent_list)

        sentence_ranking = defaultdict(int)

        for i, sentence in enumerate(word_sent_list):
            for word in sentence:
                if word in frequencies:
                    sentence_ranking[i] += frequencies[word]

        top_sentences_index = nlargest(
            number_of_top_sentences,
            sentence_ranking,
            key=sentence_ranking.get
        )

        return [sentences[index] for index in top_sentences_index]

    def _compute_frequencies(self, sentence_list):
        freq = defaultdict(int)
        for sentence in sentence_list:
            for word in sentence:
                if word not in self._stopwords:
                    freq[word] += 1

        max_freq = float(max(freq.values()))

        for word in list(freq.keys()):
            freq[word] = freq[word]/max_freq

            if freq[word] >= self._max_cut or freq[word] <= self._min_cut:
                del freq[word]

        return freq

#####################################################################################

summarizer = ArticleSummarizer()

someUrl = "http://www.bbc.com/news/technology-39973787"

textOfUrl = summarizer.get_text_from_url(someUrl)

summary = summarizer.summarize(textOfUrl[1], 3)

print(textOfUrl[0])
for sent in summary:
    print("\n")
    print(sent)
