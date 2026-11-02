# NOT-IN-BUILD: ufispace-bsp-utils

**Status: present for reference. Not built into the image. Not verified. Not supported.**

Hardware-vendor support is out of scope for this project. See the "Hardware support scope" section of the
[`build-iso` README](https://github.com/i-danos/build-iso#hardware-support-scope). This directory is kept in the tree for reference only;
the project makes no commitment to build, test or maintain it. Last commit here: 2852d4b 2026-08-23.

## What this is

- `python3-ufispace-bsp-utils`: Python Ufi Space board support package
- `python3-ufispace-bsp-sfp-helper`: Ufi Space board support package SFP helper library
- `ufispace-stat-led-control`: Package to control the STAT led

## Measured (image `i-danos_2608_20261030T0752-amd64.hybrid`, sha256 `5d9e25d937fc6dccb8df93bdbdb6a2bc1aa8dd8239491e77d2152f0c0c386fb4`, on 2026-11-02)

| binary package | in the image (SBOM, 1524 pkgs) | named in a package list | built by OBS (repo-index) |
|---|---|---|---|
| `python3-ufispace-bsp-utils` | no | no | yes |
| `python3-ufispace-bsp-sfp-helper` | no | no | yes |
| `ufispace-stat-led-control` | no | no | yes |

Some of these packages are built by this project's OBS repository (see the table), so they exist as `.deb` files, but **no package list installs them and nothing in the image depends on them**, so they are not in the image.

## What provides the corresponding function in the delivered image

No component supports the UfiSpace Apollo board (BSP, SFP helper, STAT LED). The image targets generic x86 machines and virtual machines. Note that a hardware-specific YANG deviation for Apollo *is* in the image, see the build-iso README, "Hardware support scope".

## How to verify this

From the workstation checkout root (`/home/aikon/danos`), with `NAMES="python3-ufispace-bsp-utils python3-ufispace-bsp-sfp-helper ufispace-stat-led-control"`:

```
# in the image? (an empty list means no)
python3 -c "import json,sys;n=set(sys.argv[1:]);S=json.load(open('releases/i-danos_2608_20261030T0752-amd64.hybrid/sbom.json'))['packages'];print(sorted(p['name'] for p in S if p['name'] in n))" $NAMES
# named in a package list? (no output means no)
for n in $NAMES; do grep -nE "^[[:space:]]*$n[[:space:]]*(#.*)?\$" build-iso/danos-sources/build-iso/config/package-lists/*.chroot; done
# built by OBS? (1 means yes)
for n in $NAMES; do echo $n $(grep -cE "^Package: $n\$" build-iso/danos-build/repo-index/Packages); done
```
