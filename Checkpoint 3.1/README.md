# Tool / Function Calling ilə AI Agent (Devjoint Təcrübə Proqramı - 3-cü Həftə)

Bu layihə **Devjoint Təcrübə Proqramının** 3-cü həftəlik **"Tool/Function Calling ilə AI Agent"** tapşırığı çərçivəsində hazırlanmışdır. Layihənin əsas məqsədi Böyük Dil Modelinin (LLM) istifadəçi niyyətini anlayaraq xarici funksiyaları (alətləri) dəqiq təyin etməsini, icra etməsini və nəticələri təbii dildə cavablandırmasını təmin etməkdir.
# Layihənin Məqsədi (Project Purpose)
1. **Aydın Sxematik Tool Tərifləri:** LangChain və Pydantic istifadə edərək adı, təsviri (description) və parametr tipləri dəqiq müəyyən edilmiş alətlər yaratmaq.
2. **Niyyət Analizi və Tool Seçimi:** LLM-in istifadəçi sorğusundan alət ehtiyacını müəyyən etməsi (Function Calling).
3. **İcra Dövrəsi (Execution Loop) və Söhbət Tarixçəsi:** Modelin qaytardığı JSON alət çağırışlarının Python mühitində icra olunması, nəticələrin `ToolMessage` kimi söhbət tarixçəsinə əlavə edilməsi və yekun cavabın formalaşdırılması.
4. **Çoxlu / Zəncirvari İstifadə (Sequential Calling):** Tək bir sorğuda birdən çox alətin ardıcıllıqla işlədilməsi (Məsələn: Əvvəlcə havanı öyrən -> Sonra dərəcəni Fahrenheit-ə çevir).
5. **Sonsuz Döngə Mühafizəsi:** `max_iterations` məhdudiyyəti ilə agentin sonsuz döngəyə girməsinin qarşısının alınması.

# Necə İşləyir? (How It Works)

1. **İstifadəçi Sorğusu:** İstifadəçi təbii dildə sual verir.
2. **Function Calling:** LLM mövcud alətlərin JSON sxemlərini (Pydantic schemas) nəzərdən keçirir. Əgər alətə ehtiyac varsa, `tool_calls` çıxışı yaradır.
3. **Execution Loop:** Python kodu bu çağırışı tutur, müvafiq funksiyanı düzgün parametrlərlə icra edir (`Observation`).
4. **Söhbət Tarixçəsinin Yenilənməsi:** Əldə edilən xam məlumat `ToolMessage` kimi tarixçəyə əlavə olunur və yenidən LLM-ə təqdim edilir.
5. **Yekun Cavab:** LLM xam məlumatları sintez edərək istifadəçiyə axıcı dildə cavab qaytarır.
