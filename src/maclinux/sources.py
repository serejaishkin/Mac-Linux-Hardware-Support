"""Driver source provenance registry."""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class SourceSpec:
    driver: str
    type: str
    repository: str
    revision: str
    license: str
    checksum: str = ""
    firmware: str = ""
    proprietary: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


SOURCES = {
    "facetimehd": SourceSpec(
        "facetimehd", "git", "https://github.com/patjak/facetimehd",
        "pinned-by-downstream-recipe", "GPL-2.0", firmware="facetimehd-firmware",
    ),
    "applespi": SourceSpec(
        "applespi", "git", "https://github.com/linux-surface/applespi",
        "pinned-by-downstream-recipe", "GPL-2.0",
    ),
    "snd_hda_macbookpro": SourceSpec(
        "snd_hda_macbookpro", "git", "https://github.com/davidjo/snd_hda_macbookpro",
        "pinned-by-downstream-recipe", "GPL-2.0",
    ),
}


def get_source(driver: str) -> SourceSpec | None:
    return SOURCES.get(driver)
