import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Ətraf mühit dəyişənlərini yükləyirik
load_dotenv()

# OpenAI müştərisini başladırıq
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. Həqiqi icra olunacaq Python funksiyası
def get_weather(location):
    """Verilmiş məkan üçün hava durumunu qaytarır (Simulyasiya)"""
    if "baku" in location.lower():
        return json.dumps({"location": "Baku", "temperature": "24°C", "condition": "Sunny"})
    return json.dumps({"location": location, "temperature": "Unknown", "condition": "Clear"})

# 2. LLM-ə təqdim olunacaq Tool sxemi (Tool Definition)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Müəyyən bir məkan üçün cari hava durumunu əldə etmək üçün istifadə olunur.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Şəhər və ya rayon adı, məsələn: Baku, London",
                    }
                },
                "required": ["location"],
            },
        },
    }
]

def run_conversation(user_prompt):
    print(f"İstifadəçi sorğusu: {user_prompt}\n")
    
    # Sorğunu və alətləri LLM-ə göndəririk
    messages = [{"role": "user", "content": user_prompt}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto" # Model aləti seçib-seçməməyə özü qərar verir
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # Model bir tool çağırmağa qərar verdisə:
    if tool_calls:
        print(" LLM Uğurla Tool Seçimi Etdi!")
        available_functions = {"get_weather": get_weather}
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"Çağırılan Funksiya: {function_name}")
            print(f"Model tərəfindən çıxarılan arqumentlər: {function_args}")
            
            # Həqiqi funksiyanı işlədirik
            function_response = function_to_call(location=function_args.get("location"))
            print(f"Funksiyanın Cavabı: {function_response}\n")
            
    else:
        print("Model hər hansı bir tool seçmədi, birbaşa cavab verdi:")
        print(response_message.content)

# Test edirik
if __name__ == "__main__":
    run_conversation("Bakıda hazırda hava necədir?")
