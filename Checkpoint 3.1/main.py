import os
import json
from dotenv import load_dotenv
from langchain.tools import tool
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# .env faylından API açarını yükləyirik
load_dotenv()

# 1. TOOL DEFINITIONS (Aydın Sxemli Funksiyaların Yaradılması)

class WeatherInput(BaseModel):
    location: str = Field(
        description="Şəhər və ya ölkə adı (Nümunə: 'Bakı', 'İstanbul')"
    )
    unit: str = Field(
        default="celsius", 
        description="Temperatur vahidi: 'celsius' və ya 'fahrenheit'"
    )

@tool("get_current_weather", args_schema=WeatherInput)
def get_current_weather(location: str, unit: str = "celsius") -> str:
    """
    Qeyd olunan şəhər və ya məkan üçün cari hava şəraitini qaytarır.
    İstifadəçi müəyyən bir yerin havasını soruşduqda bu alət çağırılmalıdır.
    """
    # Real ssenaridə xarici Weather API müraciət edərdi
    mock_weather = {
        "Bakı": {"temp": 22, "condition": "Günəşli"},
        "İstanbul": {"temp": 18, "condition": "Buludlu"},
        "London": {"temp": 12, "condition": "Yağışlı"}
    }
    
    data = mock_weather.get(location, {"temp": 20, "condition": "Açıq"})
    return f"{location} üçün hava şəraiti {data['condition']} və temperatur {data['temp']} {unit}-dur."


class CalculatorInput(BaseModel):
    operation: str = Field(
        description="İcra olunacaq riyazi əməliyyat: 'add', 'subtract', 'multiply', 'divide'"
    )
    a: float = Field(description="Birinci ədəd")
    b: float = Field(description="İkinci ədəd")

@tool("calculator_tool", args_schema=CalculatorInput)
def calculator_tool(operation: str, a: float, b: float) -> str:
    """
    İki ədəd üzərində əsas riyazi əməliyyatları (toplama, çıxma, vurma, bölmə) yerinə yetirir.
    İstifadəçi hesablama tələb edən sual verdikdə istifadə olunmalıdır.
    """
    if operation == "add":
        res = a + b
    elif operation == "subtract":
        res = a - b
    elif operation == "multiply":
        res = a * b
    elif operation == "divide":
        res = a / b if b != 0 else "Xəta: Sıfıra bölmə!"
    else:
        res = "Yanlış əməliyyat"
    return str(res)


class UnitConverterInput(BaseModel):
    temperature: float = Field(description="Çevriləcək temperatur dəyəri")
    to_unit: str = Field(
        description="Hədəf temperatur vahidi: 'celsius' və ya 'fahrenheit'"
    )

@tool("convert_temperature", args_schema=UnitConverterInput)
def convert_temperature(temperature: float, to_unit: str) -> str:
    """
    Temperatur dəyərini Celsius-dan Fahrenheit-ə və ya Fahrenheit-dən Celsius-a çevirir.
    Temperatur vahidlərinin çevrilməsi lazım olduqda istifadə olunur.
    """
    if to_unit.lower() == "fahrenheit":
        converted = (temperature * 9/5) + 32
        return f"{temperature}°C = {converted:.1f}°F"
    elif to_unit.lower() == "celsius":
        converted = (temperature - 32) * 5/9
        return f"{temperature}°F = {converted:.1f}°C"
    return str(temperature)


# Alətlər dəstini təyin edirik və xəritələndiririk
tools = [get_current_weather, calculator_tool, convert_temperature]
tools_dict = {t.name: t for t in tools}

# 2. AGENT EXECUTION LOOP (Tool İcrası və Dövr Koruması)

def run_agent(user_query: str, max_iterations: int = 5):
    """
    LLM Function Calling məntiqini icra edən əsas funksiya.
    Sonsuz dövrə qarşı qoruma (max_iterations) ehtiva edir.
    """
    print(f"\n")
    print(f"[USER INQUIRY]: {user_query}")
    print(f" ")

    # LLM Modeli və Tool Bağlanması (Binding)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    messages = [HumanMessage(content=user_query)]
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1
        
        # LLM-dən cavab alırıq
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # Əgər model hər hansı bir alət çağırmayıbsa, yekun cavabı hazırlayıb
        if not response.tool_calls:
            print(f"\n[FINAL RESPONSE]: {response.content}")
            return response.content

        # Model bir və ya daha çox alət çağırmaq istədikdə
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            print(f"\n[AGENT THOUGHT]: Alətin çağırılması lazımdır -> {tool_name}")
            print(f"[ACTION]: {tool_name}({tool_args})")

            # Uyğun aləti tapırıq və icra edirik
            if tool_name in tools_dict:
                selected_tool = tools_dict[tool_name]
                observation = selected_tool.invoke(tool_args)
                print(f"[OBSERVATION]: {observation}")

                # Nəticəni mesaj tarixçəsinə ToolMessage kimi əlavə edirik
                messages.append(
                    ToolMessage(content=str(observation), tool_call_id=tool_call_id)
                )
            else:
                print(f"[ERROR]: {tool_name} adında bir alət tapılmadı!")

    print("\n[WARNING]: Maksimum təkrarlanma limitinə çatıldı! Sonsuz dövrün qarşısı alındı.")
    return "Əməliyyat çox uzun çəkdi, xahiş olunur sorğunuzu sadələşdirin."


if __name__ == "__main__":
    # Test 1: Sadə Tool istifadəsi
    run_agent("Bakıda hava necədir?")

    # Test 2: Zəncirvari (Sequential) Tool istifadəsi (Hava -> Çevrilmə)
    run_agent("Bakıda hava neçə dərəcədir və bu temperatur Fahrenheit ilə neçəyə bərabərdir?")
