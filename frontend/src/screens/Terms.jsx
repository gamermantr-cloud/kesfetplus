import {
  AlertTriangle,
  Ban,
  ChevronLeft,
  Gavel,
  Mail,
  MessageSquareText,
  RefreshCw,
  Scale,
  ShieldAlert,
  Trash2,
  UserCog,
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

export default function Terms() {
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
        <h1 className="ml-3 font-display text-xl text-espresso">Kullanım Şartları</h1>
      </header>

      {/* Taslak uyarısı - Privacy.jsx'teki aynı dürüst uyarıyla birebir */}
      <div className="mt-5 px-5">
        <div className="flex gap-3 rounded-2xl border border-tan-dark/30 bg-tan-dark/10 px-4 py-4">
          <AlertTriangle size={18} className="mt-0.5 shrink-0 text-tan-dark" />
          <p className="text-xs leading-relaxed text-espresso-soft">
            <span className="font-semibold text-espresso">Bu metin bir taslaktır.</span>{' '}
            Kod tabanı incelenerek iyi niyetle hazırlanmıştır, ancak bir avukat
            tarafından onaylanmamıştır. Bu metin{' '}
            <span className="font-semibold text-espresso">hukuki tavsiye değildir</span>{' '}
            ve gerçek kullanıcılara açılan bir yayına alınmadan önce yetkin bir
            hukuk danışmanına onaylatılmalıdır.
          </p>
        </div>
      </div>

      <p className="mt-5 px-5 text-xs text-taupe">
        Son güncelleme: 17 Ekim 2026 (taslak sürüm)
      </p>

      {/* 1. Hizmetin tanımı */}
      <Section icon={Scale} title="1. Hizmetin Tanımı">
        <p>
          Keşfet Plus ("Uygulama"), İstanbul'daki mekanları/restoranları
          keşfetmene, gerçek kullanıcıların yorum ve anlık durum
          paylaşımlarını görmene ve kendin de paylaşım yapmana yarayan, henüz
          geliştirme/erken aşamada olan bir uygulamadır. Uygulama şu an için
          bir şirket/tüzel kişilik tarafından değil, geliştiren gerçek kişi(ler)
          tarafından işletilmektedir (bkz. Gizlilik Politikası bölüm 1).
        </p>
      </Section>

      {/* 2. Hesap */}
      <Section icon={UserCog} title="2. Hesap Oluşturma ve Sorumluluk">
        <ul className="list-disc space-y-1.5 pl-4">
          <li>Hesap oluşturmak için gerçek bir e-posta adresi ve en az 8 karakterli bir şifre gerekir.</li>
          <li>Hesabının güvenliğinden (şifreni gizli tutmaktan) sen sorumlusun.</li>
          <li>
            Girdiğin bilgilerin (görünen isim, yorum, durum paylaşımı)
            doğru olduğunu ve başka bir gerçek kişi/markayı taklit etmediğini
            kabul edersin.
          </li>
          <li>13 yaşından küçüklerin hesap oluşturması beklenmemektedir.</li>
        </ul>
      </Section>

      {/* 3. İçerik ve davranış kuralları */}
      <Section icon={MessageSquareText} title="3. Kullanıcı İçeriği ve Davranış Kuralları">
        <p className="mb-2">Uygulamaya yazdığın yorum, durum paylaşımı ve puanlar için:</p>
        <ul className="list-disc space-y-1.5 pl-4">
          <li>
            İçeriğin senin kendi, gerçek deneyimine dayanmalı — sahte/uydurma
            yorum, puan veya check-in yasaktır (bu kural uygulamanın kendisi
            için de geçerlidir: hiçbir mekan verisi, yorum veya istatistik
            yapay olarak üretilmez).
          </li>
          <li>Hakaret, nefret söylemi, taciz veya açık cinsel içerik yasaktır.</li>
          <li>Reklam/spam amaçlı toplu paylaşım yasaktır.</li>
          <li>
            Paylaştığın içerik otomatik güven puanlaması ve içerik
            filtrelemeden geçer (bkz. Gizlilik Politikası bölüm 8); şüpheli
            veya kurallara aykırı görülen içerik moderasyon incelemesine
            alınabilir veya gizlenebilir.
          </li>
          <li>
            İçeriğini yayınlayarak, Uygulama içinde (örn. mekan sayfasında)
            gösterilmesine izin verirsin; içerik senin kalır, Uygulama
            dışında bir yerde satılmaz veya lisanslanmaz.
          </li>
        </ul>
      </Section>

      {/* 4. Yasaklı kullanım */}
      <Section icon={Ban} title="4. Yasaklı Kullanım">
        <ul className="list-disc space-y-1.5 pl-4">
          <li>Uygulamayı otomatikleştirilmiş araçlarla (bot, scraper) kullanmak,</li>
          <li>Güven puanlaması veya moderasyon sistemini atlatmaya/kandırmaya çalışmak,</li>
          <li>Başka bir kullanıcının hesabına yetkisiz erişmeye çalışmak,</li>
          <li>Uygulamanın altyapısına orantısız yük bindirecek şekilde istek göndermek</li>
        </ul>
        <p className="mt-2">yasaktır ve hesabının askıya alınmasına/silinmesine yol açabilir.</p>
      </Section>

      {/* 5. Hesap silme */}
      <Section icon={Trash2} title="5. Hesabını Silme">
        <p>
          İstediğin zaman, Profil ekranındaki{' '}
          <span className="font-medium text-espresso">"Hesabımı Sil"</span>{' '}
          seçeneğinden şifreni doğrulayarak hesabını kalıcı olarak silebilirsin.
          Bu işlem geri alınamaz: hesabın, oturumların ve bildirim
          aboneliklerin tamamen silinir. Daha önce yazdığın yorum/durum
          paylaşımları, diğer kullanıcıların zaten görmüş olabileceği gerçek
          katkılar olduğu için toptan silinmez — sadece hesabınla bağlantısı
          kaldırılır (bkz. Gizlilik Politikası bölüm 6-7). Verilerinin tümüyle
          silinmesini istersen {' '}
          <a href={`mailto:${SUPPORT_EMAIL}`} className="font-medium text-tan-dark underline">
            {SUPPORT_EMAIL}
          </a>{' '}
          adresinden bizimle iletişime geçebilirsin.
        </p>
      </Section>

      {/* 6. Sorumluluğun sınırlandırılması */}
      <Section icon={ShieldAlert} title="6. Sorumluluğun Sınırlandırılması">
        <p>
          Uygulama "olduğu gibi" sunulmaktadır. Mekan bilgileri, fotoğraflar ve
          kullanıcı yorumları iyi niyetle derlenmiş olsa da güncelliği/doğruluğu
          garanti edilmez — bir mekana gitmeden önce kendi araştırmanı da
          yapmanı öneririz. Uygulama, erken geliştirme aşamasında olduğu için
          kesintiye uğrayabilir veya hatalar içerebilir.
        </p>
      </Section>

      {/* 7. Fesih */}
      <Section icon={Gavel} title="7. Hizmetin Sona Erdirilmesi">
        <p>
          Bu Kullanım Şartları'nı ihlal ettiğini düşündüğümüz bir hesabı
          askıya alabilir veya silebiliriz. Sen de istediğin zaman bölüm 5'te
          açıklanan şekilde hesabını kendin silebilirsin.
        </p>
      </Section>

      {/* 8. Değişiklikler */}
      <Section icon={RefreshCw} title="8. Bu Şartlardaki Değişiklikler">
        <p>
          Uygulama geliştikçe bu metin güncellenebilir. Önemli bir değişiklik
          olduğunda, bu sayfadaki "son güncelleme" tarihini güncelleyeceğiz.
        </p>
      </Section>

      <div className="mt-6 px-5">
        <div className="flex gap-3 rounded-2xl border border-tan-dark/30 bg-tan-dark/10 px-4 py-4">
          <AlertTriangle size={18} className="mt-0.5 shrink-0 text-tan-dark" />
          <p className="text-xs leading-relaxed text-espresso-soft">
            Yinelemek gerekirse:{' '}
            <span className="font-semibold text-espresso">
              bu bir taslak metindir, hukuki tavsiye niteliği taşımaz.
            </span>
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
