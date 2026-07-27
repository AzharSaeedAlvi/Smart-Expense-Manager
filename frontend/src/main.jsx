import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(       // Finds the root in index.html file
  <StrictMode>
    <App />
  </StrictMode>,
)
