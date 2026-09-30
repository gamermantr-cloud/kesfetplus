import Skeleton, { SkeletonTheme } from 'react-loading-skeleton'
import 'react-loading-skeleton/dist/skeleton.css'

/**
 * Grid of card-shaped skeletons matching the real venue card layout (h-24
 * image area + two text lines), shown in place of a bare "Yükleniyor..."
 * text while Home/ExploreAll fetch venues. Colors pulled from the sand/cream
 * tokens so the shimmer stays inside the project's palette.
 */
export default function VenueCardSkeleton({ count = 6 }) {
  return (
    <SkeletonTheme baseColor="var(--color-sand-dark)" highlightColor="var(--color-cream)">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-sand rounded-2xl overflow-hidden" aria-hidden="true">
          <Skeleton height={96} className="block" style={{ borderRadius: 0 }} />
          <div className="p-3">
            <Skeleton width="75%" height={13} />
            <div className="mt-1.5">
              <Skeleton width="45%" height={11} />
            </div>
          </div>
        </div>
      ))}
    </SkeletonTheme>
  )
}
