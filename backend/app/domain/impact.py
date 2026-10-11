"""Interpret bounded query rows without inventing graph edges."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ImpactPath:
    node_ids: tuple[str, ...]
    relationship_types: tuple[str, ...]
    evidence_ids: tuple[str, ...]

    @property
    def hops(self) -> int:
        return len(self.relationship_types)


def ordered_callers(paths: list[ImpactPath]) -> list[str]:
    """One caller per ID, nearest first; retain full paths separately."""
    ordered = sorted(paths, key=lambda p: (p.hops, p.node_ids))
    return list(dict.fromkeys(path.node_ids[0] for path in ordered))
