from algosdk.v2client import algod # type: ignore
from algosdk import account, mnemonic # type: ignore
from algosdk.transaction import PaymentTxn, AssetTransferTxn, wait_for_confirmation, AssetFreezeTxn # type: ignore
from dotenv import load_dotenv # type: ignore
import os
from algosdk.v2client import indexer  # Add this import
import base64
def get_recipient_address(mnemonic_phrase: str) -> str:
    # Get private key from mnemonic
    private_key = mnemonic.to_private_key(mnemonic_phrase)
    # Get address from private key
    address = account.address_from_private_key(private_key)
    return address

def create_and_fund_wallet():
    load_dotenv()
    ALGOD_ADDRESS = 'https://testnet-api.algonode.cloud'
    ALGOD_TOKEN = ''
    algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

    FUNDING_AMOUNT = 2_000_000  # microAlgos (0.2 ALGO, enough to opt-in + fees)

    admin_mnemonic = os.getenv('MNEMONIC')
    admin_private_key = mnemonic.to_private_key(admin_mnemonic)
    admin_address = account.address_from_private_key(admin_private_key)
    # 1. Create a new wallet
    private_key, address = account.generate_account()
    wallet_mnemonic = mnemonic.from_private_key(private_key)

    print("🆕 New wallet created!")
    print("🔐 Mnemonic:", wallet_mnemonic)
    print("📫 Address:", address)

    # 2. Fund it from admin wallet
    params = algod_client.suggested_params()
    pay_txn = PaymentTxn(
        sender=admin_address,
        sp=params,
        receiver=address,
        amt=FUNDING_AMOUNT,
    )
    signed_pay = pay_txn.sign(admin_private_key)
    txid = algod_client.send_transaction(signed_pay)
    wait_for_confirmation(algod_client, txid, 4)
    print(f"💸 Funded new wallet with {FUNDING_AMOUNT / 1e6} ALGO")

    ## Opt in to ASAs
    ids = [737489627, 737496803, 737496822, 737496823]

    for id in ids:
        optin_wallet(address, private_key, id)

    return {
        "address": address,
        "mnemonic": wallet_mnemonic,
        "private_key": private_key,
    }

def optin_wallet(address: str, private_key: str, ASA_ID: int):
    load_dotenv()
    ALGOD_ADDRESS = 'https://testnet-api.algonode.cloud'
    ALGOD_TOKEN = ''
    algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

    params = algod_client.suggested_params()

    optin_txn = AssetTransferTxn(
        sender=address,
        sp=params,
        receiver=address,
        amt=0,
        index=ASA_ID,
    )
    signed_optin = optin_txn.sign(private_key)
    txid = algod_client.send_transaction(signed_optin)
    wait_for_confirmation(algod_client, txid, 4)
    print("✅ Wallet opted in to ASA", ASA_ID)
    
def transfer_asa(
    receiver_address: str,
    asset_id: int,
    amount: int,
    price: int
) -> str:
    """
    Transfer ASA tokens to a specified wallet address
    
    Args:
        algod_address: Algorand node address
        algod_token: Algorand node token
        sender_mnemonic: Sender's mnemonic phrase
        receiver_address: Recipient's wallet address
        asset_id: ID of the ASA token
        amount: Amount of tokens to transfer
        
    Returns:
        Transaction ID of the transfer
    """
    ALGOD_ADDRESS = 'https://testnet-api.algonode.cloud'
    ALGOD_TOKEN = ''
    algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    
    load_dotenv()

    # Get sender's address and private key
    sender_mnemonic = os.getenv('MNEMONIC')
    print(sender_mnemonic)
    sender_private_key = mnemonic.to_private_key(sender_mnemonic)
    sender_address = account.address_from_private_key(sender_private_key)
    
    # Get network parameters
    params = algod_client.suggested_params()
    
    # Add note to transaction
    note = f"transferred *{asset_id}* coin to user *{receiver_address}* at *{price}*".encode()
    
    # Create asset transfer transaction
    txn = AssetTransferTxn(
        sender=sender_address,
        sp=params,
        receiver=receiver_address,
        amt=amount,
        index=asset_id,
        revocation_target=sender_address,
        note=note
    )
    
    # Sign transaction
    signed_txn = txn.sign(sender_private_key)
    
    # Send transaction
    txid = algod_client.send_transaction(signed_txn)
    print(f"Sent asset transfer transaction with ID: {txid}")
    
    # Wait for confirmation
    confirmed_txn = wait_for_confirmation(algod_client, txid)
    print(f"Asset transfer confirmed in round: {confirmed_txn['confirmed-round']}")
    
    return txid

def get_asa_balance(address: str, asset_id: int) -> int:
    """
    Get the balance of a specific ASA token for a wallet address
    
    Args:
        address: Wallet address to check
        asset_id: ID of the ASA token
        
    Returns:
        Amount of tokens owned by the address
    """
    ALGOD_ADDRESS = 'https://testnet-api.algonode.cloud'
    ALGOD_TOKEN = ''
    algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    
    # Get account info
    account_info = algod_client.account_info(address)
    
    # Look for the asset in the account's assets
    for asset in account_info['assets']:
        if asset['asset-id'] == asset_id:
            return asset['amount']
    
    return 0  # Return 0 if the asset is not found

def unfreeze_tokens(
    target_address: str,
    asset_id: int
):
    load_dotenv()
    ALGOD_ADDRESS = 'https://testnet-api.algonode.cloud'
    ALGOD_TOKEN = ''
    algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
    freeze_admin_mnemonic = os.getenv('MNEMONIC')
    private_key = mnemonic.to_private_key(freeze_admin_mnemonic)
    freeze_admin_address = account.address_from_private_key(private_key)

    params = algod_client.suggested_params()

    txn = AssetFreezeTxn(
        sender=freeze_admin_address,
        sp=params,
        index=asset_id,
        target=target_address,
        new_freeze_state=False
    )

    signed_txn = txn.sign(private_key)
    txid = algod_client.send_transaction(signed_txn)
    print(f"Sent unfreeze txn: {txid}")

    wait_for_confirmation(algod_client, txid)
    print(f"Tokens for {target_address} are now unfrozen.")

def burn_tokens(sender_address, asset_id, amount, price):
    ALGOD_ADDRESS = 'https://testnet-api.algonode.cloud'
    ALGOD_TOKEN = ''
    algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

    load_dotenv()

    params = algod_client.suggested_params()

    reserve_mnemonic = os.getenv('MNEMONIC')
    reserve_private_key = mnemonic.to_private_key(reserve_mnemonic)
    reserve_address = account.address_from_private_key(reserve_private_key)
    print('Reserve Address', reserve_address)

    # Create note with price info
    note = f"sold *{asset_id}* from user *{sender_address}* at *{price}*".encode()

    burn_txn = AssetTransferTxn(
        sender=reserve_address,  # Clawback address
        sp=params,
        receiver=reserve_address,  # Reserve address to receive tokens
        amt=amount,
        index=asset_id,
        revocation_target=sender_address,  # Address to clawback from
        note=note
    )
    signed_txn = burn_txn.sign(reserve_private_key)
    txid = algod_client.send_transaction(signed_txn)
    print(f"Sent burn txn: {txid}")
    
    wait_for_confirmation(algod_client, txid)
    print(f"Burn confirmed: {amount} tokens removed.")
        
def get_asa_transactions(address):
    ALGOD_ADDRESS = 'https://testnet-api.algonode.cloud'
    ALGOD_TOKEN = ''
    INDEXER_ADDRESS = 'https://testnet-idx.algonode.cloud'
    
    indexer_client = indexer.IndexerClient(ALGOD_TOKEN, INDEXER_ADDRESS)
    
    # List of ASA IDs to check
    asa_ids = [737489627, 737496803, 737496822, 737496823]
    
    # Dictionary to store transactions for each ASA
    asa_transactions = {}
    
    for asa_id in asa_ids:
        # Get transactions for the address and current ASA
        response = indexer_client.search_transactions(
            address=address,
            asset_id=asa_id
        )

        transactions = []
        if 'transactions' in response:
            for txn in response['transactions']:
                if 'asset-transfer-transaction' in txn:
                    asa_amount = txn['asset-transfer-transaction']['amount']
                    sender = txn['sender']
                    receiver = txn['asset-transfer-transaction']['receiver']
                    
                    # Determine if the transaction is a buy or sell
                    transaction_type = "buy" if receiver == address else "sell"
                    
                    # Get and decode the note if present
                    price = None
                    if 'note' in txn:
                        try:
                            note = base64.b64decode(txn['note']).decode('utf-8')
                            # Assuming price is stored in the note
                            price = float(note.split('*')[-2])
                        except:
                            continue
                            
                    if price is not None:
                        transactions.append({
                            'amount': asa_amount,
                            'price': price,
                            'txn_id': txn['id'],
                            'type': transaction_type
                        })
                        
        asa_transactions[asa_id] = transactions
        
    return asa_transactions
