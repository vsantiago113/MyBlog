from flask import Blueprint, render_template, request, abort
import hashlib
from app.blueprints.bitcoin.crypto_lib import ecdsa
from app.blueprints.bitcoin.crypto_lib import base58
import binascii

bitcoin = Blueprint("bitcoin", __name__, template_folder="templates", static_folder="static",
                    url_prefix="/bitcoin")


def create_address(_pub_key):
    # Hash160
    _hash160 = hashlib.new('ripemd160', hashlib.sha256(binascii.unhexlify(_pub_key)).digest()).digest()

    # Calculate checksum
    extended_hash160 = b'00' + binascii.hexlify(_hash160)
    hashed_from_ext_hash160 = hashlib.sha256(binascii.unhexlify(extended_hash160)).digest()
    hash256_2 = hashlib.sha256(hashed_from_ext_hash160).digest()
    checksum = binascii.hexlify(hash256_2)[:8]

    final_hash = extended_hash160 + checksum

    _address = base58.b58encode(binascii.unhexlify(final_hash))
    return _address, binascii.hexlify(_hash160).decode('utf-8')


def create_brainwallet(passphrase):
    # Secret Exponent
    passphrase_to_long = int(hashlib.sha256(passphrase.encode('ascii', 'ignore')).hexdigest(), 16)
    pk = ecdsa.SigningKey.from_secret_exponent(passphrase_to_long, ecdsa.curves.SECP256k1)
    _secret_exponent = binascii.hexlify(pk.to_string())

    # Public Key
    _pub_key = binascii.hexlify(pk.get_verifying_key().to_string())
    public_key = b'04' + _pub_key

    # Private Key as WIF
    private_key, private_key_compressed = priv_key_to_wif(binascii.hexlify(pk.to_string()))
    return private_key, public_key.decode('utf-8'), _secret_exponent.decode('utf-8')


def priv_key_to_wif(_priv_key):
    # Uncompressed
    extended_priv_key = b'80' + _priv_key
    _hash256 = hashlib.sha256(binascii.unhexlify(extended_priv_key)).digest()
    _hash256_2 = hashlib.sha256(_hash256).digest()
    checksum = binascii.hexlify(_hash256_2)[:8]
    final_hash = extended_priv_key + checksum

    # Compressed
    extended_priv_key_compressed = b'80' + _priv_key + b'01'
    _hash256_compressed = hashlib.sha256(binascii.unhexlify(extended_priv_key_compressed)).digest()
    _hash256_2_compressed = hashlib.sha256(_hash256_compressed).digest()
    checksum_compressed = binascii.hexlify(_hash256_2_compressed)[:8]
    final_hash_compressed = extended_priv_key_compressed + checksum_compressed
    return base58.b58encode(binascii.unhexlify(final_hash.decode('utf-8'))), base58.b58encode(binascii.unhexlify(final_hash_compressed.decode('utf-8')))


@bitcoin.route("/brainwallet", methods=("GET", "POST"))
def brainwallet():
    if request.method == 'POST':
        form = request.form
        if form:
            seed = request.form.get('passphrase')
            priv_key, pub_key, secret_exponent = create_brainwallet(seed)
            address, hash160 = create_address(pub_key)
            _bitcoin = dict(seed=seed,
                            priv_key=priv_key,
                            pub_key=pub_key,
                            secret_exp=secret_exponent,
                            address=address,
                            hash160=hash160,
                            qr_address='https://blockchain.info/address/{}'.format(address))

            return render_template('brainwallet.html', bitcoin=_bitcoin)
        else:
            abort(404)
    else:
        _bitcoin = dict(seed='',
                        priv_key='',
                        pub_key='',
                        secret_ext='',
                        address='',
                        hash160='',
                        qr_address='')
        return render_template('brainwallet.html', bitcoin=_bitcoin)
