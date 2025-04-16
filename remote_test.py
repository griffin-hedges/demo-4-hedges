import requests
import json

def test_generate_wallet():
    # API endpoint URL
    url = "https://demo-4-hedges.onrender.com/wallet/generate"
    
    try:
        # Make POST request to generate wallet
        response = requests.post(url)
        
        # Check if request was successful
        if response.status_code == 200:
            # Parse response JSON
            wallet_data = response.json()
            
            print("✅ Wallet generated successfully!")
            print("📫 Address:", wallet_data["wallet_address"])
            print("🔑 Private key:", wallet_data["private_key"])
            print("🔐 Mnemonic:", wallet_data["mnemonic"])
            
            return wallet_data
            
        else:
            print("❌ Failed to generate wallet")
            print("Status code:", response.status_code)
            print("Error:", response.text)
            return None
            
    except Exception as e:
        print("❌ Error occurred:")
        print(str(e))
        return None

if __name__ == "__main__":
    test_generate_wallet()
