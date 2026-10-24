"""Pure-Python substring search, independent of the Qt UI."""

def kmp_contains(haystack, needle):
    """Case-insensitive substring match using a KMP prefix table."""
    pattern=needle.casefold().strip()
    if not pattern:return True
    text=haystack.casefold()
    lps=[0]*len(pattern)
    prefix=0
    for pos in range(1,len(pattern)):
        while prefix and pattern[pos]!=pattern[prefix]:prefix=lps[prefix-1]
        if pattern[pos]==pattern[prefix]:prefix+=1
        lps[pos]=prefix
    matched=0
    for char in text:
        while matched and char!=pattern[matched]:matched=lps[matched-1]
        if char==pattern[matched]:matched+=1
        if matched==len(pattern):return True
    return False
