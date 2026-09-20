# Development

## Workflow

1. Detect the physical Mac model.
2. Collect PCI, USB, ACPI and DMI information.
3. Identify the exact device and existing Linux driver.
4. Check kernel compatibility.
5. Check firmware requirements.
6. Build/install through the appropriate distribution adapter.
7. Run a functional hardware test.
8. Record the result in the compatibility database.

## Useful diagnostics

```bash
uname -a
cat /sys/devices/virtual/dmi/id/product_name
cat /sys/devices/virtual/dmi/id/product_version
lspci -nn
lsusb
dmesg
journalctl -k
v4l2-ctl --list-devices
lsmod
```

Hardware-dependent tests require real Apple machines. CI can additionally cover build-only compatibility.
