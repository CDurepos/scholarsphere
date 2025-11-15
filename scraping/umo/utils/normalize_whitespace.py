import re
import unicodedata
from typing import Optional

# Replace any white space with a space
def norm_ws(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s).strip()
    return s or None