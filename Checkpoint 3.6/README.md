# AI Agent with Tool Calling & Detailed Debug Logging
Bu layihə OpenAI GPT-4o-mini modeli vasitəsilə alətlərin (Tools / Function Calling) dinamik çağırılmasını və agentin düşünmə (reasoning) mərhələlərinin **struktuılaşdırılmış loglanmasını** nümayiş etdirir.
# Özəlliklər
- **Aydın Debug Loglanması:** Python `logging` modulu vasitəsilə `[AGENT START]`, `[REASONING]`, `[TOOL CALL DETECTED]`, `[TOOL EXECUTION]` və `[TOOL OUTPUT]` mərhələləri izlənilir.
- **Təhlükəsiz Mühit:** API açarları `.env` faylında saxlanılır.
- **Sonsuz Dövr Qoruması:** İcra axını 2-mərhələli idarə olunan sistem üzərində qurulub.
# Quraşdırma və İşə Salma

1. Repozitoriyanı klonlayın və virtuallaşdırma mühitini yaradın:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows üçün: venv\Scripts\activate
