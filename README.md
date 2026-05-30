<div align="center">

# 🌐 MRR Programlama Dili: Tersine Mühendislik, Malware geliştirme, Tool geliştirme ve Kernel Seviye programlamada 1. seviye
**Mikroişlemciden Bulut Mimarisi ve Kernel Mühendislik İŞTE BU MRR

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-purple)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)

</div>

<br/>

## Önsöz: Neden MRR?

Yazılım dünyasında pek çok dil bulunur. MRR (Memory, Registers, Rings) ise bir siber güvenlik uzmanının, işletim sisteminin Ring 0 (Çekirdek - Kernel) ve Ring 3 (Kullanıcı - Userland) seviyeleri arasında rahatça gezinmesini sağlamak, ancak bunu modern dillerin sadeliğinde sunmak için tasarlanmıştır. Bu kitapta, her bir kod parçasını tam **8 farklı boyutta** inceleyeceğiz: Dördü kodun yazılımsal felsefesini, diğer dördü ise işlemci ve donanımda yarattığı fiziksel yankıları anlatacak.

---

## BÖLÜM 1: İlk Adım ve "Merhaba Dünya"

```mrr
print("Merhaba, Siber Dünya!")
```

### 💻 Yazılımsal Analiz (Software Architecture)
**Sözdizimi ve Kullanım Amacı:** `print` komutu, MRR dilinde kullanıcıya veya konsol (terminal) ekranına metin tabanlı çıktı vermek için kullanılan en temel standart kütüphane (stdlib) fonksiyonudur. Yeni satıra inmez, imleci metnin bittiği yerde bırakır. Geliştiriciler bu komutu genellikle log kayıtlarını veya kullanıcıya verilecek basit geri bildirimleri ekrana yansıtmak için tercih eder.
**Derleyici (Compiler) Davranışı:** Derleyici (Lexer ve Parser), kodu okuduğunda `print` kelimesini bir anahtar kelime (keyword) veya tanımlı fonksiyon olarak AST (Soyut Sözdizimi Ağacı) üzerinde işaretler. Parantez içindeki metni ise değişmez bir karakter dizisi (String Literal) olarak semantik analize sokar. Eğer veri tipi uygunsa, kod bir sonraki aşamaya geçer.
**Yazılımsal Güvenlik ve Bellek Kontrolü:** Yazılım seviyesinde bu komut oldukça masumdur, ancak içine siber saldırganların format string zafiyeti (örn: `%s%n`) sokmasını engellemek için MRR, bu girdileri dahili bir sanitizasyon (temizleme) süzgecinden geçirir. Yazılımcı bu komutu çalıştırdığında bellek taşması riski minimuma indirilmiş olur.
**İşletim Sistemi Bağımsızlığı:** Bu komut yazılım düzeyinde evrensel bir arayüze (Interface) sahiptir. Siz sadece `print` yazarsınız, ancak MRR motoru arkada Windows'ta `WriteConsole`, Linux'ta ise standart POSIX arayüzlerini tetikleyecek şekilde yazılımsal köprüleri (wrappers) otomatik olarak yönetir.

### ⚙️ Donanımsal Analiz (Hardware & Physical Layer)
**RAM ve Sanal Bellek Tahsisi:** Çalıştırılabilir dosyanız yüklendiğinde, "Merhaba, Siber Dünya!" metni İşletim Sisteminin Bellek Yöneticisi tarafından RAM'in Salt-Okunur (.rodata) bir sayfasına, örneğin tam olarak `0x00402000` sanal bellek adresine kopyalanır. Fiziksel RAM üzerindeki bu transistörler, sadece okunabilir (Read-Only) elektrik yüklerine sahip olur.
**CPU Yazmaçları ve Sistem Çağrısı (Syscall):** CPU, bu kodu yürütürken Ring 3 (User Modu) yetkilerindedir. Metnin uzunluğunu ve RAM adresini sırasıyla CPU'nun `RDX` ve `RSI` yazmaçlarına (Registers) doldurur. Ardından EAX yazmacına yazma emrinin numarasını koyarak `syscall` (veya `int 0x80`) kesmesini (Interrupt) ateşler ve işlemci kontrolü Kernel'a (Ring 0) teslim eder.
**Kernel ve MMU (Bellek Yönetim Birimi) Entegrasyonu:** İşletim sisteminin çekirdeği (Kernel), `0x00402000` adresinden veriyi okumak için CPU içindeki MMU'ya emir verir. MMU, TLB (Translation Lookaside Buffer) donanımını kullanarak bu sanal adresi fiziksel RAM adresine (örneğin `0x1A205000`) çevirir ve baytları okumaya başlar.
**Anakart Veri Yolları ve GPU İletimi:** Okunan bu karakter baytları (örneğin 'M' harfi için `0x4D`), anakart üzerindeki PCIe (Peripheral Component Interconnect Express) veri yolu üzerinden inanılmaz bir hızla Ekran Kartının (GPU) Framebuffer (Görüntü Tamponu) belleğine (`0xD0000000` gibi bir adrese) taşınır. GPU bu baytları voltaj sinyallerine çevirip monitörünüzdeki pikselleri aydınlatır.

---

## BÖLÜM 2: Bellek Yönetimi ve Veri Kilitleme (Variables)

```mrr
let hedef_ip = "192.168.1.50"
mut tarama_yuzdesi = 0
```

### 💻 Yazılımsal Analiz (Software Architecture)
**Değişmezlik (Immutability) Felsefesi:** `let` kelimesi ile oluşturulan `hedef_ip` değişkeni yazılımsal olarak "Sabit" (Constant/Immutable) kabul edilir. Bir yazılımcı bu satırı yazdıktan sonra programın hiçbir yerinde bu değeri değiştiremez. Bu, özellikle büyük yazılımlarda bir başka geliştiricinin yanlışlıkla kritik bir veriyi değiştirmesini önlemek için tasarlanmış yazılımsal bir tasarım desenidir.
**Değişkenlik (Mutability) İhtiyacı:** Eğer bir değer sürekli güncellenecekse (örneğin bir döngü sayacı veya indirme yüzdesi), geliştirici bilinçli bir kararla `mut` kelimesini kullanarak `tarama_yuzdesi` değişkenini tanımlar. Bu, koda bakan birinin "Bu değer zamanla değişecek, buna dikkat et" demesini sağlayan görsel ve anlamsal bir işarettir.
**Tip Çıkarımı (Type Inference):** Yazılımcı `str` (metin) veya `i32` (sayı) yazmasa da, MRR'ın yazılımsal motoru sağ taraftaki veriye bakarak "Bu bir metin" veya "Bu bir tam sayı" çıkarımını yapar. AST ağacında bu değişkenlere güçlü tipler atanır, böylece sayı beklenen yere metin gönderilmesi derleme aşamasında yazılımsal olarak engellenir.
**Yazılımsal Kapsam (Scope) Kontrolü:** Bu değişkenler, tanımlandıkları bloğun (süslü parantez veya girinti) dışına çıkamazlar. Yazılımsal Çöp Toplayıcı (Garbage Collector) veya Referans Sayıcı (Reference Counter), bu değişkenlerin kapsamı bittiği anda onları yazılımsal olarak silinecekler listesine ekler.

### ⚙️ Donanımsal Analiz (Hardware & Physical Layer)
**MMU Donanımsal Kilit Mekanizması:** `let` komutu kullanıldığında, işletim sistemi MMU (Bellek Yönetim Birimi) üzerinden bu RAM sayfasını donanımsal olarak sadece okunabilir (`PAGE_READONLY`) olarak kilitler. Kötü niyetli bir kod bu adrese veri yazmaya çalışırsa, MMU bir `Page Fault` (Sayfa Hatası) fırlatarak transistör seviyesinde yazma işlemini durdurur.
**CPU Cache ve Yazma (Write) İzni:** `mut` ile oluşturduğumuz `tarama_yuzdesi` ise `PAGE_READWRITE` izniyle RAM'de yer alır. İşlemci bu değişkeni L1 SRAM önbelleğine (Cache) alır. Değer `0`'dan `1`'e değiştiğinde, CPU'nun Cache kontrolcüsü bu değişikliği anında algılar ve doğru anı bekleyerek (Write-Back stratejisiyle) RAM'e yeni voltajı uygular.
**Yazmaç (Register) Seçimi ve ALU İşlemleri:** `tarama_yuzdesi` isimli sayısal değişken, CPU'nun GPR (Genel Amaçlı Yazmaçlar - örneğin `EAX` veya `RCX`) içine yerleştirilir. Buna eklenecek her `+1` işlemi, ALU (Aritmetik Mantık Birimi) içindeki donanımsal Toplayıcı (Adder) devrelerinde elektrik akımı olarak hesaplanır.
**Bellek Veriyolu (Memory Bus) Trafiği:** `hedef_ip` gibi metinsel ifadeler CPU yazmaçlarına sığmaz (RAM'de ardışık bloklar kaplar). İşlemci bu veriye ihtiyaç duyduğunda, Bellek Kontrolcüsüne (Memory Controller) sinyal gönderir; veriler FSB (Front Side Bus) veya modern QPI/Infinity Fabric yolları üzerinden CPU'ya aktarılır.

---

## BÖLÜM 3: Kontrol Akışı ve İşlemci Yönlendirme (Control Flow)

```mrr
let sunucu_yaniti = 404

if sunucu_yaniti == 200:
    println("Bağlantı başarılı")
elif sunucu_yaniti == 404:
    println("Hedef bulunamadı.")
```

### 💻 Yazılımsal Analiz (Software Architecture)
**Mantıksal Sınama Felsefesi:** `if` ve `elif` blokları, yazılımın karar verme yeteneğidir. Yazılımcı, programın her durumu kapsamasını sağlamak için "Eğer böyleyse bunu yap, yoksa şunu yap" mantığıyla bir senaryo ağacı (Decision Tree) çizer. Yazılım, bu ağaçtaki doğru yolu bularak akışına devam eder.
**Dallanma Kapsamı ve İzolasyon:** Her bir if bloğunun içi, kendine has bir Scope (kapsam) yaratır. Bu blokların içine yazılan yeni değişkenler, diğer bloklara sızmaz. Yazılımsal olarak bu izolasyon, hatalı durumların (örneğin sadece 404 durumunda oluşması gereken bir hatanın 200 durumunda görünmesi) önüne geçer.
**Opcode Optimizasyonu:** Derleyici (MRR Engine), bu if-elif yapısını gördüğünde, bunları yazılımsal "Jump" (Sıçrama) etiketlerine (Labels) çevirir. Kodun çalışabilir bayt kodu (Bytecode), sırayla if şartlarını değerlendirecek ve şart sağlandığında diğer tüm blokları yazılımsal olarak atlayacak şekilde dizayn edilir.
**Kodun Okunabilirliği ve Bakımı:** MRR'da süslü parantez kullanılmaması ve Python gibi girintilere (indentation) dayalı olması, yazılım ekiplerinin (geliştirici, tester) kodu gözle okumasını (Code Review) hızlandırır. Karmaşık ve iç içe geçmiş mantık hataları daha hızlı tespit edilir.

### ⚙️ Donanımsal Analiz (Hardware & Physical Layer)
**CMP (Compare) Donanım Komutu:** `sunucu_yaniti == 200` satırı, doğrudan CPU'ya bir `CMP` (Karşılaştırma) Assembly komutu olarak gider. İşlemcinin ALU'su, kendi yazmacındaki (EAX) değeri alıp, donanımsal olarak 200 (`0xC8`) sayısı ile çıkarır. Eğer sonuç sıfırsa, işlemcinin `Zero Flag` (Sıfır Bayrağı) adı verilen küçük bir transistörü "1" (Açık) konumuna geçer.
**JMP (Jump) ve Program Sayacı (Program Counter):** Eğer Zero Flag "1" olursa, işlemcinin EIP/RIP (Program Sayacı) yazmacı, o kod bloğunun fiziksel bellek adresine (örneğin `0x004010A2`) sıçrar (`JE` - Jump if Equal). Eğer eşit değilse, Program Sayacı mevcut adresi okumaya devam ederek `elif` kontrolüne gider.
**Branch Prediction (Dallanma Tahmini):** İşlemci, program çalışırken zaman kaybetmemek için bir "kahin" gibi davranır. İşlemcinin Branch Predictor (Dallanma Tahmincisi) donanımı, geçmiş tecrübelerine dayanarak sunucu yanıtının 200 mü 404 mü olacağını önden tahmin edip kodu işler. 
**Pipeline Flush (Boru Hattı Yıkımı):** Eğer işlemcinin tahmini yanlış çıkarsa (Örneğin 200 beklerken 404 gelmesi), işlemci boru hattına (Pipeline) önden yüklediği tüm komutları "donanımsal olarak" iptal eder (Flush). Bu durum CPU için büyük bir efordur ve yaklaşık 15-20 saat vuruşu (clock cycle) yani zaman kaybı demektir; MRR derleyicisi bu tahmini kolaylaştıracak şekilde donanım odaklı Assembly üretir.

---

## BÖLÜM 4: Yapılar (Structs) ve Uzamsal Bellek Modelleme

```mrr
struct AgPaketi:
    pub ttl: i32         
    priv payload: bytes  

let paket = AgPaketi(ttl: 64, payload: b"X")
```

### 💻 Yazılımsal Analiz (Software Architecture)
**Nesne Modelleme Yaklaşımı:** Yazılım dünyasında her şey rakam veya metin olamaz. Gerçek dünyadaki nesneleri veya bir siber güvenlik saldırısındaki ağ paketini modellemek için `struct` (Yapı) kullanılır. Geliştirici, kendi ihtiyacına göre "AgPaketi" adında özel bir yazılımsal veri kalıbı inşa eder.
**Kapsülleme (Encapsulation) İlkesi:** Yazılım mühendisliğinin en önemli kuralı yetkileri sınırlandırmaktır. `pub` anahtar kelimesi ile "ttl" alanı diğer dosyalardaki yazılımcılara açık bırakılırken, `priv` ile "payload" alanı dış dünyadan yazılımsal olarak kilitlenir. Modülün iç çalışmasına dışarıdan müdahale edilemez.
**Tip Güvenliği ve Sözleşme:** Bu struct oluşturulduğunda, derleyici için yeni bir "Sözleşme" devreye girer. Bundan sonra, `AgPaketi` bekleyen bir fonksiyona sadece bu kalıba uygun bir nesne gönderilebilir. İçinde `ttl` yerine başka bir alan olan nesne yazılımsal olarak reddedilir.
**Değer vs Referans Transferi:** Yazılım seviyesinde, bir fonksiyon bu struct'ı parametre olarak aldığında, arka planda bu verinin tamamı kopyalanacak mı (Call by Value) yoksa sadece adresi mi iletilecek (Call by Reference) kararı derleyicinin RAM optimizasyon kurallarına göre belirlenir.

### ⚙️ Donanımsal Analiz (Hardware & Physical Layer)
**Fiziksel Bellek Dizilimi (Memory Layout):** Bir `struct` bellekte rastgele değil, mükemmel bir blok halinde dizilir. RAM'in `0x0A005000` adresinde paket objesi oluşturulduysa, CPU tam o noktadan başlayarak ilk 4 bayta `ttl` değerini (64 -> `0x00000040`), hemen yanındaki adrese ise `payload` verisini kopyalar.
**Hizalama (Memory Alignment) Kuralları:** İşlemciler, bellek adreslerini 4 veya 8'in katları şeklinde okumayı sever. MRR, arka planda bu `ttl` (4 byte) ile `payload` (dinamik 8 byte pointer) arasına, işlemci veri yolu tek seferde pürüzsüz okusun diye donanımsal olarak "boş baytlar" (Padding) yerleştirebilir.
**Önbellek Yakınlığı (Spatial Locality):** Bu yapı tamamen tek bir RAM bloğunda olduğu için, CPU `ttl` değerini okumak için RAM'e başvurduğunda, CPU'nun Prefetcher donanımı "nasıl olsa hemen yanındaki veriye de ihtiyaç olur" diyerek `payload` bilgisini de aynı anda (tek bir Cache Line içinde) L1 Önbelleğine çeker.
**İşaretçi (Pointer) Dereferencing İşlemi:** `paket.ttl` yazıldığında, CPU arka planda paket objesinin kök adresi (`0x0A005000`) ile `ttl` elemanının göreceli mesafesini (Offset - örneğin +0 byte) donanımsal toplayıcısında (ALU) toplar. Doğrudan hedef belleğe (RAM'e) bir adresleme isteği göndererek fiziksel voltajı çeker.

---

## BÖLÜM 5: Çekirdek İstismarı ve Zafiyet İzolasyonu (Exploits)

```mrr
exploit "Memory Extraction":
    let raw_socket_id = portswinger_socket_create(2, 3, 6)
```

### 💻 Yazılımsal Analiz (Software Architecture)
**Kum Havuzu (Sandbox) Mantığı:** Bir yazılımcı (veya siber güvenlikçi), işletim sisteminin koruma sınırlarını zorlayan riskli işlemler yapmak istediğinde bu kodları `exploit` bloğu içine alır. Yazılımsal olarak bu blok, içindeki herhangi bir çökmenin, dışarıdaki ana yazılımı veya sunucuyu çökertmesini (Crash) önleyen izole bir kapsüldür.
**Standartları Yıkma Özgürlüğü:** Normal yazılım standartlarında bir paket oluşturmak için onlarca katmandan (OSI modeli) geçmeniz gerekir. Bu yazılımsal `portswinger` kütüphanesi ise, tüm bu yüksek seviyeli protokolleri reddeder ve size "kendi başlığını kendin yaz" yetkisi vererek protokol tasarımcısı rolüne bürünmenizi sağlar.
**İstisna (Exception) Yönetim Alanı:** `exploit` blokları, yazılımsal olarak kendi içlerinde çok sıkı bir hata yakalama (Implicit Try-Catch) süzgecine sahiptir. İşletim sistemi bu isteği reddederse, program paniklemek yerine `null` veya özel bir hata nesnesi döndürerek yazılımsal bütünlüğü korur.
**Kütüphane (DLL/SO) Soyutlaması:** `portswinger_socket_create` aslında MRR'ın kendi çekirdeğinde yoktur. Dışarıdan dahil edilen C++ tabanlı bir kütüphanedir. Yazılımsal FFI (Foreign Function Interface) teknolojisi, MRR dilinin metinsel veri tiplerini arka planda C++'ın beklediği ham C tiplerine (pointers) çeviren kusursuz bir çevirmendir.

### ⚙️ Donanımsal Analiz (Hardware & Physical Layer)
**NIC (Ağ Kartı) Doğrudan Erişimi:** 3 numaralı "Raw Socket" tipi oluşturulduğunda, donanımsal olarak şu gerçekleşir: İşletim sisteminin Kernel Ağ Yığını (Network Stack) by-pass edilir. Yazdığınız `bytes` dizilimleri, doğrudan anakartın PCIe hattından Ethernet kartının (NIC) donanımsal kontrolcüsüne (MAC Controller) fiziksel elektrik sinyalleri olarak gönderilir.
**DMA (Direct Memory Access) Hızlandırması:** Paketler yollanırken CPU her baytı kendi üzerinden geçirmek zorunda kalmaz. Ağ kartı, DMA denilen özel donanımsal bir özellik ile direkt olarak RAM'in belli bölgesine (Buffer) erişir ve paketleri ana işlemcinin (CPU) mesaisini harcamadan şebekeye basar.
**Ring 0 Yetkilendirme Engeli:** Bu kodu çalıştıran CPU, eğer Ring 3 (User Modu) yetkisindeyse ve siz Root/Yönetici değilseniz, Kernel bu soket oluşturma sistem çağrısına (Syscall) cevap olarak EAX yazmacına `-1` veya `EPERM` (Erişim Reddedildi) hata kodunu basar. Bu tamamen işlemcinin yetki donanımıyla yönetilir.
**Ağ Kablosunda Voltaj Dönüşümü:** Oluşturduğunuz bu özel TCP paketi, Ağ kartınızdaki PHY (Physical Layer) donanımından geçer. Burada paketlerinizin `1` ve `0`'ları, CAT6 kablonuzdaki bakır teller üzerinden +2.5V veya -2.5V elektrik darbelerine dönüştürülür ve ışık hızına yakın bir süratle hedef sunucunun anakartına doğru fiziksel yolculuğuna başlar.

---

## BÖLÜM 6: Asenkron Web Fuzzer (Gerçek Hayat Örneği)

```mrr
add.code "portswinger"
import std::network

async fn fuzz_hedef(hedef_ip: str, yol: str):
    let yanit = network::http_get("http://" + hedef_ip + yol)
    if yanit["status"] == 200:
        println("[+] BULUNDU: " + yol)

async fn tarama_baslat():
    let payload_listesi = ["/admin", "/.git", "/backup.zip"]
    for yol in payload_listesi:
        fuzz_hedef("10.0.0.5", yol) // await kullanmadan ateşle ve devam et!
```

### 💻 Yazılımsal Analiz (Software Architecture)
**Asenkron Tetikleme Felsefesi:** Geliştirici `await` anahtar kelimesini bilerek kullanmamıştır. Bu durum, "Ben fonksiyona komutu verdim, sonucunu beklemeden döngüdeki diğer hedeflere geçmek istiyorum" anlamına gelir (Fire and Forget). Yazılımsal olarak bu, binlerce dizinin (directory) saniyeler içinde taranabilmesini sağlayan bir fuzzer mantığıdır.
**Ağ Kütüphanesi İzolasyonu:** `import std::network` ile dilin çekirdek motoru şişirilmemiş olur. HTTP istekleri, soket açma kapama ve header (başlık) analiz işlemleri sadece bu modül çağırıldığında derleyiciye yüklenir. Geliştirici TCP detaylarıyla değil, sadece `status` (200, 404) kodlarıyla yazılımsal olarak muhatap olur.
**Koleksiyon Üzerinde Döngü (Iterator):** `payload_listesi` içindeki metinler, geleneksel C stili (i=0; i<3) döngü yerine modern ve güvenli bir "Iterator" (Gezgin) ile taranır. Bu yaklaşım, listenin sınırlarını (Out of Bounds) aşma riskini yazılımsal olarak tamamen sıfıra indirir.
**Yazılımsal Yanıt İşleme:** `yanit["status"]` ifadesi, dönen ağ verisinin MRR tarafından anında bir Sözlük (Dictionary) veri yapısına çevrildiğini (JSON veya HTTP Header ayrıştırma) gösterir. Geliştirici ham string verisi ayıklamak yerine, yapılandırılmış verilere (Structured Data) anahtarlar aracılığıyla erişir.

### ⚙️ Donanımsal Analiz (Hardware & Physical Layer)
**I/O Kesintileri (Hardware Interrupts):** CPU, ağ isteğini başlattığında, hedef sunucunun cevap vermesini beklemek (Idle/Boşta beklemek) yerine işlemi I/O kontrolcüsüne devreder. Anakartın güney köprüsü (Southbridge) veriyi aldığında, CPU'ya fiziksel bir donanım kesmesi (Hardware Interrupt - IRQ) göndererek "Veri geldi, işlemeye başla" mesajı iletir.
**Thread ve Context Switch:** İşlemci, bir `async` fonksiyondan diğerine atlarken Bağlam Değişimi (Context Switch) yaşar. O anki yazmaçların (EAX, RSP vb.) durumu RAM'de saklanır (Save State) ve yeni görevin yazmaç değerleri CPU'ya çekilir. MRR'ın hafif iş parçacıkları (Green Threads), bu donanımsal geçiş maliyetini nanosaniyelere düşürür.
**Soket Dosya Tanımlayıcıları (File Descriptors):** İşletim sisteminin Kernel tablosunda, açık olan her HTTP bağlantısı için donanımsal bir "File Descriptor" tahsis edilir. Çok fazla asenkron işlem aynı anda başlatılırsa, Kernel'ın bu dosya tanımlayıcı sınırına (örneğin ulimit limiti olan 1024) takılınır ve Kernel yeni soket açma işlemlerini donanımsal/sistemsel seviyede reddeder.
**TCP/IP Buffer Yönetimi:** Hedef sunucudan dönen veri, RAM'in Kernel bölgesindeki özel Socket Buffer alanlarına (Örn: `sk_buff` yapısı) donanımsal olarak yazılır. MRR, bu veriyi okumak için CPU'nun `sys_recv` komutunu kullanarak, Kernel RAM alanındaki baytları User RAM alanına (Kullanıcı bellek sayfasına) kopyalar.

---

## BÖLÜM 7: Dış Bellek Analizi - Memory Scanner (Oyun Hilesi/Zafiyet Testi)

```mrr
add.code "memory_reader"

exploit "Hedef Uygulama Belleğine Sızma":
    memory_attach("calc.exe")
    let can_adresi = 0x1400B820
    let okunan_deger = memory_read_i32(can_adresi)
    println("Bellekten okunan veri: #{okunan_deger}")
```

### 💻 Yazılımsal Analiz (Software Architecture)
**Dışsal Bellek (Out-of-Process) Okuma:** Normalde bir yazılım, sadece kendi değişkenlerini ve kendi tanımladığı verileri görebilir. Ancak bu MRR kodu, yazılımsal sınırları yıkarak "calc.exe" adlı başka bir uygulamanın belleğine sızar. Tersine mühendislik araçları (Cheat Engine gibi) tam olarak bu yazılımsal mimariyi kullanır.
**Fonksiyonel Modülerlik:** `memory_attach` fonksiyonu, süreç adı (Process Name) girilmesine izin vererek yazılımcıyı PID (Process ID) arama zahmetinden kurtarır. Yazılım motoru arka planda işletim sisteminin tüm çalışan uygulama listesini tarar, eşleşen adı bulur ve bağlantıyı (Handle) oluşturur.
**Tip Dayatmalı Okuma:** `memory_read_i32` fonksiyonunun sonundaki "i32" takısı, o bellek adresindeki byteların yazılımsal olarak nasıl yorumlanacağını MRR motoruna dikte eder. Ham 4 byte alınacak ve yazılımcıya standart bir 32-bit Tam Sayı olarak geri verilecektir. 
**Tehlikeli İzole Tasarım:** `exploit` bloğu, hedef program (calc.exe) kapatılırsa veya adres geçerliliğini yitirirse oluşacak yazılımsal panik (Panic/Crash) durumunu sönümler. Hedef okuma işlemi başarısız olsa bile yazılımımız hata fırlatıp kapanmaz, sadece bu bloğu atlayarak güvende kalır.

### ⚙️ Donanımsal Analiz (Hardware & Physical Layer)
**İşletim Sistemi API ve Ring 0 Talebi:** `memory_attach` komutu, Windows'ta `OpenProcess`, Linux'ta ise `ptrace` sistem çağrısını tetikler. İşlemci, Ring 0 moduna geçer ve Kernel'dan "Ben calc.exe'nin RAM sayfalarına erişmek istiyorum" diye donanımsal bir Handle (Belge) ister.
**VAD (Virtual Address Descriptor) Aşırması:** `0x1400B820` adresi, sizin programınıza ait bir RAM adresi değildir. Bu, "calc.exe"nin Sanal Bellek Haritasında (Virtual Memory Map) yer alır. MMU (Bellek Yönetim Birimi), sizin programınızın `ReadProcessMemory` talebini aldığında, calc.exe'nin sayfa tablolarını (Page Tables) okur ve fiziksel RAM'deki o transistör kümesini tespit eder.
**Fiziksel RAM (DRAM) Okuma Voltajı:** Tespit edilen fiziksel adresteki (Örn: Row 4, Column 12) kapasitörler şarjlıysa '1', deşarj olmuşsa '0' olarak algılanır. Bellek Kontrolcüsü bu 4 baytlık (32 bit) elektrik yükünü, anakartın FSB'si üzerinden CPU'nun EAX yazmacına taşır.
**Anti-Cheat ve Donanım Koruması:** Eğer calc.exe gelişmiş bir oyun korumasıyla (Anti-Cheat) çalışıyorsa, Kernel düzeyinde (Ring 0) donanım saat kesmelerini (Timer Interrupts) veya Özel Kayıtları (Debug Registers - DR0, DR1) manipüle etmiş olabilir. Bu durumda MMU bu adresi okumanızı reddeder ve CPU bir Exception (İstisna) sinyali üreterek okuma işlemini fiziksel olarak durdurur.

---

## BÖLÜM 8: MRR Kütüphanesi (Library) Detaylı Referansı

MRR dili, sisteminizdeki `library` dizininde bulunan, donanım seviyesinde çalışan modüllerden güç alır. Aşağıda bu çekirdek modüllerin detaylı açıklamaları ve kod örnekleri yer almaktadır.

# crypto
**Açıklama (Yazılımsal ve Donanımsal Derinlik):** 
Bu modül sıradan bir yazılımsal hesaplama yapmaz; gücünü doğrudan CPU'nun içindeki donanımsal AES-NI (Advanced Encryption Standard New Instructions) komut setinden alır. Yazılımınız `crypto_aes_encrypt` çağırdığında, algoritma Ring 0 (Kernel) ve ALU arasındaki en kısa yoldan donanımsal mantık kapılarına iner. Kötü amaçlı bir bellek okumasına (Side-Channel Attack veya Cache Timing Attack) karşı bağışıklıdır; çünkü işlem süresi CPU donanımında sabit (Constant-Time) bir döngüde gerçekleşir. SHA-256 ve MD5 algoritmaları, Zararlı Yazılım (Malware) imzası çıkarmada veya ağ paketlerinin bütünlüğünü (Integrity) teyit etmede SIMD (Single Instruction, Multiple Data) mimarisi ile paralel vektör hesaplamalarından geçer. Parolalar asla RAM'de çıplak (Clear-text) beklemez, anında bit düzeyinde entropi havuzuna karışarak şifrelenir.
**Örnek Kullanım:**
```mrr
add.code "crypto"

// 1. Veri Bütünlüğü için Donanım Destekli SHA256 Hashing
let hash_degeri = crypto_sha256(b"kutuphane_dosyasi.dll")
println("Dosya İmzası: " + hash_degeri)

// 2. Zararlı Yazılım İletişimi (C2 Server) için AES-256 Şifreleme
let gizli_anahtar = b"0xDEADC0DE0xDEADC0DE0xDEADC0DE00" 
let sifreli_veri = crypto_aes_encrypt(b"Sisteme Sizildi", gizli_anahtar)
println("Ağda Gezecek Şifreli Paket: " + sifreli_veri)
```

# datetime
**Açıklama:** Anakart üzerindeki RTC (Real-Time Clock) yongasından (CMOS) zaman bilgisini okuyan ve bu veriyi kullanılabilir zaman/tarih formatlarına biçimlendiren modüldür.
**Örnek Kullanım:**
```mrr
add.code "datetime"
let anlik_zaman = datetime_now()
println("Sistem Saati: " + anlik_zaman)
```

# hex
**Açıklama (Yazılımsal ve Donanımsal Derinlik):** 
Siber güvenlik dünyasında her şey baytlardan ibarettir. Bellekten okunan çiğ (Raw) baytların, insan gözünün algılayabileceği `00` ile `FF` aralığındaki Hex (16'lık) sistem formuna dönüştürülmesi ciddi CPU eforu gerektirir. `hex` kütüphanesi, C++ tabanlı bir "Lookup Table" (Arama Tablosu) kullanarak bu dönüşümü L1 Ön Bellek (Cache) hızında yapar. Bir Malware bellek dökümünü (Memory Dump) veya ele geçirilmiş bir ağ paketini analiz ederken, Endianness (Little-Endian / Big-Endian) sorunlarına otomatik çözüm getirir. Bellek (RAM) hücrelerindeki transistörlerin `1` ve `0` durumlarını bit kaydırma (Bitwise Shift) işlemleri ile gruplayarak ekrana adeta Matrix'in kaynak kodunu basar.
**Örnek Kullanım:**
```mrr
add.code "hex"

// İşletim sistemi belleğinden çalınmış ham 4 byte
let calinan_bellek = b"\x4D\x5A\x90\x00" // Windows PE (EXE) Başlığı

// Ham baytları Hexadecimal'e çevir (Endian dönüşümü yapılarak)
let hex_dizisi = hex_encode(calinan_bellek)
println("Bellek Dökümü Analizi: 0x" + hex_dizisi) // Çıktı: 0x4D5A9000
```

# json
**Açıklama:** RESTful API'ler ve ayar dosyalarıyla haberleşmek için kullanılan, JSON formatındaki metinleri MRR Sözlüklerine (Dictionary) çeviren çok hızlı bir ayrıştırıcıdır (Parser).
**Örnek Kullanım:**
```mrr
add.code "json"
let ayar = json_parse("{\"port\": 8080}")
println("Hedef Port: " + string(ayar["port"]))
```

# maths
**Açıklama:** İşlemcinin doğrudan FPU (Floating Point Unit - Kayan Nokta Birimi) transistörlerini tetikleyen, trigonometri ve logaritma gibi ileri düzey matematik hesaplamalarını içeren C tabanlı kütüphanedir.
**Örnek Kullanım:**
```mrr
add.code "maths"
let sonuc = math_sqrt(144)
println("Karekök: " + string(sonuc))
```

# memory_reader
**Açıklama:** İşletim sisteminin Ring 0 (Kernel) izinlerini kullanarak, sistemde çalışan başka bir uygulamanın (Örn: oyunlar, zararlı yazılımlar) RAM sayfalarına dışarıdan okuma ve yazma erişimi sağlayan sömürü (Exploit) modülüdür.
**Örnek Kullanım:**
```mrr
add.code "memory_reader"
memory_attach("notepad.exe")
let okunan = memory_read_i32(0x1400B820)
```

# network
**Açıklama (Yazılımsal ve Donanımsal Derinlik):** 
MRR dilinin en tehlikeli alt katmanlarından biridir. POSIX uyumlu (Berkeley Sockets) mimarisinde, doğrudan işletim sisteminin Çekirdeğine (Kernel) inerek Ring 0'da donanımsal File Descriptor (Dosya Tanımlayıcı) talep eder. Ağ Kartı (NIC) üzerindeki PHY ve MAC denetleyicilerini uyandırarak, işletim sisteminin TCP yığını (TCP/IP Stack) üzerinden SYN, SYN-ACK, ACK süreçlerini (Three-way Handshake) donanım tabanlı yürütür. Ağ yığılmalarını (Congestion) engellemek için DMA (Direct Memory Access) çember tamponlarına (Ring Buffers) okuma ve yazma yapar. CPU yükünü azaltmak amacıyla ağ paketleri, işlemci yerine doğrudan ağ kartı tarafından RAM'e yazılır (Zero-copy Networking). İster Botnet sunucusu, ister bir sızma testi (Penetration Test) modülü yazın, en çıplak soket erişiminiz bu kütüphanedir.
**Örnek Kullanım:**
```mrr
add.code "network"

// C2 (Command & Control) Sunucusu için Port Dinleme (Bind & Listen)
let sunucu_soket = network_listen("0.0.0.0", 4444)
println("Port 4444'te kurbanlar bekleniyor...")

// İstemci geldiğinde TCP Bağlantısını Kabul Et (Accept) ve Kernel Buffer'dan veri oku
let kurban_soket = network_accept(sunucu_soket)
let gelen_veri = network_recv(kurban_soket, 1024)
println("Kurbandan Gelen Paket: " + gelen_veri)
```

# os
**Açıklama:** Doğrudan işletim sistemine (Windows API / Linux Syscalls) dosya oluşturma, klasör silme veya süreç (Process) yetkilerini yönetme gibi Ring 0 emirleri yollayan çekirdek modülüdür.
**Örnek Kullanım:**
```mrr
add.code "os"
os_mkdir("/var/log/mrr_logs")
println("Klasör oluşturuldu.")
```

# portswinger
**Açıklama:** İşletim sisteminin TCP yığınını (Stack) atlayarak (bypass) doğrudan Ethernet Kartına (NIC) kendi özel TCP başlıklarınızı (Headers) enjekte etmenizi sağlayan saldırı, sahtecilik (Spoofing) ve analiz kütüphanesi.
**Örnek Kullanım:**
```mrr
add.code "portswinger"
// 3 numaralı tip "Raw Socket" oluşturur
let fd = portswinger_socket_create(2, 3, 6)
```

# portswinger_raw
**Açıklama:** `portswinger` kütüphanesinin çok daha donanımsal, tamamen Layer 2 (Data Link) seviyesinde çalışan ve MAC adresleri düzeyinde sızma testleri yapan gelişmiş C++ modülüdür.
**Örnek Kullanım:**
```mrr
add.code "portswinger_raw"
let raw_arayuz = raw_bind_interface("eth0")
```

# random
**Açıklama:** Anakartın entropi havuzunu (Entropy Pool) veya modern işlemcilerdeki `RDRAND` donanımsal rastgele sayı üretecini kullanarak, tahmin edilemez kriptografik sayılar üreten güvenlik modülüdür.
**Örnek Kullanım:**
```mrr
add.code "random"
let guvenli_sayi = random_crypto_int()
println("Tek kullanımlık şifre (OTP): " + string(guvenli_sayi))
```

# requests
**Açıklama (Yazılımsal ve Donanımsal Derinlik):** 
Uygulama Katmanı'nda (Layer 7) asenkron devrimi başlatan devasa bir motordur. Binlerce HTTP ve HTTPS isteğini arka planda Linux'ta `epoll`, Windows'ta `IOCP` (I/O Completion Ports) donanım mekanizmalarıyla eşzamanlı olarak hedefe fırlatır. CPU'nun Context Switch (Bağlam Değiştirme) maliyetini sıfıra indirmek için asenkron (Non-blocking) soket modunda çalışır. Hedef sunuculara yapılan SSL/TLS şifreli bağlantılarda (HTTPS), OpenSSL köprüleriyle TLS 1.3 Handshake sürecini donanım şifreleme desteğiyle mili-saniyeler içinde tamamlar. Özellikle Web Fuzzer, Dizin Tarama (Directory Brute-Forcing) veya SQL Injection test otomasyonları yazılırken saniyede on binlerce paketi hedefe gönderip CPU'nun "Idle" (boşta bekleme) süresini yok eder.
**Örnek Kullanım:**
```mrr
add.code "requests"

// Kapsamlı bir HTTP POST isteği inşası (Kimlik Bilgisi Sızdırma / Brute Force)
let basliklar = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
let payload = "{\"kullanici\":\"admin\", \"sifre\":\"' OR '1'='1\"}"

let yanit = requests_post("https://hedef-sunucu.com/api/login", 
                          headers: basliklar, 
                          body: payload)
                          
println("Saldırı Sonucu Durum Kodu: " + string(yanit.status))
```

# response
**Açıklama (Yazılımsal ve Donanımsal Derinlik):** 
`requests` kütüphanesinin yakaladığı okyanus büyüklüğündeki ağ paketlerini parçalayan State-Machine (Durum Makinesi) ayrıştırıcısıdır. RAM'e akan devasa bir HTTP yanıtı geldiğinde, veriyi tek tek parçalara bölerek RAM'de israfa yol açmaz; bunun yerine Sıfır-Kopya (Zero-Copy) bellek haritalaması kullanarak işaretçilerle (Pointers) okuma yapar. "Chunked Transfer Encoding" gibi karmaşık sunucu yanıtlarını CPU'nun ALU (Aritmetik Mantık Birimi) üzerinden akıcı bir şekilde birleştirir (Defragmentation). Geliştirici sadece `response_get_body()` yazdığında, arka planda Kernel seviyesinde soket tamponları (Socket Buffers) sıyrılır, HTTP üstbilgileri (Headers) tıraşlanır ve sadece amaca yönelik ham zafiyet/veri ekranına düşer.
**Örnek Kullanım:**
```mrr
add.code "response"

// Yanıt objesinden gelişmiş analiz
let sunucu_sistemi = response_get_header("Server")
let set_cookie = response_get_header("Set-Cookie")

// Sunucunun kullandığı teknolojiyi ve çerezleri çalma
println("Hedefin Web Sunucusu: " + sunucu_sistemi)
if string_contains(set_cookie, "session_id"):
    println("[!] Kritik Oturum Çerezi Yakalandı: " + set_cookie)
```

# sys
**Açıklama:** Donanımsal mimariye en yakın olan araçtır. RAM doluluk durumunu, CPU çekirdek sayısını, donanım kimliklerini ve işletim sistemi ortam değişkenlerini (Environment Variables) okuyan Kernel modülüdür.
**Örnek Kullanım:**
```mrr
add.code "sys"
println("Sistemdeki CPU Çekirdeği: " + string(sys_cpu_cores()))
```

# xor
**Açıklama (Yazılımsal ve Donanımsal Derinlik):** 
Antivirüsleri ve EDR (Endpoint Detection and Response) sistemlerini kör etmek (Obfuscation) için kullanılan, donanımın en saf ve en ölümcül mantıksal kapısıdır. XOR (Exclusive OR) komutu, CPU'nun içindeki transistörlerde sadece bir saat vuruşunda (1 Clock Cycle) hesaplanır. Modern MRR motoru, büyük bir zararlı yazılım payload'ını (örn. 50 MB) gizlerken, işlemcinin AVX/SSE (Gelişmiş Vektör Uzantıları) donanım setini tetikleyerek 256-bit veya 512-bit veriyi tek seferde şifreler. Bellekteki (RAM) imza tabanlı (Signature-based) taramaları atlatmak için, statik olan bayt dizilimi çalışma anında (Runtime) maskelenir ve ancak işlemci register'larında (Yazmaçlar) gerçek formuna dönüşüp çalıştırılır. Bu Polymorphic (Çok Biçimli) tasarım, tersine mühendisleri saatlerce uğraştırır.
**Örnek Kullanım:**
```mrr
add.code "xor"

// 1. Antivirüslerden Gizlenmiş (Obfuscated) Shellcode
let zararli_payload = b"\x31\xC0\x50\x68\x2F\x2F\x73\x68\x68\x2F\x62\x69\x6E\x89\xE3"
let gizli_anahtar = 0xAA

// 2. RAM Üzerinde Donanım Hızlandırmalı XOR Şifreleme (Bulaşma Öncesi)
let maskeli_shellcode = xor_bytes(zararli_payload, gizli_anahtar)
println("Antivirüs Kör Edildi. Şifreli Payload: " + hex_encode(maskeli_shellcode))

// 3. Çalışma Anında (Runtime) RAM'de Çözme ve Tetikleme
let orjinal_payload = xor_bytes(maskeli_shellcode, gizli_anahtar)
```

---

<div align="center">

**MRR Programlama Dili: Teoriden Pratiğe İmkansızları Gerçeğe Çeviren Güç .MRR**  
*Gücü kontrol et, işlemcinin sınırlarını baştan yaz.*

</div>
