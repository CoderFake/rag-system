import requests
import json
from backend.config.settings import Config 

class OllamaClient:
    def __init__(self):

        self.base_url = Config.OLLAMA_BASE_URL
        self.model_name = Config.OLLAMA_MODEL_NAME
        self.api_url = f"{self.base_url}/api/generate"

    def generate_response(self, prompt: str, stream: bool = False) -> str:
        if stream:

            print("Warning: Ollama streaming not yet implemented in this client.")
            return "Streaming not implemented."

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False 
        }
        
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload), timeout=120) 
            response.raise_for_status() 
            
            response_data = response.json()
            print(f"Received response from Ollama: {response_data}")
            

            if 'response' in response_data:
                return response_data['response'].strip()
            else:
                print(f"Error: 'response' key not found in Ollama output: {response_data}")
                return "Error: Could not parse Ollama response."

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama API at {self.api_url}: {e}")

            if isinstance(e, requests.exceptions.ConnectionError):
                return f"Error: Could not connect to Ollama at {self.base_url}. Is Ollama running?"
            return f"Error communicating with Ollama: {e}"
        except json.JSONDecodeError:
            print(f"Error decoding JSON response from Ollama: {response.text}")
            return "Error: Invalid response format from Ollama."
        except Exception as e:
            print(f"An unexpected error occurred while calling Ollama: {e}")
            return f"An unexpected error occurred: {e}"

