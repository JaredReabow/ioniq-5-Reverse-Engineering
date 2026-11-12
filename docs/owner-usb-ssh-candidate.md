# Owner authentication recovery candidate

The selected recovery overlay is version **4.0.2**, based on the retained
official EU **260128** rootfs. Its backups are independent ways to authenticate
over the existing working Ethernet connection:

- The retained owner Ed25519 SSH key.
- Nonempty SSH password authentication, compiled into the pinned static server.
- An HTTPS browser terminal at `https://10.42.0.1:8443`, using a separate
  recovery password and no Dropbear, PAM, SSH-key or Linux-login-account lookup.
- A physically triggered local Weston terminal using a USB keyboard. Actual
  head-unit surface visibility and keyboard focus remain to be verified.

Ethernet is managed separately from both login daemons. A failed SSH service
cannot remove the address needed by the browser terminal. The selected overlay
contains no Wi-Fi AP, Radxa ECM, or serial/TTL console; prior module source is
retained for research.

Credentials stay in the ignored, mode-0700
`work/radxa-toctou-build/private` directory. The SSH password is in
`owner_ssh_password.txt`; the distinct browser password is in
`owner_web_password.txt`. They are not printed in logs, published in Git, or
passed on process command lines. Browser TLS is self-signed: compare its
certificate fingerprint with the retained `owner_web_tls.crt`.

The selected package is `owner_access_v4.0.2_260128.te2`, 879,126,179 bytes,
with SHA-256
`94323aa3d05b4cf2e1a894ca445f4bf8a85f9341c0a879d2cdbbc338304123c6`.
Its builder verified the decrypted overlay, root ownership, modes and TE2
integrity, with 44,639 bytes of padding remaining. This is a prepared candidate;
it has not been installed or authenticated on the head unit.

## Connection design

After the custom firmware is installed, the simplest reliable SSH path is a
private wired link:

```text
IONIQ 5 data USB port
  -> supported USB-to-Ethernet adapter
  -> Ethernet cable
  -> Mac Ethernet interface (normally a USB-C Ethernet adapter)
```

The head unit uses `10.42.0.1/24`; configure the Mac Ethernet interface manually
as `10.42.0.2` with subnet mask `255.255.255.0`. Leave router/gateway and DNS
blank. The firmware deliberately provides no DHCP server, default route, or
internet sharing.

Keep the owner's previously working RTL8152 adapter reporting USB ID
`0bda:8152`. Also allowlisted are Realtek `0bda:8153` and ASIX
`0b95:7720`, `0b95:772a`, and `0b95:772b`. AX88179, RNDIS, and the target's
SMSC static-route hook are deliberately outside this candidate. Static module
evidence supports these allowlisted families. The previous live run established
the owner's RTL8152 link and the SSH listener; authentication in this recovery
build still requires verification after installation.

## Authentication

Keep the retained owner private key on the Mac and connect with:

```sh
ssh -o PreferredAuthentications=publickey \
    -o PasswordAuthentication=no \
    -i /absolute/path/to/the/private_key \
    root@10.42.0.1
```

On first connection, compare the presented host-key fingerprint with the
fingerprint calculated from the retained build input before accepting it. An
unrelated key, wrong password or blank password must fail. A correct owner
password is an independent alternative to the key:

```sh
ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password root@10.42.0.1
```

Legacy SCP is available with `scp -O`. The exact static binary has passed key,
password, wrong/blank credential, PTY, SCP round-trip and forwarding-denial
checks in a disposable Linux container with the OEM-style `/` mode `0775`.
The browser terminal uses its own credential verifier and starts `/bin/sh`
directly, so it can be used to repair SSH even when SSH account setup fails.
The current binary is version 1.0.2. Real Chrome-to-Linux testing verified
normal click-to-type input, execution of a shell command, successful logout,
closure of the old terminal socket and unauthenticated reload. Its compact
terminal supports command-line recovery; it is not a complete terminal emulator
for every full-screen application.

## Runtime behavior

The service activates only after udev identifies an allowlisted USB NIC and
renames it `ownerusb0`. It revalidates the interface's sysfs path, USB identity,
driver, and ifindex before making changes. It refuses an existing address,
route, or firewall-name collision. Its firewall permits SSH and HTTPS between the
dedicated subnet and `10.42.0.1`, and blocks forwarding and IPv6 on that
interface. Unplugging the adapter stops its login services and removes only state that still
belongs to the same physical interface identity.

The Radxa is separate: it presents the two-pass dynamic update medium during
installation. It is not needed for SSH once the modified head unit has booted.

## Radxa control

The prepared SD card boots as `radxa-ioniq.local` and accepts the owner key only.
From the configured Mac, connect with:

```sh
ssh radxa-ioniq
```

Update-media auto-arm is intentionally disabled. The explicit control commands
are `ioniq-update-media prepare`, `verify`, `arm`, `status`, and `teardown`. Always run
`teardown` before unplugging the Radxa or changing the OTG connection. The
physical Radxa-only arm/teardown cycle has passed; this does not itself prove
the vehicle updater will consume the switched medium.

The installed tools and firmware are reused after power cycles. Explicit
`prepare` verifies new or changed content and persists a private validation
cache; normal arming checks exact file identities without starting another
30 GB hash. `verify` explicitly forces full hashing when wanted. The cache
trusts local ownership and filesystem metadata and does not detect silent media
corruption; force verification after storage errors. A real cached load plus
both rechecks took 0.019 seconds on this Radxa.
After selecting 4.0.2, the complete cached plan process took 0.735 seconds,
including Python startup and live resource inspection. This measures plan
validation, not total USB enumeration or car-side update time.

The KDE desktop automatically logs in as `radxa`. Its read-only dashboard
shows preparation, USB read passes, measured byte coverage and verbose logs.
It never equates a complete USB read with a completed car-side flash. The
dashboard and in-place runtime have separate installers; the SD image does not
need rebuilding. Persistent session metadata warns about a previous boot's
interrupted arm, without automatically restarting it.
Dashboard 1.0.7 disables automatic idle suspend, dimming and display power-off,
and runs a separate root sleep/idle inhibitor. The apparent board crash was a
journal-confirmed KDE deep suspend; the board resumed within the same boot.
The installed API now reports the selected media ready and unarmed. Historical
cache extents superseded by a current whole-file identity do not cause a false
changed-file warning; real mutations still require explicit preparation.

## Historical v2 verification

The candidate has passed deterministic generation, decrypted-overlay checks,
the integrated 121-test/35-subtest suite, exact exFAT extent validation, a
complete genuine-first/custom-second replay over the real 30.1 GB media image,
and a physical Radxa UDC/NBD/configfs arm-to-clean-teardown cycle. Owner image
`1.0.3` has SHA-256
`14d8662e84a84d8ce079042fb2ddb428a385af6c58e35ede853bf0273f169312`.
See `evidence/vehicle-usb/owner-usb-ssh-offline-verification.md`.

These results describe the earlier v2 package. The later vehicle update was
reported complete and its Ethernet listener was reached, but the owner key was
rejected because its directory was outside the runtime account home. Recovery
version 4.0.2 addresses that failure and must receive its own installed checks.
