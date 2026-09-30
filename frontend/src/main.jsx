import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { LucideProvider } from 'lucide-react'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import { AuthProvider } from './lib/AuthContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {/*
      "Sıcak/organik" karakter: lucide-react ikonlarının varsayılan
      stroke-linecap/linejoin'i zaten "round" (kütüphanenin kendi
      defaultAttributes'i) - burada tek merkezi noktadan (her ikon
      kullanımını tek tek değiştirmeden) sadece stroke-width'i hafifçe
      kalınlaştırıyoruz (2 -> 2.25), çizgiler biraz daha dolgun/yumuşak
      görünsün diye. Bir ikon kendi strokeWidth prop'unu verirse bu
      varsayılanı ezer (context en düşük öncelikli).
    */}
    <LucideProvider strokeWidth={2.25}>
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </LucideProvider>
  </StrictMode>,
)
