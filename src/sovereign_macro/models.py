from dataclasses import asdict, dataclass
from datetime import date
import math


class DataError(ValueError):
    """A machine-readable validation failure."""


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


@dataclass(frozen=True)
class Observation:
    iso3: str
    metric: str
    value: float
    period: str
    currency: str = ""
    unit: str = "percent"
    provider: str = ""
    dataset: str = ""
    series: str = ""
    edition: str = ""
    classification: str = "observation"
    source_date: str = ""
    retrieved_at: str = ""
    url: str = ""
    raw_sha256: str = ""
    tenor_years: float | None = None
    yield_type: str = ""
    compounding: str = "provider convention (not converted)"
    redistribution: str = "pending"

    def to_dict(self):
        return asdict(self)

    def valid_on(self, as_of: date, stale_days=7):
        if not finite(self.value):
            raise DataError("NONFINITE")
        if self.unit != "percent" or self.tenor_years not in (5, 10):
            raise DataError("YIELD_CONTRACT")
        try:
            observed = date.fromisoformat(self.period)
        except ValueError as exc:
            raise DataError("FREQUENCY_OR_DATE") from exc
        if observed > as_of:
            raise DataError("FUTURE_OBSERVATION")
        if (as_of-observed).days > stale_days:
            raise DataError("STALE")
        return True
