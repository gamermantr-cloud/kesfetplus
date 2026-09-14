import { Route, Routes } from 'react-router-dom'
import PhoneFrame from './components/PhoneFrame.jsx'
import AIAssistant from './screens/AIAssistant.jsx'
import ExploreAll from './screens/ExploreAll.jsx'
import Home from './screens/Home.jsx'
import MapView from './screens/MapView.jsx'
import Messages from './screens/Messages.jsx'
import Notifications from './screens/Notifications.jsx'
import PlaceDetail from './screens/PlaceDetail.jsx'
import Profile from './screens/Profile.jsx'
import Splash from './screens/Splash.jsx'

export default function App() {
  return (
    <PhoneFrame>
      <Routes>
        <Route path="/" element={<Splash />} />
        <Route path="/home" element={<Home />} />
        <Route path="/place/:placeId" element={<PlaceDetail />} />
        <Route path="/ai" element={<AIAssistant />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/messages" element={<Messages />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/explore" element={<ExploreAll />} />
        <Route path="/map" element={<MapView />} />
      </Routes>
    </PhoneFrame>
  )
}
