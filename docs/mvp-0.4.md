# MVP 0.4 — Resolution, binding and functional evidence

The validation layer now correlates three independent signals:

1. hardware identity and resolved driver candidates;
2. kernel driver/module binding exposed by PCI/sysfs inventory;
3. non-invasive functional test results.

The resulting component record exposes `binding`, `functional` and `validation` fields. A functional pass is evidence that a subsystem is exposed and responding to the selected check; it is not a guarantee that every feature works.

Firmware remains a separate evidence channel. The project deliberately does not claim that firmware is loaded merely because a file exists on disk.

`maclinux test --json` now returns the correlated component records.
