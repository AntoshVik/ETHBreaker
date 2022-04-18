import os
from pywallet import wallet
from web3 import Web3, HTTPProvider
from threading import Thread

proxies = {'http': '158.69.53.98:9300', 'http': '209.97.171.82:8080', 'http': '213.135.0.69:8080'}

THREAD_NUMBER = 3

CHILDS_NUMBER = 10

w3 = Web3(HTTPProvider('https://nodes.mewapi.io/rpc/eth',request_kwargs={"proxies":proxies}))

def generate_seed():
    return wallet.generate_mnemonic()

def create_wallet(number_childrens):
    return wallet.create_wallet(network="ETH", seed=generate_seed(), children=number_childrens)

def check_balance(wallets):
    balance = w3.eth.get_balance(Web3.toChecksumAddress(wallets['address']))
    if(balance > 0):
        writeto(wallets['seed'], wallets['address'], balance, wallets['private_key'], wallets['public_key'])
    print("!==============================================================================!\n" + wallets['seed'] + "\n" + wallets['address'] +" "+ str(balance / 1000000000000000000) + " ETH")
    for w in wallets['children']:
        mini_balance = w3.eth.get_balance(Web3.toChecksumAddress(w['address']))
        if(mini_balance > 0):
            writeto(wallets['seed'], w['address'], mini_balance, w['public_key'], bip_path=w['bip32_path'])
        print("!==============================================================================!\n" + wallets['seed'] + "\n" + w['address'] +" "+ str(balance / 1000000000000000000) + " ETH")

def writeto(phrase, eth_addr, eth_balance, public, private="None", bip_path = "main"):
    f = open(os.path.join(os.path.dirname(__file__), 'wallets.txt'), "a")
    f.write("=========================================================")
    f.write("ADDRESS: " + eth_addr)
    f.write("PHRASE: " + phrase)
    f.write("PRIVATE: " + private)
    f.write("PUBLIC: " + public)
    f.write("BIP32PATH: " + bip_path)
    f.write("BALANCE: " + eth_balance / 1000000000000000000 + " ETH")
    f.close()

def show(wallets):
    print("ADDRESS: " + wallets['address'])
    print("SEED: " + wallets['seed'])
    print("PRIVATE: " + wallets['private_key'])
    print("PUBLIC: " + wallets['public_key'])
    print("X_PRIVATE: " + wallets['xprivate_key'])
    print("X_PUBLIC: " + wallets['xpublic_key'])
    for num, child in enumerate(wallets['children']):
        print("CHILD " + str(num) + " ADDRESS: " + child['address'])
        print("CHILD " + str(num) + " X_PUBLIC: " + child['xpublic_key'])
        print("CHILD " + str(num) + " PATH: " + child['path'])
        print("CHILD " + str(num) + " BIP32PATH: " + child['bip32_path'])

def run():
    while True:
        check_balance(create_wallet(CHILDS_NUMBER))

def main():
    print("Press Enter to exit", flush=True)
    for i in range(THREAD_NUMBER):
        Thread(target=run).start()
    input()

main()
