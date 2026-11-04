# Mitigations

The vulnerability is a verify-then-use TOCTOU on an in-place file on removable media, with
no post-write device verification and no boot-time rootfs integrity. Any **one** of the
following closes it; defense in depth would apply several.

## 1. Verify and use the *same bytes* (the direct fix)
Do not read the update file twice from untrusted media with the integrity decision in
between. Either:
- **Copy to trusted local storage first**, then verify **and** install the *local* copy; or
- **Hash while installing** in a single streaming pass (tee the decrypt/extract stream into
  the digest) and compare the result to the signed digest, aborting the A/B switch on
  mismatch. One open, one read, no window.

## 2. Post-write device read-back
After writing the inactive partition, **re-hash the partition as written on the device** and
compare to the signed manifest before the A/B switch. Today the post-install "verify" is
source-side and takes 46 ms — it never re-reads the 879 MB partition, so a swapped image is
not caught.

## 3. dm-verity (or enforced IMA-appraisal) on the rootfs
Mount the system rootfs under **dm-verity** with the root hash anchored in the
signature-covered boot image. A swapped ext4 then fails at mount/boot even if it reached the
partition. Currently the rootfs is plain ext4 with no verity and the bootloader RSA covers
only the boot image.

## Why signing alone is not enough
The update **is** RSA-signed and the signing chain **is** enforced — but the attack never
breaks the signature. It presents the genuine, correctly-signed image *to the check* and a
different image *to the install*. Signature enforcement defends the bytes that are checked;
it does nothing for bytes that are read later from mutable media. The fix must bind the
checked bytes to the used bytes.
