import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { Route, Routes, useLocation } from 'react-router-dom'
import PhoneFrame from './components/PhoneFrame.jsx'
import AIAssistant from './screens/AIAssistant.jsx'
import ExploreAll from './screens/ExploreAll.jsx'
import Home from './screens/Home.jsx'
import Login from './screens/Login.jsx'
import MapView from './screens/MapView.jsx'
import Messages from './screens/Messages.jsx'
import Moderation from './screens/Moderation.jsx'
import Notifications from './screens/Notifications.jsx'
import PlaceDetail from './screens/PlaceDetail.jsx'
import Privacy from './screens/Privacy.jsx'
import Profile from './screens/Profile.jsx'
import Register from './screens/Register.jsx'
import Splash from './screens/Splash.jsx'
import Support from './screens/Support.jsx'

// Very light cross-fade between routes (opacity only, no transform - a
// transform here would change the containing block for any `fixed`-
// positioned descendant, e.g. PlaceDetail's bottom action bar/compare
// panel, which are meant to stay pinned to the viewport, not this wrapper).
function AnimatedRoutes() {
  const location = useLocation()
  const shouldReduceMotion = useReducedMotion()

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={location.pathname}
        initial={shouldReduceMotion ? false : { opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={shouldReduceMotion ? undefined : { opacity: 0 }}
        transition={{ duration: 0.14, ease: 'easeOut' }}
      >
        <Routes location={location}>
          <Route path="/" element={<Splash />} />
          <Route path="/home" element={<Home />} />
          <Route path="/place/:placeId" element={<PlaceDetail />} />
          <Route path="/ai" element={<AIAssistant />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/messages" element={<Messages />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/explore" element={<ExploreAll />} />
          <Route path="/map" element={<MapView />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/support" element={<Support />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/moderation" element={<Moderation />} />
        </Routes>
      </motion.div>
    </AnimatePresence>
  )
}

export default function App() {
  return (
    <PhoneFrame>
      <AnimatedRoutes />
    </PhoneFrame>
  )
}
