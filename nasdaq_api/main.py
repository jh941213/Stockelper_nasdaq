from stock_api import KoreanInvestmentAPI

def get_nasdaq_price(symbol: str) -> None:
    """
    나스닥 주식의 현재 가격을 조회하고 출력하는 함수
    
    Args:
        symbol (str): 종목 코드 (예: 'AAPL', 'TSLA' 등)
    """
    try:
        api = KoreanInvestmentAPI()
        stock_info = api.get_stock_price("NAS", symbol)
        
        print(f"\n{symbol} 주식 정보:")
        print(f"현재 가격: ${stock_info['current_price']:.2f}")
        print(f"변동: ${stock_info['change']:.2f} ({stock_info['change_percent']:.2f}%)")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")

def main():
    print("나스닥 주식 가격 조회 프로그램")
    print("종료하려면 'q'를 입력하세요.")
    
    while True:
        symbol = input("\n주식 심볼을 입력하세요: ").upper()
        
        if symbol.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
            
        get_nasdaq_price(symbol)

if __name__ == "__main__":
    main()