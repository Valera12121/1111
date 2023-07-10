from aptos_sdk.account import Account
from Aptos_client import RestClient

from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from json import load
from loguru import logger
import time
from dotenv import dotenv_values


NODE_URL = dotenv_values()["NODE_URL"]
MAX_GAS = dotenv_values()["GAS_LIMIT"]
GAS_PRICE= dotenv_values()["GAS_PRICE"]
START_TIME= int(dotenv_values()["TIMESTAMP_START"])

aptos = RestClient(NODE_URL)


def get_payload():
    with open("payload.json", "r") as f:
        return dict(load(f))


payload = get_payload()


class Minter:
    def __init__(self, account):
        self.account = account
        self.nonce = str(aptos.account_sequence_number(account.address()))

    def mint(self):
        tx = aptos.mint_transaction(self.account, payload, self.nonce, MAX_GAS, GAS_PRICE)
        logger.success(f'Send tx - {tx}')


def create_minters():
    result = []
    with open('private_keys.txt', 'r') as f:
        seeds = [row.strip() for row in f]

    def from_key(seed):
        acc = Account.load_key(seed)
        minter = Minter(acc)
        result.append(minter)

    with ThreadPoolExecutor(max_workers=30) as wp_executor:
        wp_executor.map(from_key, seeds)

    return result


left_time = START_TIME - time.time()
if left_time > 0:
    print(f'Waiting mint - {left_time}')
    time.sleep(left_time)
start = time.time()
threads = []
minters = create_minters()
for m in minters:
    threads.append(Thread(target=m.mint))

for t in threads:
    t.start()

for t in threads:
    t.join()
print(f'Mint time - {time.time() - start}')
