import re
from dataclasses import dataclass
from fnmatch import fnmatch


SENSITIVE_FILENAME_PATTERNS = [
    ".env", "*.env", ".env.*",
    "*.key", "*.pem", "*.p12", "*.pfx",
    "secrets.*", "credentials.*",
    "*secret*", "*credential*",
]

SENSITIVE_CONTENT_PATTERNS = [
    (r'(API_KEY|SECRET_KEY|SECRET|PASSWORD|TOKEN|PRIVATE_KEY|ACCESS_KEY|AUTH_KEY)\s*=\s*(\S+)', r'\1=****'),
    (r'(sk-[a-zA-Z0-9]{20,})', r'sk-****'),
    (r'(ghp_[a-zA-Z0-9]{10,})', r'ghp_****'),
    (r'(gho_[a-zA-Z0-9]{10,})', r'gho_****'),
    (r'(glpat-[a-zA-Z0-9\-]{10,})', r'glpat-****'),
    (r'-----BEGIN (RSA |EC |)PRIVATE KEY-----', r'-----BEGIN \1PRIVATE KEY----- [REDACTED]'),
]


@dataclass
class SensitiveMatch:
    pattern: str
    count: int


class GuardLayer:
    def is_sensitive_filename(self, filename: str) -> bool:
        name = filename.split("/")[-1]
        return any(fnmatch(name, pat) for pat in SENSITIVE_FILENAME_PATTERNS)

    def mask_content(self, content: str) -> tuple[str, list[SensitiveMatch]]:
        masked = content
        matches: list[SensitiveMatch] = []
        for pattern, replacement in SENSITIVE_CONTENT_PATTERNS:
            new_content, count = re.subn(pattern, replacement, masked)
            if count > 0:
                matches.append(SensitiveMatch(pattern=pattern, count=count))
                masked = new_content
        return masked, matches
