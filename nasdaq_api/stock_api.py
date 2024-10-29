# stock_api.py
import requests
import json
from datetime import datetime
from config import Config

class KoreanInvestmentAPI:
    def __init__(self):
        """Initialize the Korean Investment API client"""
        self.app_key = Config.APP_KEY
        self.app_secret = Config.APP_SECRET
        self.base_url = "https://openapi.koreainvestment.com:9443"
        self.access_token = None
        
    def get_access_token(self):
        """Get access token from Korean Investment API"""
        url = f"{self.base_url}/oauth2/tokenP"
        
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        headers = {
            "content-type": "application/json"
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            return self.access_token
        else:
            raise Exception(f"Failed to get access token: {response.text}")

    def get_stock_price(self, exchange: str, symbol: str) -> dict:
        """
        Get current stock price from Korean Investment API
        
        Args:
            exchange (str): Exchange code (e.g., 'NAS', 'NYS', 'HKS', etc.)
            symbol (str): Stock symbol (e.g., 'AAPL', 'TSLA', etc.)
            
        Returns:
            dict: Stock price information
        """
        if not self.access_token:
            self.get_access_token()
            
        url = f"{self.base_url}/uapi/overseas-price/v1/quotations/price"
        
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "HHDFS00000300"
        }
        
        params = {
            "AUTH": "",
            "EXCD": exchange,
            "SYMB": symbol
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result["rt_cd"] == "0":  # Success
                return {
                    "symbol": symbol,
                    "exchange": exchange,
                    "current_price": float(result["output"]["last"]),
                    "previous_close": float(result["output"]["base"]),
                    "change": float(result["output"]["diff"]),
                    "change_percent": float(result["output"]["rate"]),
                    "volume": int(result["output"]["tvol"]),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception(f"API Error: {result['msg1']}")
        else:
            raise Exception(f"Request failed: {response.text}")
