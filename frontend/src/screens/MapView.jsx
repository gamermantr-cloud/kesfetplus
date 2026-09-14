import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { ChevronLeft } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'
import { useNavigate } from 'react-router-dom'
import { approxLatLng } from '../lib/districts.js'
import { getAllVenues } from '../lib/data.js'

const ISTANBUL_CENTER = [41.02, 28.965]

// Custom pin so we don't need to bundle Leaflet's default marker images.
const pinIcon = L.divIcon({
  className: '',
  html: '<div style="width:14px;height:14px;border-radius:9999px;background:#b99569;border:2px solid #f6f0e6;box-shadow:0 1px 4px rgba(43,32,24,0.4)"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
})

export default function MapView() {
  const navigate = useNavigate()
  const [venues, setVenues] = useState([])

  useEffect(() => {
    let cancelled = false
    getAllVenues().then((data) => {
      if (!cancelled) setVenues(data)
    })
    return () => {
      cancelled = true
    }
  }, [])

  const points = useMemo(
    () => venues.filter((v) => v.area).map((v) => ({ venue: v, pos: approxLatLng(v) })),
    [venues],
  )

  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center gap-3 border-b border-cream-line bg-cream px-4 py-4">
        <button
          type="button"
          onClick={() => navigate(-1)}
          aria-label="Geri"
          className="flex h-9 w-9 items-center justify-center rounded-full bg-sand text-espresso-soft"
        >
          <ChevronLeft size={20} />
        </button>
        <div>
          <h1 className="font-display text-xl text-espresso">Harita</h1>
          <p className="text-xs text-taupe">{points.length} mekan · yaklaşık ilçe konumu</p>
        </div>
      </header>

      <div className="min-h-0 flex-1">
        <MapContainer center={ISTANBUL_CENTER} zoom={11} scrollWheelZoom style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> katkıda bulunanları'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {points.map(({ venue, pos }) => (
            <Marker key={venue.id} position={[pos.lat, pos.lng]} icon={pinIcon}>
              <Popup>
                <div className="min-w-[140px]">
                  <p className="font-medium text-espresso">{venue.name}</p>
                  {venue.area && <p className="text-xs text-taupe">{venue.area}</p>}
                  <button
                    type="button"
                    onClick={() => navigate(`/place/${venue.id}`)}
                    className="mt-2 rounded-full bg-tan px-3 py-1 text-xs font-medium text-cream"
                  >
                    Detayı gör
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      <p className="border-t border-cream-line bg-cream px-4 py-2 text-center text-[10px] text-taupe">
        Konumlar mekanın bulunduğu ilçenin yaklaşık merkezidir, kesin adres değildir.
      </p>
    </div>
  )
}
