import re
from typing import Tuple, Optional
from .normalize_whitespace import norm_ws

_PREFIX_RE = re.compile(
    r"^(dr|prof|professor)\.?\s+",
    flags=re.I,
)

_CREDENTIAL_RE = re.compile(
    r",?\s*(Ph\.?D\.?|Ed\.?D\.?|D\.?Ed\.?|M\.?D\.?|D\.?O\.?|MFA|M\.?F\.?A\.?|MBA|M\.?B\.?A\.?|"
    r"MS|M\.?S\.?|MA|M\.?A\.?|MEd|M\.?Ed\.?|JD|J\.?D\.?|Esq\.?|RN|FNP|PNP|DNP|CFA|CFP|CPA)\b\.?",
    flags=re.I,
)

_SUFFIX_RE = re.compile(
    r",?\s*(Jr\.?|Sr\.?|II|III|IV|V)$",
    flags=re.I,
)


def split_name(full: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Robust-ish name splitter:
    - Strips prefixes like Dr., Prof.
    - Strips common degree credentials.
    - Keeps Jr./Sr./II/etc as part of last name.
    """
    full = norm_ws(full) or ""
    if not full:
        return None, None

    full = _PREFIX_RE.sub("", full)
    full = _CREDENTIAL_RE.sub("", full)
    suffix = None
    m = _SUFFIX_RE.search(full)
    if m:
        suffix = m.group(1)
        full = full[: m.start()].strip()

    parts = full.split()
    if not parts:
        return None, None
    if len(parts) == 1:
        return parts[0], suffix

    first = " ".join(parts[:-1])
    last = parts[-1]
    if suffix:
        last = f"{last} {suffix}"
    return first or None, last or None