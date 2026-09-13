import { Route, Routes } from 'react-router-dom'
import PhoneFrame from './components/PhoneFrame.jsx'
import AIAssistant from './screens/AIAssistant.jsx'
import Home from './screens/Home.jsx'
import PlaceDetail from './screens/PlaceDetail.jsx'
import Splash from './screens/Splash.jsx'

export default function App() {
  return (
    <PhoneFrame>
      <Routes>
        <Route path="/" element={<Splash />} />
        <Route path="/home" element={<Home />} />
        <Route path="/place/:placeId" element={<PlaceDetail />} />
        <Route path="/ai" element={<AIAssistant />} />
      </Routes>
    </PhoneFrame>
  )
}
