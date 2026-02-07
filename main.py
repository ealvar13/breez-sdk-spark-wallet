import os, asyncio
from typing import cast
from breez_sdk_spark import Seed, default_config, Network, connect, \
    ConnectRequest, BreezSdk, GetInfoRequest, InputType, ReceivePaymentMethod, \
    ReceivePaymentRequest

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

# TODO ?: Event handler: https://sdk-doc-spark.breez.technology/guide/events.html
# TODO ?: Logger: https://sdk-doc-spark.breez.technology/guide/logging.html

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
        return balance_sats
    except Exception as error:
        print(error)
        raise


async def parse_input(sdk: BreezSdk, user_input: str):
    try:
        parsed_input = await sdk.parse(input=user_input)
        if isinstance(parsed_input, InputType.BITCOIN_ADDRESS):
            details = parsed_input[0]
            print(f"Input is Bitcoin address {details.address}")
        elif isinstance(parsed_input, InputType.BOLT11_INVOICE):
            details = parsed_input[0]
            print(f"Input is BOLT11 invoice for {details.amount_msat} msats")
    except Exception as error:
        print(error)
        raise


async def get_bolt11_invoice(sdk: BreezSdk, description: str, amount_sats: int):
    try:
        payment_method = cast(ReceivePaymentMethod, ReceivePaymentMethod.BOLT11_INVOICE(
            description=description,
            amount_sats=amount_sats,
            expiry_secs=3600
        ))
        request = ReceivePaymentRequest(payment_method=payment_method)
        response = await sdk.receive_payment(request=request)

        payment_request = response.payment_request
        print(f"Payment Request: {payment_request}")
        receive_fee_sats = response.fee
        print(f"Fees: {receive_fee_sats}")
        return response
    except Exception as error:
        print(error)
        raise


async def get_bitcoin_receive_address(sdk: BreezSdk):
    try:
        request = ReceivePaymentRequest(
            payment_method=ReceivePaymentMethod.BITCOIN_ADDRESS()
        )
        response = await sdk.receive_payment(request=request)

        payment_request = response.payment_request
        print("Payment request: ", payment_request)
        receive_fee_sats = response.fee
        print(f"Fees: {receive_fee_sats} sats")

        return response
    except Exception as error:
        print(error)
        raise


connection = asyncio.run(connect_sdk())
print("Connected:", connection)

# Dev note here - fetching the balance with the ensure_synced set to "True"
# is pretty slow.
print("Fetching balance...")
balance = asyncio.run(fetch_balance(connection))
print("Balance:", balance)

payment_input = input("Enter a bitcoin address or BOLT11 invoice: ")
asyncio.run(parse_input(connection, payment_input))
print("Input parsing completed")

print("Ready to generate bolt11 invoice...")
bolt11_description = input("Enter an invoice description: ")
bolt11_amount_sats = int(input("Enter an amount in satoshis: "))
asyncio.run(get_bolt11_invoice(connection, bolt11_description, bolt11_amount_sats))

print("Ready to generate a bitcoin address...")
asyncio.run(get_bitcoin_receive_address(connection))

asyncio.run(disconnect_sdk(connection))
print("Disconnected:", connection)



