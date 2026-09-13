/**
 * Centers the app in a phone-width column on desktop, full-width on mobile.
 * Every screen renders inside this - keeps the "app on a phone" feel from
 * the mockup even when viewed in a wide browser window.
 */
export default function PhoneFrame({ children }) {
  return (
    <div className="min-h-screen w-full bg-sand flex justify-center">
      <div className="w-full max-w-[430px] min-h-screen bg-cream relative overflow-x-hidden shadow-xl">
        {children}
      </div>
    </div>
  )
}
