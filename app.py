import os
from mnemonic import Mnemonic
from bip32utils import BIP32Key, BIP32_HARDEN
import blocksmith
import base64
import web3
from web3 import Web3
import random
import asyncio
from contextlib import suppress
from web3 import eth


def load_env_file(dotenv_path, override=False):
    with open(dotenv_path) as file_obj:
        lines = file_obj.read().splitlines()  # Removes \n from lines

    dotenv_vars = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", maxsplit=1)
        dotenv_vars.setdefault(key, value)

    if override:
        os.environ.update(dotenv_vars)
    else:
        for key, value in dotenv_vars.items():
            os.environ.setdefault(key, value)

def phrase2seed(phrase, extra_word=''):
    """Phrase (+Extra Word) -> Seed"""
    assert isinstance(phrase, str), 'phrase should be str'
    assert isinstance(extra_word, str), 'extra_word should be str'

    mnemo = Mnemonic('english')
    return mnemo.to_seed(phrase, passphrase=extra_word)

def seed2prvkey(seed, derivation_path):
    """Seed -> Private Key"""
    assert isinstance(derivation_path, str), 'str_ should be str'
    path_list = derivation_path.split('/')
    assert path_list[0] == 'm', 'Derivation path should start with char "m"'

    xkey = BIP32Key.fromEntropy(seed).ExtendedKey()
    key = BIP32Key.fromExtendedKey(xkey)
    for path in path_list[1:]:
        if path[-1] == "'":
            key = key.ChildKey(int(path[:-1])+BIP32_HARDEN)
        else:
            key = key.ChildKey(int(path))
    return key.PrivateKey().hex()

def prvkey2ethaddr(prvkey, checksum=True):
    """Private Key -> Ethereum Address"""
    addr = blocksmith.EthereumWallet.generate_address(prvkey)
    if checksum:
        return blocksmith.EthereumWallet.checksum_address(addr)
    else:
        return addr

def phrase2ethaddr(phrase, extra_word, derivation_path, checksum=True):
    """Phrase (+Extra Word) -> Ethereum Address"""
    return prvkey2ethaddr(seed2prvkey(seed=phrase2seed(phrase, extra_word),
                                      derivation_path=derivation_path),
                          checksum=checksum)
def txt2list(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), 'r') as f:
        return [line.strip() for line in f]

def generate_mnemonic():
    mnemonic_words = []
    for x in range(12):
        mnemonic_words.append(random.choice(txt2list('bip39.txt')))
    return " ".join(mnemonic_words)

def check_balance(wallet_ac):
    from web3.auto.infura import w3
    return w3.eth.getBalance(wallet_ac)

def writeto(phrase, eth_addr, eth_balance):
    f = open(os.path.join(os.path.dirname(__file__), 'wallets.txt'), "a")
    f.write(phrase + "---" + eth_addr + "---" + eth_balance)
    f.close()

def loop():
    while True:
        phrase = generate_mnemonic()
        extra_word = '' # empty string if no extra word
        derivation_path = "m/44'/60'/0'/0/0" # the most common derivation path for generating Ethereum addresses
        eth_addr = phrase2ethaddr(phrase, extra_word, derivation_path)
        print("!==================================================================================!")
        print("Mnemonic: " + phrase)
        print("Wallet:   " + eth_addr)
        eth_balance = check_balance(eth_addr)
        print("Balance:  " + str(eth_balance))
        if(eth_balance != 0):
            writeto(phrase, eth_addr, eth_balance)


if __name__ == '__main__':
    env_file = os.path.join(os.path.dirname(__file__), 'base.env')
    load_env_file(env_file)
    loop()
