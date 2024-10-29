from typing import Any, Dict, Iterator, List, Optional
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
import requests
from pydantic import SecretStr

class HyperCLOVAChatModel(BaseChatModel):
    """HyperCLOVA API를 위한 커스텀 채팅 모델.
    
    속성:
        host: API 호스트 URL
        api_key: HyperCLOVA API 키
        api_key_primary: 기본 API 게이트웨이 키
        request_id: 요청 식별자
        temperature: 창의성 부여 파라미터
        max_tokens: 생성할 최대 토큰 수
        top_p: Top-p 샘플링 파라미터
        top_k: Top-k 샘플링 파라미터
        repeat_penalty: 반복 토큰에 대한 패널티
    """
    
    host: str = "https://clovastudio.stream.ntruss.com"
    api_key: SecretStr = SecretStr("your_api_key")
    api_key_primary: SecretStr = SecretStr("your_api_key_primary")
    request_id: str = "your_request_id"
    
    temperature: float = 0.5
    max_tokens: int = 256
    top_p: float = 0.8
    top_k: int = 0
    repeat_penalty: float = 5.0
    
    def _convert_messages_to_clova_format(
        self, messages: List[BaseMessage]
    ) -> List[Dict[str, str]]:
        """LangChain 메시지를 HyperCLOVA 형식으로 변환."""
        clova_messages = []
        for message in messages:
            if isinstance(message, SystemMessage):
                clova_messages.append({"role": "system", "content": message.content})
            elif isinstance(message, HumanMessage):
                clova_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                clova_messages.append({"role": "assistant", "content": message.content})
        return clova_messages

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """채팅 응답 생성."""
        clova_messages = self._convert_messages_to_clova_format(messages)
        
        request_data = {
            "messages": clova_messages,
            "topP": self.top_p,
            "topK": self.top_k,
            "maxTokens": self.max_tokens,
            "temperature": self.temperature,
            "repeatPenalty": self.repeat_penalty,
            "stopBefore": stop if stop else [],
            "includeAiFilters": True,
            "seed": 0
        }
        
        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self.api_key.get_secret_value(),
            "X-NCP-APIGW-API-KEY": self.api_key_primary.get_secret_value(),
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self.request_id,
            "Content-Type": "application/json; charset=utf-8"
        }
        
        response = requests.post(
            f"{self.host}/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=request_data
        )
        
        # Parse the response and create an AIMessage
        response_text = response.json().get("content", "")
        message = AIMessage(content=response_text)
        
        return ChatResult(generations=[ChatGeneration(message=message)])
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """채팅 응답 스트리밍."""
        clova_messages = self._convert_messages_to_clova_format(messages)
        
        request_data = {
            "messages": clova_messages,
            "topP": self.top_p,
            "topK": self.top_k,
            "maxTokens": self.max_tokens,
            "temperature": self.temperature,
            "repeatPenalty": self.repeat_penalty,
            "stopBefore": stop if stop else [],
            "includeAiFilters": True,
            "seed": 0
        }
        
        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self.api_key.get_secret_value(),
            "X-NCP-APIGW-API-KEY": self.api_key_primary.get_secret_value(),
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self.request_id,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream"
        }
        
        with requests.post(
            f"{self.host}/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=request_data,
            stream=True
        ) as response:
            for line in response.iter_lines():
                if line:
                    # Assuming the response format matches what we need for streaming
                    # You might need to adjust this based on actual API response format
                    content = line.decode("utf-8")
                    chunk = ChatGenerationChunk(message=AIMessageChunk(content=content))
                    
                    if run_manager:
                        run_manager.on_llm_new_token(content, chunk=chunk)
                        
                    yield chunk
    
    @property
    def _llm_type(self) -> str:
        """LLM의 유형 반환."""
        return "hyperclova"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """식별 파라미터 반환."""
        return {
            "model_name": "HCX-003",
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repeat_penalty": self.repeat_penalty
        }
