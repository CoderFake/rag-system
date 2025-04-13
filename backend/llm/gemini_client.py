import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro", 
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=2048
        )
        
    def generate(self, prompt, system_prompt=None, temperature=None):
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
            
        messages.append(HumanMessage(content=prompt))
        

        try:
            if temperature is not None:
                response = self.llm.generate([messages], temperature=temperature)
            else:
                response = self.llm.generate([messages])
                
            return response.generations[0][0].text
        except TypeError as e:
            if "unexpected keyword argument 'temperature'" in str(e):

                response = self.llm.generate([messages])
                return response.generations[0][0].text
            else:
                raise e
        
    def classify_query(self, query):
        system_prompt = """
        You are a query classifier that determines if a query requires retrieving 
        information from a knowledge base (RAG) or if it's just a conversational query (Chitchat).
        Respond with ONLY 'RAG' or 'Chitchat'.
        """
        
        try:
            result = self.generate(
                prompt=query,
                system_prompt=system_prompt,
                temperature=0.1
            ).strip().lower()
        except:
            result = self.generate(
                prompt=query,
                system_prompt=system_prompt
            ).strip().lower()
        
        if "rag" in result:
            return "RAG"
        else:
            return "Chitchat"