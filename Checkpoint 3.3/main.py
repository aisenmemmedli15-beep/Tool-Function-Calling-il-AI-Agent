import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# 1. Mühit dəyişənlərini (.env faylından) yükləyirik [cite: 26, 28]
load_dotenv()

# API açarını təhlükəsiz şəkildə oxuyuruq [cite: 20]
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("XƏTA: OPENAI_API_KEY mühit dəyişəni tapılmadı! .env faylını kontrol edin.")

client = OpenAI(api_key=api_key)


# 2. TOOL (ALƏT) FUNKSİYALARININ TƏRİFİ

def get_weather(location: str) -> str:
    """
    Verilmiş şəhər üçün hava durumu məlumatını qaytarır (Simulyasiya/API).
    """
    location_lower = location.lower()
    if "baku" in location_lower or "bakı" in location_lower:
        return json.dumps({"location": "Baku", "temperature": "22°C", "condition": "Günəşli", "humidity": "60%"})
    elif "sumqayit" in location_lower or "sumqayıt" in location_lower:
        return json.dumps({"location": "Sumqayıt", "temperature": "20°C", "condition": "Küləkli", "humidity": "65%"})
    else:
        return json.dumps({"location": location, "temperature": "18°C", "condition": "Buludlu", "humidity": "70%"})


# Alət adları ilə funksiyaların xəritələnməsi (Mapping)
available_tools = {
    "get_weather": get_weather
}

# 3. OPENAI TOOL SCHEMAS (LLM üçün alət tərifi)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Müəyyən olunmuş şəhər və ya məkan üçün cari hava durumu məlumatını gətirir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Hava durumu öyrənilmək istənən şəhər adı (məs: Bakı, Sumqayıt)",
                    }
                },
                "required": ["location"],
            },
        },
    }
]


# 4. AGENT / TOOL EXECUTION LOGIC (Əsas Məntiq)

def run_agent(user_query: str):
    """
    LLM alət icrası və nəticənin təbii dildə qaytarılması axını.
    """
    print(f"\nİstifadəçi Sorğusu: '{user_query}'")
    print("-" * 50)

    # Dialoq tarixçəsini başladırıq
    messages = [
        {
            "role": "system",
            "content": "Sən köməkçil bir asistansan. İstifadəçinin suallarına cavab vermək üçün təqdim edilən alətlərdən (tools) istifadə edirsən."
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    # ADDIM A: İLK LLM ZƏNGİ (LLM-in Alət seçimi) 
    print("[1] LLM-ə sorğu göndərilir və alət seçimi gözlənilir...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # ADDIM B: ALƏTİN İCRASI VA NƏTİCƏNİN QAYTARILMASI
    if tool_calls:
        # LLM-in cavabını tarixçəyə əlavə edirik
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"[2] LLM alət çağırmağa qərar verdi: Funksiya -> '{function_name}', Argumentlər -> {function_args}")

            # Funksiyanı icra edirik
            if function_name in available_tools:
                function_to_call = available_tools[function_name]
                tool_output = function_to_call(location=function_args.get("location"))
                
                print(f"[3] Tool uğurla icra olundu. Qaytarılan Xam Nəticə: {tool_output}")

                # Tool nəticəsini LLM-ə qaytarmaq üçün mesajlar siyahısına əlavə edirik 
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_output,
                    }
                )

        # ADDIM C: İKİNCİ LLM ZƏNGİ (Təbii dildə yekun cavabın alınması) 
        print("[4] Tool nəticəsi LLM-ə geri ötürülür və yekun cavab hazırlanır...")
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        final_answer = second_response.choices[0].message.content
        print("\n=== YEKUN CAVAB (Təbii Dildə) ===")
        print(final_answer)
        return final_answer
    else:
        # Əgər LLM alət çağırmadan birbaşa cavab veribsə
        print("\n=== YEKUN CAVAB (Alətsiz Cavab) ===")
        print(response_message.content)
        return response_message.content

# 5. TEST İCRA

if __name__ == "__main__":
    # Checkpoint 3 sınaq sorğusu
    run_agent("Bakıda hava hazırda necədir?")
