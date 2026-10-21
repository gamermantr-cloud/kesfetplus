import { GURME_SUBCATEGORIES } from '../lib/gurmeSubcategories.js'

export default function SubcategoryChips({ active, onChange }) {
  return (
    <div className="flex gap-2 px-5 mt-2.5 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
      {GURME_SUBCATEGORIES.map((sub) => {
        const Icon = sub.icon
        const isActive = active === sub.id
        return (
          <button
            key={sub.id}
            onClick={() => onChange(isActive ? null : sub.id)}
            className={`flex items-center gap-1 shrink-0 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
              isActive ? 'border-tan bg-tan/15 text-tan-dark' : 'border-sand-dark bg-cream text-espresso-soft'
            }`}
          >
            <Icon size={13} />
            {sub.label}
          </button>
        )
      })}
    </div>
  )
}
