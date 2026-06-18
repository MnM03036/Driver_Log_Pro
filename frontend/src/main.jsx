import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// NOTE: StrictMode is intentionally removed.
// react-leaflet's MapContainer cannot survive StrictMode's double-mount in dev,
// which causes a fatal crash resulting in a blank screen.
createRoot(document.getElementById('root')).render(
  <App />
)
