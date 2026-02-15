import os, asyncio
from typing import cast
from breez_sdk_spark import Seed, default_config, Network, connect, \
    ConnectRequest, BreezSdk, GetInfoRequest, InputType, ReceivePaymentMethod, \
    ReceivePaymentRequest, PrepareSendPaymentRequest, SendPaymentRequest, \
    ListPaymentsRequest, GetPaymentRequest

from dotenv import load_dotenv

load_dotenv()

breez_api_key = os.getenv("BREEZ_API_KEY", "")
seed_phrase = os.getenv("SEED_PHRASE")
network_env = os.getenv("NETWORK", "REGTEST").upper()

# Map environment variable to Network enum
if network_env == "MAINNET":
    network = Network.MAINNET
else:
    network = Network.REGTEST  # Default to REGTEST for safety

# Breez SDK Spark typing: Seed.MNEMONIC is a valid Seed at runtime,
# but the Python stubs don't model the union correctly.
seed = cast(Seed, Seed.MNEMONIC(mnemonic=seed_phrase, passphrase=None))

config = default_config(network=network)
config.api_key = breez_api_key

# TODO ?: Event handler: https://sdk-doc-spark.breez.technology/guide/events.html
# TODO ?: Logger: https://sdk-doc-spark.breez.technology/guide/logging.html

async def connect_sdk():
    try:
        network_name = "MAINNET" if network == Network.MAINNET else "REGTEST"
        print(f"Welcome to your spark wallet!")
        print(f"Network: {network_name}")
        if network == Network.REGTEST:
            print("💡 Get test coins: https://app.lightspark.com/regtest-faucet")
        else:
            print("⚠️  WARNING: Using MAINNET - Real Bitcoin!")
        
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


async def send_bolt11_payment(sdk: BreezSdk, bolt11: str, amount_sats: int = None):
    try:
        # Parse the invoice first to check if it has an amount
        parsed_input = await sdk.parse(input=bolt11)
        
        invoice_amount_sats = None
        if isinstance(parsed_input, InputType.BOLT11_INVOICE):
            details = parsed_input[0]
            if details.amount_msat and details.amount_msat > 0:
                invoice_amount_sats = details.amount_msat // 1000
                print(f"Invoice Amount: {invoice_amount_sats} sats")
                # If invoice has an amount, ignore user-provided amount
                amount_sats = None
            else:
                print("Zero-amount invoice detected")
        
        # Step 1: Prepare the payment
        prepare_request = PrepareSendPaymentRequest(
            payment_request=bolt11,
            amount=amount_sats
        )
        prepare_response = await sdk.prepare_send_payment(request=prepare_request)
        
        print(f"Preparing payment...")
        # Show fees from prepare response
        if hasattr(prepare_response, 'fee'):
            print(f"Estimated Fees: {prepare_response.fee} sats")
        
        # Step 2: Send the payment
        send_request = SendPaymentRequest(
            prepare_response=prepare_response,
            options=None,
            idempotency_key=None
        )
        response = await sdk.send_payment(request=send_request)

        payment = response.payment
        print(f"Payment ID: {payment.id}")
        if hasattr(payment, 'payment_hash'):
            print(f"Payment Hash: {payment.payment_hash}")
        print(f"Amount: {payment.amount} sats")
        print(f"Fee: {payment.fees} sats")
        print(f"Status: {payment.status}")
        return response
    except Exception as error:
        print(error)
        raise


async def send_onchain_payment(sdk: BreezSdk, address: str, amount_sats: int):
    try:
        # Step 1: Prepare the payment
        prepare_request = PrepareSendPaymentRequest(
            payment_request=address,
            amount=amount_sats
        )
        prepare_response = await sdk.prepare_send_payment(request=prepare_request)
        
        print(f"Preparing payment...")
        # Show fees from prepare response
        if hasattr(prepare_response, 'fee'):
            print(f"Estimated Fees: {prepare_response.fee} sats")
        
        # Step 2: Send the payment
        send_request = SendPaymentRequest(
            prepare_response=prepare_response,
            options=None,
            idempotency_key=None
        )
        response = await sdk.send_payment(request=send_request)

        payment = response.payment
        print(f"Payment ID: {payment.id}")
        if hasattr(payment.details, '__dict__') and hasattr(payment.details, 'txid'):
            print(f"Transaction ID: {payment.details.txid}")
        print(f"Amount: {payment.amount} sats")
        print(f"Fee: {payment.fees} sats")
        print(f"Status: {payment.status}")
        return response
    except Exception as error:
        print(error)
        raise


async def list_payments(sdk: BreezSdk, limit: int = 10, offset: int = 0):
    try:
        request = ListPaymentsRequest(
            offset=offset,
            limit=limit,
            sort_ascending=False  # Newest first
        )
        response = await sdk.list_payments(request=request)
        
        payments = response.payments
        
        if not payments:
            print("No payments found.")
            return response
        
        print(f"\nShowing {len(payments)} payment(s) (offset: {offset})")
        print("="*80)
        
        for i, payment in enumerate(payments, start=offset + 1):
            print(f"\n{i}. Payment ID: {payment.id}")
            print(f"   Type: {payment.payment_type}")
            print(f"   Status: {payment.status}")
            print(f"   Amount: {payment.amount} sats")
            print(f"   Fees: {payment.fees} sats")
            print(f"   Method: {payment.method}")
            # Format timestamp
            from datetime import datetime
            dt = datetime.fromtimestamp(payment.timestamp)
            print(f"   Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            
        print("="*80)
        return response
    except Exception as error:
        print(error)
        raise


async def get_payment_details(sdk: BreezSdk, payment_id: str):
    try:
        request = GetPaymentRequest(payment_id=payment_id)
        response = await sdk.get_payment(request=request)
        payment = response.payment
        
        print("\n" + "="*80)
        print("PAYMENT DETAILS")
        print("="*80)
        print(f"Payment ID: {payment.id}")
        print(f"Type: {payment.payment_type}")
        print(f"Status: {payment.status}")
        print(f"Amount: {payment.amount} sats")
        print(f"Fees: {payment.fees} sats")
        print(f"Method: {payment.method}")
        
        # Format timestamp
        from datetime import datetime
        dt = datetime.fromtimestamp(payment.timestamp)
        print(f"Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show details if available
        if payment.details:
            print(f"\nAdditional Details:")
            print(f"{payment.details}")
        
        print("="*80)
        return response
    except Exception as error:
        print(error)
        raise


def display_menu():
    print("\n" + "="*50)
    print("BREEZ SDK WALLET - Main Menu")
    print("="*50)
    print("1. Get Balance")
    print("2. Get BOLT11 Invoice")
    print("3. Get On-Chain Receive Address")
    print("4. Parse Payment Input (Bitcoin Address or BOLT11)")
    print("5. Send BOLT11 Payment")
    print("6. Send On-Chain Payment")
    print("7. List Payments (Paginated)")
    print("8. Get Payment Details")
    print("9. Exit")
    print("="*50)


async def main():
    sdk = None
    try:
        # Connect to SDK
        sdk = await connect_sdk()
        print("✓ Successfully connected to Breez SDK\n")

        # Main wallet loop
        while True:
            display_menu()
            choice = input("\nEnter your choice (1-9): ").strip()

            if choice == "1":
                # Get Balance
                print("\nFetching balance...")
                balance = await fetch_balance(sdk)
                print(f"✓ Balance: {balance:,} sats\n")

            elif choice == "2":
                # Get BOLT11 Invoice
                print("\n--- Generate BOLT11 Invoice ---")
                description = input("Enter invoice description: ")
                try:
                    amount_sats = int(input("Enter amount in satoshis: "))
                    print("\nGenerating invoice...")
                    await get_bolt11_invoice(sdk, description, amount_sats)
                    print("✓ Invoice generated successfully!\n")
                except ValueError:
                    print("✗ Invalid amount. Please enter a number.\n")

            elif choice == "3":
                # Get Bitcoin Receive Address
                print("\n--- Generate Bitcoin Receive Address ---")
                await get_bitcoin_receive_address(sdk)
                print("✓ Address generated successfully!\n")

            elif choice == "4":
                # Parse Input
                print("\n--- Parse Payment Input ---")
                payment_input = input("Enter a Bitcoin address or BOLT11 invoice: ")
                await parse_input(sdk, payment_input)
                print("✓ Input parsed successfully!\n")

            elif choice == "5":
                # Send BOLT11 Payment
                print("\n--- Send BOLT11 Payment ---")
                bolt11 = input("Enter BOLT11 invoice: ")
                
                # Parse invoice first to check if it has an amount
                try:
                    parsed_input = await sdk.parse(input=bolt11)
                    invoice_has_amount = False
                    
                    if isinstance(parsed_input, InputType.BOLT11_INVOICE):
                        details = parsed_input[0]
                        if details.amount_msat and details.amount_msat > 0:
                            invoice_amount_sats = details.amount_msat // 1000
                            print(f"Invoice contains amount: {invoice_amount_sats} sats")
                            invoice_has_amount = True
                        else:
                            print("This is a zero-amount invoice")
                    
                    # Only ask for amount if invoice doesn't have one
                    amount_sats = None
                    if not invoice_has_amount:
                        amount_input = input("Enter amount in satoshis: ").strip()
                        try:
                            amount_sats = int(amount_input) if amount_input else None
                            if amount_sats is None:
                                print("✗ Amount is required for zero-amount invoices.\n")
                                continue
                        except ValueError:
                            print("✗ Invalid amount. Please enter a number.\n")
                            continue
                    
                    print("\nSending payment...")
                    await send_bolt11_payment(sdk, bolt11, amount_sats)
                    print("✓ Payment sent successfully!\n")
                except Exception as e:
                    print(f"✗ Error: {e}\n")

            elif choice == "6":
                # Send On-Chain Payment
                print("\n--- Send On-Chain Payment ---")
                address = input("Enter Bitcoin address: ")
                try:
                    amount_sats = int(input("Enter amount in satoshis: "))
                    print("\nSending payment...")
                    await send_onchain_payment(sdk, address, amount_sats)
                    print("✓ Payment sent successfully!\n")
                except ValueError:
                    print("✗ Invalid amount. Please enter a number.\n")

            elif choice == "7":
                # List Payments (Paginated)
                print("\n--- List Payments ---")
                offset = 0
                limit = 10
                
                while True:
                    await list_payments(sdk, limit=limit, offset=offset)
                    
                    print("\nOptions: [N]ext page, [P]revious page, [B]ack to menu")
                    nav = input("Enter choice: ").strip().upper()
                    
                    if nav == "N":
                        offset += limit
                    elif nav == "P":
                        offset = max(0, offset - limit)
                    elif nav == "B":
                        break
                    else:
                        print("Invalid option. Returning to menu.")
                        break

            elif choice == "8":
                # Get Payment Details
                print("\n--- Get Payment Details ---")
                payment_id = input("Enter Payment ID: ").strip()
                if payment_id:
                    try:
                        await get_payment_details(sdk, payment_id)
                    except Exception as e:
                        print(f"✗ Error: {e}\n")
                else:
                    print("✗ Payment ID is required.\n")

            elif choice == "9":
                # Exit
                print("\nExiting wallet...")
                break

            else:
                print("\n✗ Invalid choice. Please enter a number between 1 and 9.\n")

    except Exception as error:
        print(f"\n✗ Error: {error}")
    finally:
        # Disconnect from SDK
        if sdk:
            await disconnect_sdk(sdk)
            print("✓ Disconnected from Breez SDK")
            print("\nThank you for using Breez SDK Wallet!")


if __name__ == "__main__":
    asyncio.run(main())