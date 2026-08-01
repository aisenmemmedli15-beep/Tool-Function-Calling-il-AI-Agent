import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# 1. Mühit dəyişənlərini (.env faylından) yükləyirik
load_dotenv()

# OpenAI API açarını əldə edirik
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("XƏTA: OPENAI_API_KEY .env faylında tapılmadı! Lütfən .env faylınızı yoxlayın.")

# OpenAI klientini başlatırıq
client = OpenAI(api_key=api_key)


# 2. Xarici alət (Tool) funksiyasının təyini
def get_weather(location: str) -> str:
    """
    Verilmiş şəhər üçün hava məlumatını simulasiya edən lokal alət funksiyası.
    """
    # Real ssenarilərdə burada xarici Hava Məlumatı API-nə sorğu göndərilir.
    weather_data = {
        "baku": {"temperature": "24°C", "condition": "Güneşli", "humidity": "50%"},
        "bakı": {"temperature": "24°C", "condition": "Güneşli", "humidity": "50%"},
        "london": {"temperature": "15°C", "condition": "Yağışlı", "humidity": "80%"},
        "tokyo": {"temperature": "18°C", "condition": "Buludlu", "humidity": "65%"}
    }
    
    city_key = location.lower().strip()
    data = weather_data.get(city_key, {"temperature": "20°C", "condition": "Açıq", "humidity": "55%"})
    
    return json.dumps({
        "location": location,
        "temperature": data["temperature"],
        "condition": data["condition"],
        "humidity": data["humidity"]
    })


# 3. LLM üçün Alət Sxemlərinin (Tool Schemas) Təyin Olunması
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Verilmiş şəhər və ya məkan üçün cari hava şəraiti məlumatını qaytarır.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Hava məlumatı istənilən şəhərin adı (məsələn: Bakı, London)."
                    }
                },
                "required": ["location"]
            }
        }
    }
]


def run_agent(user_prompt: str):
    """
    LLM Tool Execution axınını idarə edən əsas funksiya:
    Addım 1: İstifadəçi sorğusunu və alətləri LLM-ə göndərir.
    Addım 2: LLM alət icrası (tool call) istəyərsə, müvafiq Python funksiyasını çalışdırır.
    Addım 3: İcra nəticəsini LLM-ə geri qaytararaq təbii dildə yekun cavab alır.
    """
    print(f"\n💬 İstifadəçi Sorğusu: '{user_prompt}'\n" + "-"*50)
    
    # Dialoq tarixçəsi
    messages = [
        {"role": "system", "content": "Sən istifadəçilərin suallarına dəqiq və köməkçil cavablar verən AI köməkçisisən."},
        {"role": "user", "content": user_prompt}
    ]

    # ADDIM 1: İlk LLM Çağırışı (Alət sxemləri ilə birlikdə)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"  # LLM alət istifadə edib-etməyəcəyinə özü karar verir
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # LLM-in ilk cavabını dialoq tarixçəsinə əlavə edirik
    messages.append(response_message)

    # ADDIM 2: Alət İcrası (Tool Execution) Kontrolü
    if tool_calls:
        print("🛠️ LLM Alət icra etmək qərarına gəldi!")
        
        # Mövcud lokal funksiyaların xəritəsi
        available_functions = {
            "get_weather": get_weather,
        }

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            print(f" İcra olunan alət: {function_name}")
            print(f" Ötürülən argumentlər: {function_args}")

            # Lokal Python funksiyasını çağırırıq
            function_response = function_to_call(
                location=function_args.get("location")
            )
            
            print(f" Alətin qaytardığı ham nəticə (JSON): {function_response}\n")

            # ADDIM 3: Alət nəticəsini "tool" rolu ilə tarixçəyə əlavə edirik
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

        # Yekun Cavab Çağırışı: Alət nəticələri ilə 2-ci dəfə LLM-ə sorğu göndəririk
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        final_answer = second_response.choices[0].message.content
        print(f" Yekun AI Cavabı:\n{final_answer}")
        return final_answer
        
    else:
        # LLM alət çalıştırmağa ehtiyac duymadısa doğrudan cavab verir
        print(f" LLM harici alət icrasına ehtiyac duymadı.")
        print(f" AI Cavabı:\n{response_message.content}")
        return response_message.content


# Kodu işə salmaq üçün əsas blok
if __name__ == "__main__":
    # Test sorğusu
    query = "İndi Bakıda hava necədir?"
    run_agent(query)
