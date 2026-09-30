/**
 * Shared empty-state pattern: icon in a soft circle + title + description.
 * Used by screens that have no content yet (Notifications, Messages, ...).
 * `icon` is a rendered icon element, e.g. <Bell size={26} />.
 */
export default function EmptyState({ icon, title, description }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-3 px-8 text-center">
      <span className="flex h-14 w-14 items-center justify-center rounded-full bg-sand text-taupe">
        {icon}
      </span>
      <p className="font-display text-lg text-espresso">{title}</p>
      <p className="text-sm text-taupe">{description}</p>
    </div>
  )
}
