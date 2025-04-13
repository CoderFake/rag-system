import requests
import json
import logging
import time
from config.settings import Config

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, fallback_client=None):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model_name = Config.OLLAMA_MODEL_NAME
        self.api_url = f"{self.base_url}/api/generate"
        self.fallback_client = fallback_client
        self.model_ready = False
        self.model_loading = False
        

        self._check_connection()
        
    def _check_connection(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                logger.info(f"Kết nối thành công tới Ollama tại {self.base_url}")
                self._check_model()
            else:
                logger.error(f"Không thể kết nối tới Ollama API: {response.status_code}")
                logger.error(f"Sử dụng fallback (nếu có)")
        except Exception as e:
            logger.error(f"Lỗi kết nối tới Ollama: {str(e)}")
            logger.error(f"Sử dụng fallback (nếu có)")
    
    def _check_model(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            
            if response.status_code != 200:
                logger.error("Không thể lấy danh sách mô hình")
                return
                
            models_data = response.json()
            model_names = [model.get('name') for model in models_data.get('models', [])]
            
            if self.model_name in model_names:
                logger.info(f"Mô hình {self.model_name} đã có sẵn và sẵn sàng sử dụng")
                self.model_ready = True
            else:
                logger.info(f"Mô hình {self.model_name} chưa có sẵn, đang tải về")
                self._pull_model()
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra mô hình: {str(e)}")
    
    def _pull_model(self):
        if self.model_loading:
            return
            
        self.model_loading = True
        
        try:
            pull_url = f"{self.base_url}/api/pull"
            payload = {"name": self.model_name}
            
            import threading
            
            def download_model():
                try:
                    logger.info(f"Bắt đầu tải mô hình {self.model_name}")
                    response = requests.post(pull_url, json=payload, timeout=600)
                    
                    if response.status_code == 200:
                        logger.info(f"Đã tải xong mô hình {self.model_name}")
                        self.model_ready = True
                    else:
                        logger.error(f"Lỗi tải mô hình: {response.status_code}")
                except Exception as e:
                    logger.error(f"Lỗi khi tải mô hình: {str(e)}")
                finally:
                    self.model_loading = False
            
            thread = threading.Thread(target=download_model)
            thread.daemon = True
            thread.start()
            
            logger.info(f"Đã bắt đầu tải mô hình {self.model_name} trong background")
            logger.info(f"Đang sử dụng fallback (nếu có) trong thời gian chờ")
            
        except Exception as e:
            logger.error(f"Lỗi khi bắt đầu tải mô hình: {str(e)}")
            self.model_loading = False

    def generate(self, prompt, system_prompt=None, temperature=None):

        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
            
        temp_param = {}
        if temperature is not None:
            temp_param = {"temperature": float(temperature)}
            
        return self.generate_response(full_prompt, **temp_param)
    
    def generate_response(self, prompt: str, **kwargs) -> str:

        if not self.model_ready and self.fallback_client:
            logger.info(f"Mô hình Ollama {self.model_name} chưa sẵn sàng, sử dụng fallback")
            return self.fallback_client.generate(prompt=prompt)

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False 
        }
        
        for key, value in kwargs.items():
            payload[key] = value
        
        headers = {'Content-Type': 'application/json'}

        try:
            logger.debug(f"Gửi request tới Ollama: {self.api_url}")
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=120) 
            response.raise_for_status() 
            
            response_data = response.json()
            
            if 'response' in response_data:
                return response_data['response'].strip()
            else:
                logger.error(f"Không tìm thấy trường 'response' trong kết quả: {response_data}")

                if self.fallback_client:
                    logger.info("Sử dụng fallback do lỗi kết quả")
                    return self.fallback_client.generate(prompt=prompt)
                return "Lỗi: Không tìm thấy câu trả lời từ Ollama."

        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi kết nối tới Ollama API tại {self.api_url}: {e}")
            
            if self.fallback_client:
                logger.info("Sử dụng fallback do lỗi kết nối")
                return self.fallback_client.generate(prompt=prompt)
                
            if isinstance(e, requests.exceptions.ConnectionError):
                return f"Lỗi: Không thể kết nối tới Ollama tại {self.base_url}. Ollama có đang chạy không?"
            return f"Lỗi giao tiếp với Ollama: {e}"
        except json.JSONDecodeError:
            logger.error(f"Lỗi giải mã JSON từ Ollama")

            if self.fallback_client:
                logger.info("Sử dụng fallback do lỗi định dạng JSON")
                return self.fallback_client.generate(prompt=prompt)
            return "Lỗi: Định dạng phản hồi không hợp lệ từ Ollama."
        except Exception as e:
            logger.error(f"Lỗi không xác định khi gọi Ollama: {e}")

            if self.fallback_client:
                logger.info("Sử dụng fallback do lỗi không xác định")
                return self.fallback_client.generate(prompt=prompt)
            return f"Đã xảy ra lỗi không xác định: {e}"