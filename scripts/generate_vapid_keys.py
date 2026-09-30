"""Generate a real VAPID key pair for Web Push (RFC 8292).

VAPID (Voluntary Application Server Identification) is a self-signed EC key
pair the *server* generates and keeps forever - it proves to the browser's
push service (Chrome/Firefox/Edge's own infrastructure) which application
server is allowed to send pushes to a given subscription. This is NOT an
account with a third party: no signup, no API key from Google/Mozilla/Apple
is needed, unlike the older FCM/APNs-only approach. See
docs/research/sonraki-adimlar-firsat-analizi.md item 4 and CLAUDE.md.

Run once (per environment - dev and prod should each have their own pair):

    venv\\Scripts\\python.exe scripts\\generate_vapid_keys.py

Then copy the two printed lines into your local .env (never commit .env -
see .gitignore). VAPID_CLAIMS_EMAIL is not generated here; set it yourself
in .env to a real contact address (used in the VAPID JWT "sub" claim, as
required by RFC 8292 - push services may use it to contact you about abuse).

Both keys are printed as raw, URL-safe base64 without padding - the exact
format the browser's `PushManager.subscribe({applicationServerKey})` and
`pywebpush.webpush(vapid_private_key=...)` both expect directly (no PEM
wrapping needed), so they can be pasted straight into .env.
"""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from py_vapid.utils import b64urlencode


def generate_vapid_keypair() -> tuple[str, str]:
    """Returns (public_key_b64url, private_key_b64url).

    public_key_b64url: the 65-byte uncompressed EC point (SECP256R1),
    base64url-encoded - what the frontend passes as applicationServerKey.

    private_key_b64url: the 32-byte raw private scalar, base64url-encoded -
    what pywebpush.webpush(vapid_private_key=...) accepts directly (it
    detects this isn't a file path and calls Vapid.from_string on it).
    """
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()

    private_raw = private_key.private_numbers().private_value.to_bytes(32, "big")
    public_raw = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )

    return b64urlencode(public_raw), b64urlencode(private_raw)


if __name__ == "__main__":
    public_key, private_key = generate_vapid_keypair()
    print("Gerçekten üretilmiş yeni bir VAPID anahtar çifti (RFC 8292).")
    print("Aşağıdaki iki satırı .env dosyana kopyala (asla commit etme):\n")
    print(f"VAPID_PUBLIC_KEY={public_key}")
    print(f"VAPID_PRIVATE_KEY={private_key}")
    print("VAPID_CLAIMS_EMAIL=mailto:you@example.com  # gerçek bir iletişim adresiyle değiştir")
