import os, asyncio
from breez_sdk_spark import Seed, default_config, Network, connect, ConnectRequest

from dotenv import load_dotenv

load_dotenv()

breez_api_key = os.getenv("BREEZ_API_KEY", "")
seed_phrase = os.getenv("SEED_PHRASE")

seed = Seed.MNEMONIC(mnemonic=seed_phrase, passphrase=None)

# TODO: Network env variable
config = default_config(network=Network.REGTEST)
config.api_key = breez_api_key

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

connection = asyncio.run(connect_sdk())

print("Connected:", connection)



