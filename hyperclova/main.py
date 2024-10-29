from clova import HyperCLOVAChatModel
import sys
from langchain_core.messages import HumanMessage
import json

def main():
    # HyperCLOVA 챗봇 모델 초기화
    chat_model = HyperCLOVAChatModel(
        temperature=0.7,
        max_tokens=256,
        top_p=0.8,
        top_k=0,
        repeat_penalty=5.0
    )
    
    print("챗봇과 대화를 시작합니다. 종료하려면 'quit' 또는 'exit'를 입력하세요.")
    
    while True:
        # 사용자 입력 받기
        user_input = input("\n사용자: ")
        
        # 종료 조건 확인
        if user_input.lower() in ['quit', 'exit']:
            print("대화를 종료합니다.")
            break
            
        print("\n챗봇: ", end='', flush=True)
        
        try:
            messages = [HumanMessage(content=user_input)]
            
            for chunk in chat_model.stream(messages):
                if "data:" in chunk.content:
                    try:
                        data_str = chunk.content.split("data:")[1].strip()
                        data = json.loads(data_str)
                        if 'message' in data and 'content' in data['message']:
                            content = data['message']['content']
                            if content:  # 빈 문자열이 아닌 경우에만 출력
                                print(content, end='', flush=True)
                    except json.JSONDecodeError:
                        continue
            print()  # 줄바꿈
            
        except Exception as e:
            print(f"\n오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        sys.exit(0)