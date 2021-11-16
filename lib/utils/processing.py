
from difflib import SequenceMatcher


def suggest(dic, word, distance, maxSuggestion=3):
    return [i[1] for i in sorted([(distance(word1, word), word1) for word1 in dic], key=lambda x: x[0], reverse=True)[:maxSuggestion]]

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
