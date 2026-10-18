/**
 * Loads the real seed data (public/data/*.json, mirrored from
 * database/seed/ in the backend) - no mock/example data.
 */
export async function getPlaces() {
  const res = await fetch('/data/places.json')
  return res.json()
}

export async function getGurme() {
  const res = await fetch('/data/gurme.json')
  return res.json()
}

export async function getHotels() {
  const res = await fetch('/data/hotels.json')
  return res.json()
}

export async function getSahne() {
  const res = await fetch('/data/sahne.json')
  return res.json()
}

export async function getKultur() {
  const res = await fetch('/data/kultur.json')
  return res.json()
}

export async function getAllVenues() {
  const [places, gurme, hotels, sahne, kultur] = await Promise.all([
    getPlaces(),
    getGurme(),
    getHotels(),
    getSahne(),
    getKultur(),
  ])
  return [
    ...places.map((p) => ({ ...p, kind: p.kind ?? 'place' })),
    ...gurme,
    ...hotels,
    ...sahne,
    ...kultur,
  ]
}
