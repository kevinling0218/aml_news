from string import punctuation


# Remove numbers
def remove_numbers(s):
    return ''.join([c for c in s if not c.isdigit()])


# Remove punctuations
def remvoe_punctuation(s):
    return ''.join(c for c in s if c not in punctuation)


# Remove single character
def remove_single_character(s):
    return ' '.join(w for w in s.split() if len(w) > 1)
