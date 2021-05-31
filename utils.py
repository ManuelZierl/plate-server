import re


# todo: needs testing
def is_german_plate(plate_str: str) -> bool:
    if re.match(r"^[A-ZÄÖÜ]{1,3}\-[A-Z]{1,2}[1-9]{1}[0-9]{0,3}$", plate_str):
        return True
    return False


# todo: test
def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s2) == 0:
        return len(s1)
    elif len(s1) == 0:
        return len(s2)
    elif s1[0] == s2[0]:
        return levenshtein_distance(s1[1:], s2[1:])
    else:
        return 1 + min(
            levenshtein_distance(s1[1:], s2),
            levenshtein_distance(s1, s2[1:]),
            levenshtein_distance(s1[1:], s2[1:])
        )


"""
print(levenshtein_distance("abc", "abc"), 0)
print(levenshtein_distance("bca", "abc"), 2)
print(levenshtein_distance("qwe", "abc"), 3)
"""
# print(levenshtein_distance("myplate34879687b876b87b6767b765", "MEB333"))
