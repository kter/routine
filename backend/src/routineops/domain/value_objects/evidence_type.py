from enum import Enum


class EvidenceType(str, Enum):
    NONE = "none"
    TEXT = "text"
    IMAGE = "image"
