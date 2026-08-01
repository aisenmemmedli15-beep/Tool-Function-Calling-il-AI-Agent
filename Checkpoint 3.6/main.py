import os
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI

# 1. LOGGING KONFİQURASİYASI (Debug üçün aydın loglama)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("AgentLogger")

# Mühit dəyişənlərini yükləyirik
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.critical("Kritik Xəta: OPENAI_API_KEY tapılmadı!")
    raise ValueError("OPENAI_API_KEY mühit dəyişəni tapılmadı! .env faylını yoxlayın.")

client = OpenAI(api_key=api_key)

# 2. LOKAL ALƏTLƏR (TOOLS)
def get_weather(location: str) -> str:
    """Verilmiş məkan üçün cari hava şəraitini qaytaran alət."""
    logger.debug(f"[TOOL EXECUTION] 'get_weather' funksiyası çağırıldı. Məkan: {location}")
    loc_clean = location.strip().lower()
    
    weather_data = {
        "baku": {"location": "Baku", "temperature": "28°C", "condition": "Günəşli"},
        "bakı": {"location": "Baku", "temperature": "28°C", "condition": "Günəşli"},
        "sumqayıt": {"location": "Sumqayıt", "temperature": "27°C", "condition": "Küləkli"},
        "gence": {"location": "Gəncə", "temperature": "25°C", "condition": "Buludlu"},
        "gəncə": {"location": "Gəncə", "temperature": "25°C", "condition": "Buludlu"}
    }
    
    result = weather_data.get(loc_clean, {
        "location": location,
        "temperature": "22°C",
        "condition": "Mənzərəli və sabit"
    })
    
    output = json.dumps(result, ensure_ascii=False)
    logger.debug(f"[TOOL OUTPUT] 'get_weather' nəticəsi: {output}")
    return output

# 3. ALƏT SXEMLƏRİ
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
                        "description": "Hava məlumatı sorğulanacaq şəhər adı"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

available_tools = {"get_weather": get_weather}

# 4. AGENT FUNKSİYASI VƏ LOGLANMA AXINI
def run_agent(user_prompt: str) -> str:
    logger.info(f"[AGENT START] Yeni sorğu qəbul edildi: '{user_prompt}'")
    messages = [{"role": "user", "content": user_prompt}]
    
    logger.debug("[LLM CALL 1] Birinci LLM çağırışı icra olunur (Reasoning & Tool Selection)...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    if tool_calls:
        logger.info(f"[REASONING] LLM {len(tool_calls)} ədəd alət çağırmağa qərar verdi.")
        messages.append(response_message)
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            logger.info(f"[TOOL CALL DETECTED] Tool: '{function_name}' | Argumentlər: {function_args} | Call ID: {tool_call.id}")
            
            if function_name in available_tools:
                function_to_call = available_tools[function_name]
                tool_output = function_to_call(location=function_args.get("location"))
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_output
                })
                logger.debug(f"[CONTEXT UPDATED] Tool cavabı mesaj tarixçəsinə əlavə edildi.")
            else:
                logger.warning(f"[TOOL NOT FOUND] '{function_name}' adlı funksiya mövcud deyil!")
        
        logger.debug("[LLM CALL 2] İkinci LLM çağırışı icra olunur (Yekun cavabın sintezi)...")
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        final_answer = second_response.choices[0].message.content
        logger.info("[AGENT COMPLETE] Agent icranı uğurla başa vurdu.")
        return final_answer

    logger.info("[REASONING] LLM heç bir alətə ehtiyac duymadı, birbaşa cavab hazırladı.")
    return response_message.content

if __name__ == "__main__":
    prompt = "Bakıda hazırda hava necədir?"
    final_result = run_agent(prompt)
    print(f"\n[YEKUN CAVAB]: {final_result}")
