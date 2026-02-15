# Breez SDK Nodeless Wallet

A command-line Bitcoin wallet built with the **Breez SDK (Spark)** that enables self-custodial Lightning and on-chain payments with REGTEST and MAINNET support.

## Features

### Wallet Management

- **Get Balance** - View your current wallet balance in satoshis
- **REGTEST/MAINNET Network Switching** - Easy environment variable configuration

### Receive Payments

- **BOLT11 Invoices** - Generate Lightning invoices with custom amounts and descriptions
- **Bitcoin Addresses** - Generate on-chain receiving addresses for static Bitcoin deposits
- **Lightning Addresses** - _Coming soon_ - Human-readable addresses like `user@domain.com`

### Send Payments

- **BOLT11 Payments** - Send Lightning Network payments with automatic amount detection
- **On-Chain Payments** - Send Bitcoin to addresses with automatic fee estimation
- **Lightning Addresses** - _Coming soon_ - Send to Lightning addresses

### Payment History

- **List Payments (Paginated)** - Browse payment history with pagination controls (10 per page)
- **Payment Details** - View comprehensive information for any payment including timestamps, fees, and metadata

### Utilities

- **Parse Input** - Identify and validate Bitcoin addresses and BOLT11 invoices
- **Check Lightning Address Availability** - _Coming soon_

## Prerequisites

- Python 3.9 or higher
- Pip package manager
- A Breez SDK API key (request at: https://breez.technology/request-api-key/)
- A Bitcoin seed phrase (12 or 24 word mnemonic)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/breez-sdk-nodeless-wallet.git
cd breez-sdk-nodeless-wallet
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root (see `.env.example` for template):

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```dotenv
BREEZ_API_KEY="your-api-key-here"
SEED_PHRASE="your 12 or 24 word seed phrase"
NETWORK="REGTEST"  # or "MAINNET" for real Bitcoin
```

> **Important:** Never share your `.env` file or seed phrase. Keep it private and secure!

## Usage

### Start the Wallet

```bash
python main.py
```

### Interactive Menu

The wallet presents a menu with the following options:

```
1. Get Balance              - Check current wallet balance
2. Get BOLT11 Invoice      - Create Lightning invoice to receive payments
3. Get On-Chain Address    - Generate Bitcoin address for deposits
4. Parse Payment Input     - Validate Bitcoin address or BOLT11 invoice
5. Send BOLT11 Payment     - Send Lightning payment
6. Send On-Chain Payment   - Send Bitcoin payment
7. List Payments           - View payment history (paginated)
8. Get Payment Details     - View detailed info for specific payment
9. Exit                    - Close the wallet
```

### Example Workflow

**Receive Bitcoin via Lightning:**

1. Select option `2`
2. Enter invoice description (e.g., "Test Payment")
3. Enter amount in satoshis
4. Share the generated BOLT11 invoice with the sender

**Check Your Balance:**

1. Select option `1`
2. Your current balance displays in satoshis

**View Payment History:**

1. Select option `7`
2. Browse payments with `[N]` (next), `[P]` (previous), `[B]` (back)
3. Copy a Payment ID to view detailed information
4. Select option `8` and paste the Payment ID

## Network Configuration

### REGTEST (Testing)

- **Use Case:** Development and testing
- **Cost:** Free - test coins via [Lightspark Regtest Faucet](https://app.lightspark.com/regtest-faucet)
- **Bitcoin:** Fake satoshis with no real value
- **Lightning:** Limited - on-chain focus
- **Setup:** `NETWORK="REGTEST"` in `.env`

### MAINNET (Production)

- **Use Case:** Real Bitcoin transactions
- **Cost:** Real satoshis
- **Bitcoin:** Actual Bitcoin payments
- **Lightning:** Full Lightning Network support
- **Setup:** `NETWORK="MAINNET"` in `.env`
- **Warning:** Use small amounts initially for testing

## Testing on REGTEST

### Getting Test Coins

1. Select option `3` to generate a Bitcoin address
2. Copy the address
3. Visit [Lightspark Regtest Faucet](https://app.lightspark.com/regtest-faucet)
4. Paste your address and request test coins
5. Select option `1` to check your balance after confirmation

### Testing Payments

Once you have test coins:

- Create invoices and test receiving
- Send test payments to on-chain addresses
- Experiment with payment parsing

## Project Structure

```
breez-sdk-nodeless-wallet/
├── main.py                 # Main wallet CLI application
├── .env.example           # Template for environment variables
├── .env                   # Actual secrets (NOT in git)
├── .gitignore            # Git ignore rules
├── .data/                # Local wallet data (NOT in git)
│   ├── regtest/
│   └── mainnet/
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## API Key Setup

### Requesting an API Key

1. Visit: https://breez.technology/request-api-key/
2. Fill out the form with your details
3. Breez will send you an API key
4. Add it to your `.env` file as `BREEZ_API_KEY`

## Future Features

- **Lightning Addresses** - Register custom `user@domain.com` addresses
- **LNURL Support** - Complete LNURL-Pay and LNURL-Withdraw

## Troubleshooting

### "ModuleNotFoundError: No module named 'breez_sdk_spark'"

- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- On Windows PowerShell, you may need: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

### "Insufficient funds" on REGTEST

- Visit the [Lightspark Regtest Faucet](https://app.lightspark.com/regtest-faucet)
- Generate a receive address (option 3) and request test coins

### "Service error: Invalid API key"

- Verify your `BREEZ_API_KEY` in `.env`
- Ensure there are no extra spaces or quotes around the key

### "ModuleNotFoundError" when running wallet

- Activate virtual environment first
- Verify venv activation: You should see `(.venv)` in your terminal prompt

## Security Best Practices

1. **Never commit `.env`** - It contains your private seed phrase and API key
2. **Keep seed phrase safe** - This is your wallet's master key; losing it = losing funds
3. **Use test networks first** - Test on REGTEST before MAINNET
4. **Small amounts only** - Start with small MAINNET amounts
5. **Backup seed phrase** - Store in a safe location separate from your computer
6. **Use strong passwords** - Protect your machine and backup storage

## Contributing

Contributions are welcome! Please feel free to:

- Report issues
- Suggest features
- Submit pull requests
- Improve documentation

## Resources

- [Breez SDK Documentation](https://sdk-doc-spark.breez.technology/)
- [Breez SDK GitHub](https://github.com/breez/spark-sdk)
- [Lightning Network Protocol](https://github.com/lightningnetwork/lightning-rfc)
- [LNURL Specifications](https://github.com/lnurl/luds)
- [Bitcoin UTXO Model](https://developer.bitcoin.org/devguide/transactions.html)

## License

MIT License - See LICENSE file for details

## Disclaimer

This wallet is provided as-is for educational and testing purposes. Use at your own risk. The authors are not responsible for lost funds, security breaches, or any other issues. Always test with small amounts on REGTEST first before using MAINNET.

---
