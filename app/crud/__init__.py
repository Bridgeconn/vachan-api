'''An empty file to show this folder is a python module'''
import unicodedata

def normalize_unicode(text):
    '''to normalize text contents before adding them to DB'''
    return unicodedata.normalize('NFC', text)
    