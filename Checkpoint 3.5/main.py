import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# 1. Mühit dəyişənlərini .env faylından yükləyirik
load_dotenv()

# Təhlükəsizlik və Xəta İdarəetməsi (Error Handling)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "Kritik Xəta: OPENAI_API_KEY mühit dəyişəni tapılmadı! "
        "Xahiş olunur layihənin kök qovluğundakı .env faylını yoxlayın."
    )

# OpenAI Klientinin reallaşdırılması
client = OpenAI(api_key=api_key)

# 2. LOKAL ALƏTLƏRİN (TOOLS) TƏYİNİ

def get_weather(location: str) -> str:
    """
    Verilmiş məkan üçün cari hava şəraitini qaytaran lokal alət funksiyası (Mock API).
    
    :param location: Şəhər və ya region adı
    :return: Şəhər, temperatur və hava şəraitini ehtiva edən JSON mətni
    """
    loc_clean = location.strip().lower()
    
    # Şəhərlərə uyğun mock məlumatlar
    weather_data = {
        "baku": {"location": "Baku", "temperature": "28°C", "condition": "Günəşli"},
        "bakı": {"location": "Baku", "temperature": "28°C", "condition": "Günəşli"},
        "sumqayıt": {"location": "Sumqayıt", "temperature": "27°C", "condition": "Küləkli"},
        "gence": {"location": "Gəncə", "temperature": "25°C", "condition": "Buludlu"},
        "gəncə": {"location": "Gəncə", "temperature": "25°C", "condition": "Buludlu"}
    }
    
    if loc_clean in weather_data:
        return json.dumps(weather_data[loc_clean], ensure_ascii=False)
    
    # Siyahıda olmayan məkanlar üçün standart məlumat
    return json.dumps({
        "location": location,
        "temperature": "22°C",
        "condition": "Mənzərəli və sabit"
    }, ensure_ascii=False)

# 3. LLM ÜÇÜN ALƏT SXEMLƏRİ (JSON SCHEMA)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Verilmiş şəhər və ya məkan üzrə cari hava haqqında məlumatı qaytarır.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Hava məlumatı sorğulanacaq şəhər adı (məsələn: Baku, Sumqayıt)"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# Lokal funksiyaların adı ilə uyğunlaşdırılması üçün xəritə (Dictionary Mapping)
available_tools = {
    "get_weather": get_weather
}

# 4. İKİ MƏRHƏLƏLİ LLM AXINI (AGENT FUNKSİYASI)

def run_agent(user_prompt: str) -> str:
    """
    İstifadəçi sorğusunu emal edən, LLM ilə aləti ilişkiləndirən 
    və nəticəni təbii dildə geri qaytaran əsas idarəetmə funksiyası.
    """
    messages = [{"role": "user", "content": user_prompt}]
    
    print(f"\n[İstifadəçi Sorğusu]: {user_prompt}")

    # Addım 1: Birinci LLM çağırışı (Alət seçimi yoxlanılır)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # Addım 2: Əgər LLM alət (tool) çağırmağa qərar veribsə
    if tool_calls:
        # Birinci cavabı (tool_calls strukturunu) mesaj tarixçəsinə əlavə edirik
        messages.append(response_message)
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            
            # Çağırılacaq funksiyanın varlığını yoxlayırıq
            if function_name in available_tools:
                function_to_call = available_tools[function_name]
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"[LLM Alət Çağırışı]: '{function_name}' | Argument: {function_args}")
                
                # Lokal funksiyanı icra edirik
                tool_output = function_to_call(
                    location=function_args.get("location")
                )
                
                print(f"[Alət Nəticəsi (Raw Output)]: {tool_output}")
                
                # Nəticəni role: "tool" mətni ilə mesaj tarixçəsinə əlavə edirik
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_output
                })
        
        # Addım 3: İkinci LLM çağırışı (Təbii dildə yekun cavab)
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        return second_response.choices[0].message.content
    
    # Əgər hər hansı alətə ehtiyac yoxdursa, birbaşa ilkin cavabı qaytarırıq
    return response_message.content


# 5. SKRİPTİN İŞƏ SALINMASI

if __name__ == "__main__":
    prompt = "Bakıda hazırda hava necədir?"
    final_result = run_agent(prompt)
    print(f"\n[Sistem Yekun Cavabı]:\n{final_result}")
