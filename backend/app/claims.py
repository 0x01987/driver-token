from eth_account import Account
from eth_account.messages import encode_typed_data

from app.config import get_settings


def build_claim_typed_data(wallet: str, ride_hash: str, amount: int, nonce: int) -> dict:
    settings = get_settings()
    return {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Claim": [
                {"name": "driver", "type": "address"},
                {"name": "rideHash", "type": "bytes32"},
                {"name": "amount", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
            ],
        },
        "primaryType": "Claim",
        "domain": {
            "name": "DriverToken",
            "version": "1",
            "chainId": settings.chain_id,
            "verifyingContract": settings.driver_token_contract,
        },
        "message": {
            "driver": wallet,
            "rideHash": ride_hash,
            "amount": amount,
            "nonce": nonce,
        },
    }


def sign_claim(wallet: str, ride_hash: str, amount: int, nonce: int) -> str:
    typed_data = build_claim_typed_data(wallet, ride_hash, amount, nonce)
    message = encode_typed_data(full_message=typed_data)
    signed = Account.sign_message(message, get_settings().claim_signer_private_key)
    return signed.signature.hex()
