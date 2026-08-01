# LLM Tool Selection & Function Calling Project

Bu layihə, istifadəçi sorğularına əsasən LLM-in (Large Language Model) düzgün aləti (tool) seçməsini və arqumentləri generasiya etməsini nümayiş etdirir.
# Proqramın İşləmə Strukturu
 Layihə **OpenAI Function Calling** API-dan istifadə edir.
 Sxemləri təyin olunmuş funksiyalar modelə `tools` parametri ilə ötürülür.
 Model istifadəçinin təbii dil sorğusunu analiz edərək lazımi funksiyanı (`get_weather`) və arqumentləri (`Baku`) təyin edir.
# Quraşdırma
1. Virtual mühiti aktivləşdirin və asılılıqları yükləyin:
   ```bash
   pip install -r requirements.txt
