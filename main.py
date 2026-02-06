import os, asyncio
from typing import cast
from breez_sdk_spark import Seed, default_config, Network, connect, \
    ConnectRequest, BreezSdk, GetInfoRequest

from dotenv import load_dotenv

load_dotenv()

breez_api_key = os.getenv("BREEZ_API_KEY", "")
seed_phrase = os.getenv("SEED_PHRASE")

# Breez SDK Spark typing: Seed.MNEMONIC is a valid Seed at runtime,
# but the Python stubs don't model the union correctly.
seed = cast(Seed, Seed.MNEMONIC(mnemonic=seed_phrase, passphrase=None))

# TODO: Network env variable
config = default_config(network=Network.REGTEST)
config.api_key = breez_api_key

# TODO: Event handler

async def connect_sdk():
    try:
        # Connect using simplified(?) connect method
        sdk = await connect(
            request=ConnectRequest(config=config, seed=seed, storage_dir="./.data")
        )
        return sdk
    except Exception as error:
        print(error)
        raise


async def disconnect_sdk(sdk: BreezSdk):
    try:
       await sdk.disconnect()
    except Exception as error:
        print(error)
        raise


async def fetch_balance(sdk: BreezSdk):
    try:
        # Setting ensure_synced to 'true' as we are not
        # running the wallet in the background and want an accurate balance.
        info = await sdk.get_info(request=GetInfoRequest(ensure_synced=True))
        balance_sats = info.balance_sats
    except Exception as error:
        print(error)
        raise


connection = asyncio.run(connect_sdk())
print("Connected:", connection)

# Dev note here - fetching the balance with the ensure_synced set to "True" is pretty slow.
print("Fetching balance...")
balance = asyncio.run(fetch_balance(connection))
print("Balance:", balance)

asyncio.run(disconnect_sdk(connection))
print("Disconnected:", connection)



