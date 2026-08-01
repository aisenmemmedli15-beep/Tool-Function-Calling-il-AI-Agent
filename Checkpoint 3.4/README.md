# LLM Tool Execution Project 
Bu layihə, böyük dil modellərinin (LLM) xarici alətlərlə (Tools/Functions) inteqrasiyasını və iki mərhələli sorğu axınını həyata keçirən Python tətbiqidir. Tətbiq alətlərin icrasından əldə olunan nəticələri LLM-ə geri ötürərək təbii dildə yekun cavablar formallaşdırır.
# Layihənin Xüsusiyyətləri

* **İki mərhələli LLM axını:** LLM sorğusunu alət çağırışına yönləndirmə və alınan cavabı təbii dilə çevirmə.
* **Təhlükəsiz Konfiqurasiya:** API açarları və mühit dəyişənləri `.env` faylında təhlükəsiz şəkildə saxlanılır.
* **Xətaların İdarə Edilməsi (Error Handling):** İcra zamanı yaranan istisnaların (exception) tutulması və idarə olunması.
* **Modulyar Kod Strukturu:** İstehsalat (production) standartlarına uyğun oxunulabilən architecture.
# Quraşdırma və İşə Salma Addımları
# 1. Repozitoriyanı Klonlayın
```bash
git clone [https://github.com/istifadəçi-adınız/repo-adınız.git](https://github.com/istifadəçi-adınız/repo-adınız.git)
cd repo-adınız
