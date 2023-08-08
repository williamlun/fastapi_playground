import enum
import uuid


class OperatorType(enum.Enum):
    """operator of the alarm rule"""

    GT = "GREATER"
    LESS = "LE"
    GREATER_OR_EQUAL = "GREATER_OR_EQUAL"
    LESS_OR_EQUAL = "LESS_OR_EQUAL"
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"


class PointValue:
    _cached_point_path: dict[tuple[str, uuid.UUID], dict] = {}
