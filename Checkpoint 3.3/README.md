Layihənin əsas məqsədi OpenAI API-nin `function_calling` mexanizmindən istifadə edərək **Alət (Tool) icrası + nəticələrin LLM-ə geri verilib təbii dildə yekun cavab alınması** axınını realizə etməkdir.

# Layihənin İş Prinsipi və Arxitekturası
Layihə 4 əsas mərhələdən ibarət iki yönlü LLM çağırış axını ilə işləyir:

1. **Sorğunun Qəbulu və Tool Tərifi:** İstifadəçi sorğusu (`main.py` vasitəsilə) OpenAI modelinə təyin edilmiş JSON alət şablonları (`tools`) ilə birlikdə ötürülür.
2. **LLM-in Qərarı (Tool Calling):** Model daxil olan sorğunu analiz edir və müvafiq funksiyanın daxili məlumatlar əvəzinə xarici alət vasitəsilə icra edilməli olduğuna qərar verərək `tool_calls` parametri qaytarır.
3. **Lokal Funksiyanın İcrası (Tool Execution):** Python mühitində uyğun lokal alət (məsələn, `get_weather`) işə salınır və əldə olunan JSON formatındakı nəticə qəbul edilir.
4. **Yekun Cavabın Təbii Dildə Hazırlanması:** Lokal alətdən alınan nəticə `role: "tool"` kimliyi ilə dialoq tarixçəsinə əlavə olunur və LLM-ə 2-ci zəng edilir. Model bu nəticəni emal edərək istifadəçiyə səlis, təbii dildə yekun cavab təqdim edir.

# Fayl Strukturu

```text
.
├── main.py              # LLM agent məntiqi və Tool execution axını
├── requirements.txt     # Lazımi Python kitabxanaları
├── .env.example         # Mühit dəyişənləri üçün şablon faylı
├── .gitignore           # Git tərəfindən izlənilməyəcək fayllar (.env, venv/)
└── README.md            # Layihə haqqında geniş texniki sənədləşmə
