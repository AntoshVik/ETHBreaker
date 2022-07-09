import os
from mnemonic import Mnemonic
from bip32utils import BIP32Key, BIP32_HARDEN
import blocksmith
from threading import Thread
from web3 import Web3, HTTPProvider
import argparse


strength_of_wallet = 128
proxy_use = 'no'
THREAD_NUMBER = 1
CHILDS_NUMBER = 10
tg_launch = 'no'
proxy_file = 'proxy.txt'
TG_ADMIN = ''

w3 = Web3(HTTPProvider('https://nodes.mewapi.io/rpc/eth'))

def main():
    if tg_launch.lower() == 'no':
        Runner()
    else:
        Telegram()

def Telegram():
    from aiogram import Bot
    from config import TOKEN, ADMIN
    if TOKEN != '':
        TG_ADMIN = ADMIN
        bot = Bot(token=TOKEN)
        try:
            bot.send_message(ADMIN, text='Launched')
        except: 
            print('ERROR Send message')
            exit()
        print("Press Enter to exit", flush=True)
        for i in range(THREAD_NUMBER):
            Thread(target=loop, args=(i,'tg', bot)).start()
        input()
    else: print('No TOKEN in base.env file')

def Runner():
        print("Press Enter to exit", flush=True)
        for i in range(THREAD_NUMBER):
            Thread(target=loop, args=(i,'run')).start()
        input()

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
def generate_mnemonic():
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=strength_of_wallet)

def check_balance(wallet_ac):
    return w3.eth.getBalance(wallet_ac)

def writeto(phrase, eth_addr, eth_balance, path):
    f = open(os.path.join(os.path.dirname(__file__), 'wallets.txt'), "a")
    f.write(phrase + "---" + eth_addr + "---" + eth_balance + "---" + path)
    f.close()

def loop(thread, type_of, bot=''):
    while True:
        phrase = generate_mnemonic()
        extra_word = '' # empty string if no extra word
        derivation_path = "m/44'/60'/0'/0/" # the most common derivation path for generating Ethereum addresses
        for ch in range(CHILDS_NUMBER + 1):                
            eth_addr = phrase2ethaddr(phrase, extra_word, derivation_path + str(ch))
            print("!==================================================================================!")
            print("Thread:   " + str(thread))
            print("Mnemonic: " + phrase)
            print("Child:    " + str(ch))
            print("Wallet:   " + eth_addr)
            eth_balance = check_balance(eth_addr)
            print("Balance:  " + str(eth_balance / 1000000000000000000))
            if(eth_balance != 0):
                if type_of == 'tg':
                    bot.send_message(TG_ADMIN, text= phrase + '\n' + eth_addr + '\n' + derivation_path + str(ch))
                elif type_of == 'run':
                    writeto(phrase, eth_addr, eth_balance, derivation_path + str(ch))


parser = argparse.ArgumentParser(description='Eth wallets breaker')
parser.add_argument('-st', dest="strength_of_wallet", help="Strength of wallets (128 for 12 words / 256 for 24 words)", default=128, type=int, required=False)
parser.add_argument('-proxy', dest = "proxy_use", help="Use proxy? (YES/NO)", default="no", required=False)
parser.add_argument('-threads', dest = "THREAD_NUMBER", help="Number of threads (recommended <= 3)", default=1, type=int, required=False)
parser.add_argument('-childs', dest = "CHILDS_NUMBER", help="Number of childs for wallet (recommended <= 10)", default=10, type=int, required=False)
parser.add_argument('-tg', dest = "tg_launch", help="Launch as telegram bot (YES/NO)", default='no', required=False)
args = parser.parse_args()

strength_of_wallet = args.strength_of_wallet
proxy_use = args.proxy_use
THREAD_NUMBER = args.THREAD_NUMBER
CHILDS_NUMBER = args.CHILDS_NUMBER
tg_launch = args.tg_launch

if proxy_use.lower() == 'yes':
    with open(os.path.join(os.path.dirname(__file__), proxy_file), 'r') as file:
        w3 = Web3(HTTPProvider('https://nodes.mewapi.io/rpc/eth',request_kwargs={"proxies":file.read()}))
main()