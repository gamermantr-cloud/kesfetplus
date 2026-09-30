import { BedDouble, Coffee, Trees, UtensilsCrossed, Wine } from 'lucide-react'

/**
 * Picks a lucide icon representative of a venue's category. Used as the
 * centerpiece of placeholder card backgrounds (CARD_GRADIENTS) when a venue
 * has no real photo, so the card reads as "intentional" rather than an
 * unfinished loading block.
 */
export function getVenueIcon(venue) {
  if (venue.kind === 'hotel') return BedDouble
  if (venue.kind === 'gurme') {
    if (venue.category === 'bar' || venue.category === 'meyhane-deniz') return Wine
    if (venue.category === 'kafe-kahve' || venue.category === 'tatli-pastane') return Coffee
    return UtensilsCrossed
  }
  return Trees
}
