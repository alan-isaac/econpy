"""
Produce word counts for input file.

Sample use:

	wordfreq.py filename

TODO: use collections.Counter (Python 3+)
"""

from __future__ import division, with_statement
import sys, string
from itertools import cycle, ifilter, izip
from collections import defaultdict

class WordFreq:
	"""Summarize text file word counts.
	"""
	def __init__(self, filename, **kw):
		self.filename = filename
		self.params = kw
		self.word_hash = None
		self.ct_words = 0
		self.ct_longwords = 0
		#might want, e.g., start_after = ".. begin wordcount",
		self.start_after = ''
		self.wordsize_min = 3
		self.freq_min = 1
		self.describe()
	def describe(self):
		"""
		Return None.
		"""
		start_after = self.start_after
		wordsize_min = self.wordsize_min
		chars2strip = string.punctuation
		ct_words = 0
		ct_longwords = 0
		word_hash = defaultdict(int)
		with open(self.filename,'r') as fh:
			for line in fh:
				while start_after:
					if line.startswith(start_after):
						start_after = False
					continue
				line.strip()
				for word in line.split():
					word = word.strip(chars2strip)
					if word:
						ct_words += 1
					if len(word) >= wordsize_min:
						ct_longwords += 1
						word_hash[word] += 1
		self.word_hash=word_hash
		self.ct_words=ct_words
		self.ct_longwords=ct_longwords
	def summarize(self):
		freq_min = self.freq_min
		word_hash = self.word_hash
		summary = dict(
			word_hash=word_hash,
			ct_words=self.ct_words,
			ct_longwords=self.ct_longwords,
			wordsize_min=self.wordsize_min
			)
		fmt = "\n%24s %6d"
		#create word list in alpha order
		acceptable = ((k,v) for k,v in word_hash.iteritems() if v>=freq_min)
		summary['alpha'] = ''.join( fmt%(k,v) for k,v in sorted(acceptable) )
		#create word list in occurrence order
		acceptable = ((k,v) for k,v in word_hash.iteritems() if v>=freq_min)
		summary['occur'] = ''.join(
			fmt%(k,v)
			for k,v in sorted(acceptable, key = lambda x: (-x[1], x[0]) ))
		result = """
		Results for 'longer' words (length >= %(wordsize_min)d):
		
		=================================================
		=============== WORD COUNT ======================
		=================================================
		Total number of words: %(ct_words)d
		Total number of 'longer' words : %(ct_longwords)d


		=================================================
		=============== ALPHA ORDER =====================
		=================================================
		%(alpha)s


		=================================================
		============ OCCURRENCE ORDER ===================
		=================================================
		%(occur)s
		"""
		return result%summary

def main():
	filename = sys.argv[1]
	wf = WordFreq(filename)
	print( wf.summarize() )

if __name__ == '__main__':
	main()

