import re

from bs4 import Tag

class CitationExtractor:
    def __init__(self):
        # regex from ChatGPT
        self.citation_pattern = re.compile(
            r"""
            (                                   # capture one citation
                [A-Z][A-Za-z .,&:\-()']+        # start with a capitalized author
                .*?                             # non-greedy everything else
                \d{4}                           # require a year somewhere
                .*?                             # rest of citation
                (?=                             # stop before next citation
                    \s+[A-Z][A-Za-z .,&:\-()']+\s.*?\d{4}    # next author-year pattern
                    |$                          # or end of string
                )
            )
            """,
            re.VERBOSE | re.DOTALL
        )
        
    def tag_to_citations(self, tag: Tag, min_length: int = 75):
        """
        Pull all citations nested in a bs4.Tag object.

        Args:
            tag (bs4.Tag): tag to search for citations within
            min_length (int): filter out any matched citations less than this many characters
        """
        text = tag.get_text(separator=" ", strip=True)
        matches = self.citation_pattern.findall(text)
        filtered_matches = [re.sub(r'\s+', ' ', m) for m in matches if len(m) >= min_length] # Normalize whitespace characters and 'citations' that are too short
        return filtered_matches