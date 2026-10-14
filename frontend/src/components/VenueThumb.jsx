import { Star } from 'lucide-react'
import { photoSrc } from '../lib/api.js'

function hidePhotoOnError(e) {
  e.currentTarget.style.display = 'none'
}

/**
 * Mekan kartının üst fotoğraf alanı. Tek foto varsa tam kaplar, 2-3 foto
 * varsa küçük bir kolaj (1 büyük + 1-2 küçük) gösterir - gerçek mekan
 * fotoğraflarından, uydurma görsel yok.
 */
export default function VenueThumb({ venue, gradientClass, Icon, leftBadge }) {
  const photos = (venue.photos ?? [])
    .map((photo) => photoSrc(photo))
    .filter(Boolean)
    .slice(0, 3)

  return (
    <div
      className={`relative h-24 bg-gradient-to-br ${gradientClass} flex items-center justify-center`}
    >
      <Icon size={28} className="text-cream/60" aria-hidden="true" />
      {photos.length === 1 && (
        <img
          src={photos[0]}
          alt=""
          loading="lazy"
          className="absolute inset-0 h-full w-full object-cover"
          onError={hidePhotoOnError}
        />
      )}
      {photos.length > 1 && (
        <div className="absolute inset-0 flex gap-px">
          <img
            src={photos[0]}
            alt=""
            loading="lazy"
            className="h-full w-1/2 object-cover"
            onError={hidePhotoOnError}
          />
          <div className="flex h-full w-1/2 flex-col gap-px">
            <img
              src={photos[1]}
              alt=""
              loading="lazy"
              className={`w-full object-cover ${photos[2] ? 'h-1/2' : 'h-full'}`}
              onError={hidePhotoOnError}
            />
            {photos[2] && (
              <img
                src={photos[2]}
                alt=""
                loading="lazy"
                className="h-1/2 w-full object-cover"
                onError={hidePhotoOnError}
              />
            )}
          </div>
        </div>
      )}
      {venue.rating && (
        <div className="absolute top-2 right-2 flex items-center gap-1 bg-cream/90 rounded-full px-2 py-0.5 text-xs font-semibold text-espresso">
          <Star size={11} className="fill-gold text-gold" />
          {venue.rating}
        </div>
      )}
      {leftBadge}
    </div>
  )
}
