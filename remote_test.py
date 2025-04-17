import requests
import json

def test_buy_tokens():
    # API endpoint URL
    url = "https://demo-4-hedges.onrender.com/coins/buy"
    
    # Request data
    data = {
        "address": "KYNAULXI2ZQWRRWVG5FCA3NK3WAYUXP6KNFE3HVWZUWYZRJK4KOYQIK2SY",
        "asa_id": 737496803,  # ASA ID for the token
        "amount": 10,         # Amount of tokens to buy
        "price": 1000     # Price in microAlgos
    }
    
    try:
        # Make POST request to buy tokens
        response = requests.post(url, json=data)
        
        # Check if request was successful
        if response.status_code == 200:
            # Parse response JSON
            result = response.json()
            
            print("✅ Tokens purchased successfully!")
            print("📫 Address:", result["address"])
            print("🪙 ASA ID:", result["asa_id"]) 
            print("💰 Price:", result["price"])
            
            return result
            
        else:
            print("❌ Failed to purchase tokens")
            print("Status code:", response.status_code)
            print("Error:", response.text)
            return None
            
    except Exception as e:
        print("❌ Error occurred:")
        print(str(e))
        return None

if __name__ == "__main__":
    test_buy_tokens()
