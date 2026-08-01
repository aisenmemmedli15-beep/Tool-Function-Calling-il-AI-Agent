Bu layihə OpenAI API-nin `function_calling` (alət/tool icrası) mexanizmindən istifadə edərək Böyük Dil Modellərinin (LLM) xarici alətlərlə qarşılıqlı əlaqəsini və iki mərhələli məntiqi axınını (Two-Step Flow) nümayiş etdirən peşəkar Python tətbiqidir.
# Layihə Haqqında və Arxitekturası
LLM-lər daxili strukturları etibarilə canlı məlumatlara və ya daxili sistem funksiyalarına birbaşa çıxışa malik deyillər. Bu layihədə modelə JSON Sxemi (JSON Schema) formatında mövcud alətlərin tərifləri təqdim olunur. Model istifadəçinin sorğusunu təhlil edərək xarici alətə ehtiyac olub-olmadığını müəyyənləşdirir və uyğun parametrlərlə alət çağırışı (`tool_calls`) tələb edir.
# İki Mərhələli İcra Axını (Two-Step Execution Flow)

1. **Birinci LLM Çağırışı (Alət Seçimi):**
   - İstifadəçi sorğusu və təyin olunmuş alət sxemi (`tools`) OpenAI API-yə göndərilir.
   - Model sorğunu cavablandırmaq üçün `get_weather` funksiyasının çağırılmalı olduğuna qərar verir.

2. **Lokal Kodun İcrası (Tool Execution):**
   - Python skripti modeldən gələn parametrləri (`location`) oxuyur.
   - Lokal `get_weather` funksiyası icra olunur və xam JSON nəticəsi əldə edilir.

3. **İkinci LLM Çağırışı (Təbii Dildə Yekun Cavab):**
   - Funksiyanın nəticəsi `role: "tool"` mesaj tipi ilə söhbət tarixçəsinə əlavə edilir.
   - Yenilənmiş mesaj tarixçəsi yenidən OpenAI API-yə göndərilir və model istifadəçiyə təbii dildə, anlaşıqlı cavab formalaşdırır.

# Layihənin Fayl Strukturu

```text
.
├── main.py           # İki mərhələli LLM və alət icrası axınını idarə edən əsas Python faylı
├── .env.example      # Mühit dəyişənləri üçün nümayişçi şablon fayl (API Key təlimatı)
├── .gitignore        # Məxfi faylların (.env, venv) GitHub-a sızmasının qarşısını alır
├── requirements.txt  # Layihə üçün tələb olunan kitabxanaların siyahısı
└── README.md         # Layihə sənədləşməsi və quraşdırma təlimatı
