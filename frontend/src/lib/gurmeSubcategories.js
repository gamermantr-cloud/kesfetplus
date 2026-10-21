import { Beef, CakeSlice, Coffee, Croissant, Fish, Globe, Pizza, Salad, Sandwich, Soup, Star } from 'lucide-react'

// "Yeme & İçme" altındaki çipler; gurme.json'daki her bar dışı `category` değeri tam olarak birine düşmeli.
export const GURME_SUBCATEGORIES = [
  { id: 'kahvalti', label: 'Kahvaltı & Brunç', icon: Croissant, categories: ['kahvalti'] },
  { id: 'kafe', label: 'Kafe & Kahve', icon: Coffee, categories: ['kafe-kahve'] },
  { id: 'tatli', label: 'Tatlı & Pastane', icon: CakeSlice, categories: ['tatli-pastane'] },
  { id: 'burger', label: 'Burger & Pizza', icon: Pizza, categories: ['burger-pizza'] },
  { id: 'kebap', label: 'Kebap & Et', icon: Beef, categories: ['kebap-lokanta', 'et-restoran'] },
  { id: 'meyhane', label: 'Meyhane & Deniz', icon: Fish, categories: ['meyhane-deniz'] },
  { id: 'esnaf', label: 'Esnaf Lokantası', icon: Soup, categories: ['lokanta-esnaf'] },
  { id: 'sokak', label: 'Sokak Lezzetleri', icon: Sandwich, categories: ['sokak-lezzetleri'] },
  { id: 'fine', label: 'Fine Dining & Michelin', icon: Star, categories: ['michelin', 'fine-dining'] },
  { id: 'dunya', label: 'Dünya Mutfağı', icon: Globe, categories: ['dunya-mutfagi'] },
  { id: 'saglikli', label: 'Sağlıklı & Vegan', icon: Salad, categories: ['saglikli-mutfak', 'vejetaryen'] },
]

export function withSubcategory(category, subId) {
  const sub = category && GURME_SUBCATEGORIES.find((s) => s.id === subId)
  if (!sub) return category
  return { ...category, match: (v) => category.match(v) && sub.categories.includes(v.category) }
}
