'''A file to show this folder is a python module and define shared functions and objects'''
import unicodedata

def normalize_unicode(text):
    '''to normalize text contents before adding them to DB'''
    return unicodedata.normalize('NFKC', text)
    