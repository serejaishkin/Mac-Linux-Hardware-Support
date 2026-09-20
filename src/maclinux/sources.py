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
        "c5c7fac4e6da061ededd4c46545930ff7cdc0529", "GPL-2.0", firmware="facetimehd-firmware",
    ),
    "applespi": SourceSpec(
        "applespi", "git", "https://github.com/torvalds/linux",
        "mainline", "GPL-2.0",
    ),
    "snd_hda_macbookpro": SourceSpec(
        "snd_hda_macbookpro", "git", "https://github.com/davidjo/snd_hda_macbookpro",
        "89b22ff90b86468b186706861dd18663562defa7", "GPL-2.0",
    ),
}


def get_source(driver: str) -> SourceSpec | None:
    return SOURCES.get(driver)
