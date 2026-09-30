import {
  AlertTriangle,
  ChevronLeft,
  Cookie,
  Database,
  Gavel,
  Mail,
  Scale,
  Send,
  ShieldCheck,
  UserCheck,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const SUPPORT_EMAIL = 'kesfetplusdestek@gmail.com'

function Section({ icon: Icon, title, children }) {
  return (
    <div className="mt-6 px-5">
      <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
        <Icon size={14} />
        {title}
      </p>
      <div className="overflow-hidden rounded-2xl border border-cream-line bg-sand/40 px-4 py-4 text-sm leading-relaxed text-espresso-soft">
        {children}
      </div>
    </div>
  )
}

export default function Privacy() {
  const navigate = useNavigate()

  return (
    <div className="relative min-h-screen bg-cream pb-10">
      <header className="flex items-center px-5 pt-6">
        <button
          type="button"
          aria-label="Geri"
          onClick={() => navigate(-1)}
          className="flex h-9 w-9 items-center justify-center rounded-full bg-sand text-espresso-soft"
        >
          <ChevronLeft size={20} />
        </button>
        <h1 className="ml-3 font-display text-xl text-espresso">
          KVKK Aydınlatma Metni / Gizlilik Politikası
        </h1>
      </header>

      {/* Taslak uyarısı - en üstte, gözden kaçmayacak şekilde */}
      <div className="mt-5 px-5">
        <div className="flex gap-3 rounded-2xl border border-tan-dark/30 bg-tan-dark/10 px-4 py-4">
          <AlertTriangle size={18} className="mt-0.5 shrink-0 text-tan-dark" />
          <p className="text-xs leading-relaxed text-espresso-soft">
            <span className="font-semibold text-espresso">
              Bu metin bir taslaktır.
            </span>{' '}
            Kod tabanı incelenerek iyi niyetle hazırlanmıştır, ancak bir avukat
            veya KVKK uzmanı tarafından onaylanmamıştır. Bu metin{' '}
            <span className="font-semibold text-espresso">hukuki tavsiye değildir</span>{' '}
            ve gerçek kullanıcı verisi toplayan bir yayına alınmadan önce yetkin bir
            hukuk danışmanına/KVKK uzmanına onaylatılmalıdır.
          </p>
        </div>
      </div>

      <p className="mt-5 px-5 text-xs text-taupe">
        Son güncelleme: 30 Eylül 2026 (taslak sürüm)
      </p>

      {/* 1. Veri sorumlusu */}
      <Section icon={ShieldCheck} title="1. Veri Sorumlusunun Kimliği">
        <p>
          Keşfet Plus, şu an için henüz bir şirket/tüzel kişilik olarak
          kurulmamış, geliştirme aşamasında bir uygulamadır. Bu nedenle KVKK
          anlamında "veri sorumlusu" sıfatı, uygulamayı işleten gerçek
          kişi(ler)e aittir. Kişisel verilerinizle ilgili her türlü soru,
          talep ve başvuru için{' '}
          <a href={`mailto:${SUPPORT_EMAIL}`} className="font-medium text-tan-dark underline">
            {SUPPORT_EMAIL}
          </a>{' '}
          adresinden bize ulaşabilirsiniz. Proje resmi bir tüzel kişilik
          altında yayına alındığında bu bölüm güncellenecektir.
        </p>
      </Section>

      {/* 2. İşlenen kişisel veri kategorileri */}
      <Section icon={Database} title="2. İşlenen Kişisel Veri Kategorileri">
        <p className="mb-2">Uygulamayı kullanırken aşağıdaki verileri işliyoruz:</p>
        <ul className="list-disc space-y-1.5 pl-4">
          <li>
            <span className="font-medium text-espresso">Kimlik/İletişim verisi:</span>{' '}
            e-posta adresi, görünen isim (kayıt olurken).
          </li>
          <li>
            <span className="font-medium text-espresso">Hesap güvenliği verisi:</span>{' '}
            şifrenizin bcrypt ile geri döndürülemez biçimde hash'lenmiş hâli
            (şifrenizin kendisi hiçbir zaman düz metin olarak saklanmaz).
          </li>
          <li>
            <span className="font-medium text-espresso">Kullanıcı içeriği:</span>{' '}
            yazdığınız yorumlar, durum paylaşımları (check-in/status metni ve
            etiketi), şikayet metinleri.
          </li>
          <li>
            <span className="font-medium text-espresso">Konum verisi (isteğe bağlı):</span>{' '}
            yorum veya check-in yaparken tarayıcı/cihaz izniyle paylaşırsanız,
            enlem/boylam ve konum doğruluk (accuracy) değeri. Bu veri, yalnızca
            izin verdiğinizde gönderilir; reddetmeniz hâlinde yorum veya
            check-in yine de kaydedilir, sadece "konum doğrulandı" rozetini
            alamaz.
          </li>
          <li>
            <span className="font-medium text-espresso">İlişki/etkileşim verisi:</span>{' '}
            engellediğiniz kullanıcıların listesi (blocked_user_ids),
            moderatör olup olmadığınız bilgisi, bir yorumu/durumu "faydalı"
            olarak işaretlediğiniz bilgisi.
          </li>
          <li>
            <span className="font-medium text-espresso">Şikayet verisi:</span>{' '}
            bir içeriği şikayet ederseniz, şikayet eden kullanıcının kimliği,
            şikayet edilen içerik ve yazdığınız şikayet gerekçesi metni.
          </li>
          <li>
            <span className="font-medium text-espresso">Push bildirim verisi:</span>{' '}
            bildirim izni verirseniz, tarayıcınızın oluşturduğu push
            abonelik uç noktası (endpoint) ve şifreleme anahtarları
            (p256dh/auth) — bunlar sizi doğrudan tanımlamaz, yalnızca
            bildirim göndermeye yarar.
          </li>
          <li>
            <span className="font-medium text-espresso">Teknik/işlem verisi:</span>{' '}
            oturum token'ı ve oluşturulma zamanı, istek atılan IP adresi
            (yalnızca kötüye kullanımı/hız sınırını — rate limit — tespit
            etmek amacıyla, anlık olarak).
          </li>
        </ul>
      </Section>

      {/* 3. İşleme amaçları */}
      <Section icon={Send} title="3. Kişisel Verilerin İşlenme Amaçları">
        <ul className="list-disc space-y-1.5 pl-4">
          <li>Hesap oluşturma, giriş yapma ve oturumunuzu yönetme.</li>
          <li>
            Yorum, check-in ve durum paylaşımı gibi temel uygulama
            işlevlerini sunma.
          </li>
          <li>
            Otomatik güven puanlaması (trust-scoring) ve içerik filtreleme
            yoluyla spam/sahte/uygunsuz içeriği tespit ederek platform
            güvenliğini ve içerik kalitesini koruma (bkz. bölüm 8).
          </li>
          <li>
            Şikayet ve moderasyon süreçlerini yürütme (bir içerik şikayet
            edildiğinde incelenmesi, gerekirse gizlenmesi).
          </li>
          <li>
            İzin verdiğinizde push bildirim gönderme (örn. check-in yaptığınız
            bir mekanda yeni bir durum paylaşıldığında).
          </li>
          <li>
            Kötüye kullanımı önleme, hız sınırlama (rate limiting) ve genel
            güvenlik.
          </li>
        </ul>
      </Section>

      {/* 4. Hukuki sebep */}
      <Section icon={Gavel} title="4. Kişisel Verilerin İşlenmesinin Hukuki Sebebi">
        <p>
          Kişisel verileriniz, kayıt olurken sunulan onay adımıyla verdiğiniz{' '}
          <span className="font-medium text-espresso">açık rızanıza</span>{' '}
          dayanılarak işlenmektedir. Konum verisi özelinde ayrıca belirtmek
          isteriz: konum paylaşımı tamamen isteğe bağlıdır, reddetmeniz
          hizmeti kullanmanızı engellemez.
        </p>
      </Section>

      {/* 5. Aktarım */}
      <Section icon={Scale} title="5. Kişisel Verilerin Aktarılması">
        <p className="mb-2">
          Şu an itibarıyla kişisel verileriniz hiçbir üçüncü tarafa/yurt
          dışına aktarılmamaktadır. Uygulamada gördüğünüz Wikimedia, TikTok ve
          Instagram gömülü içerikleri (embed), yalnızca bu platformlardan
          herkese açık içerik/görsel çekip size göstermek için kullanılır —
          bu istekler sunucu tarafında yapılır ve kişisel verinizi bu
          platformlara göndermez.
        </p>
        <p>
          İstisna: TikTok/Instagram gömülü oynatıcılarını görüntülediğinizde,
          bu platformların kendi `embed.js` script'i tarayıcınızda
          çalışır; bu script'lerin kendi çerez/izleme davranışları TikTok ve
          Instagram'ın kendi gizlilik politikalarına tabidir ve bizim
          kontrolümüz dışındadır.
        </p>
      </Section>

      {/* 6. Saklama süresi */}
      <Section icon={Database} title="6. Kişisel Verilerin Saklama Süresi">
        <p>
          Dürüstçe belirtmek gerekirse: uygulamada şu an net, kodlanmış bir
          otomatik silme/saklama süresi politikası bulunmamaktadır. Veriler,
          ilgili işlevin (hesap, yorum, check-in vb.) kod tabanında
          bulunduğu sürece dosya tabanlı depolamada tutulmaktadır. Bu, taslak/
          geliştirme aşamasının bir eksiğidir ve ileride somut bir saklama ve
          silme politikası ile geliştirilecektir.
        </p>
      </Section>

      {/* 7. Haklar */}
      <Section icon={UserCheck} title="7. KVKK Madde 11 Kapsamındaki Haklarınız">
        <p className="mb-2">KVKK'nın 11. maddesi uyarınca aşağıdaki haklara sahipsiniz:</p>
        <ul className="list-disc space-y-1.5 pl-4">
          <li>Kişisel verinizin işlenip işlenmediğini öğrenme,</li>
          <li>İşlenmişse buna ilişkin bilgi talep etme,</li>
          <li>İşlenme amacını ve amacına uygun kullanılıp kullanılmadığını öğrenme,</li>
          <li>Yurt içinde/yurt dışında aktarıldığı üçüncü kişileri bilme,</li>
          <li>Eksik veya yanlış işlenmişse düzeltilmesini isteme,</li>
          <li>
            KVKK'da öngörülen şartlar çerçevesinde verinin silinmesini veya
            yok edilmesini isteme,
          </li>
          <li>
            Düzeltme/silme işlemlerinin, verinin aktarıldığı üçüncü kişilere
            bildirilmesini isteme,
          </li>
          <li>
            İşlenen verinin münhasıran otomatik sistemler ile analiz edilmesi
            sonucu aleyhinize bir sonuç çıkmasına itiraz etme,
          </li>
          <li>
            Kanuna aykırı işlenmesi nedeniyle zarara uğramanız hâlinde
            zararın giderilmesini talep etme.
          </li>
        </ul>
        <p className="mt-3">
          Bu haklarınızı kullanmak için{' '}
          <a href={`mailto:${SUPPORT_EMAIL}`} className="font-medium text-tan-dark underline">
            {SUPPORT_EMAIL}
          </a>{' '}
          adresine e-posta gönderebilirsiniz.
        </p>
      </Section>

      {/* 8. Çerez / otomatik işleme */}
      <Section icon={Cookie} title="8. Çerezler ve Otomatik Karar Verme">
        <p className="mb-2">
          Uygulama, oturumunuzu sürdürmek için üçüncü taraf çerezleri değil,
          tarayıcınızın <span className="font-medium text-espresso">localStorage</span>{' '}
          alanında saklanan bir oturum token'ı kullanır. Bu token yalnızca
          sizi cihazınızda oturum açık tutmaya yarar.
        </p>
        <p className="mb-2">
          Ayrıca, yazdığınız yorum ve durum paylaşımları{' '}
          <span className="font-medium text-espresso">otomatik olarak</span>{' '}
          iki ayrı mekanizmadan geçer:
        </p>
        <ul className="list-disc space-y-1.5 pl-4">
          <li>
            <span className="font-medium text-espresso">Güven puanlaması (trust-scoring):</span>{' '}
            konum tutarlılığı, metin benzerliği ve gönderim hızı gibi kurala
            dayalı sinyallerle bir puan hesaplanır; bu puana göre içerik
            doğrudan yayınlanır, "topluluk incelemesi bekliyor" etiketiyle
            yayınlanır veya moderasyon kuyruğuna alınır.
          </li>
          <li>
            <span className="font-medium text-espresso">İçerik filtreleme:</span>{' '}
            metniniz, küfür/nefret söylemi/açık cinsel içerik içeren bir
            kelime listesiyle otomatik olarak karşılaştırılır; eşleşme
            bulunursa içerik "gizli" duruma alınır. Eşleşen kelimeler hiçbir
            zaman kaydedilmez veya loglanmaz, yalnızca evet/hayır sonucu
            kullanılır.
          </li>
        </ul>
        <p className="mt-2">
          Bu iki mekanizma tamamen kural tabanlıdır (yapay zeka/ücretli dış
          servis kullanılmaz, veri hiçbir zaman uygulama dışına gönderilmez)
          ve bir moderatör tarafından her zaman gözden geçirilebilir/geri
          alınabilir; içerik otomatik olarak kalıcı biçimde silinmez.
        </p>
      </Section>

      {/* Alt uyarı - tekrar */}
      <div className="mt-6 px-5">
        <div className="flex gap-3 rounded-2xl border border-tan-dark/30 bg-tan-dark/10 px-4 py-4">
          <AlertTriangle size={18} className="mt-0.5 shrink-0 text-tan-dark" />
          <p className="text-xs leading-relaxed text-espresso-soft">
            Yinelemek gerekirse:{' '}
            <span className="font-semibold text-espresso">
              bu bir taslak metindir, hukuki tavsiye niteliği taşımaz.
            </span>{' '}
            Gerçek kullanıcı verisi toplanan bir yayına geçmeden önce mutlaka
            bir avukata veya KVKK uzmanına onaylatılmalıdır.
          </p>
        </div>
      </div>

      <div className="mt-6 px-5">
        <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-taupe">
          <Mail size={14} />
          Sorularınız İçin
        </p>
        <div className="overflow-hidden rounded-2xl border border-cream-line bg-sand/40 px-4 py-4">
          <a
            href={`mailto:${SUPPORT_EMAIL}`}
            className="flex w-fit items-center gap-2 rounded-full bg-tan px-4 py-2 text-xs font-medium text-cream"
          >
            <Mail size={14} />
            {SUPPORT_EMAIL}
          </a>
        </div>
      </div>
    </div>
  )
}
