import { useState } from "react"

import ExpenseList  from "./ExpenseList"

function App() {           // A component, capital A is required. React treats lowercase names as plain HTML tags, not components.
const [email, setEmail] = useState('')
const [password, setPassword] = useState('')

async function handleSubmit(event) {     //If async is missing, then it would not allow await inside. 
  event.preventDefault()                // Prevent the page from going blank when we submmit.
  
  const formBody = new URLSearchParams()     // Builds the form encoded body
  formBody.append('username', email)
  formBody.append('password', password)

  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: formBody,
  })
  
  if (response.ok){
  const data = await response.json()
  localStorage.setItem('token', data.access_token)
  console.log('Loggedin. Token stored.')
  } else{
  console.log('Login Failed:', response.status)
}
}

return(
  <div>
    <h1>Smart Expense Manger</h1>
    <form onSubmit={handleSubmit}>
      <input 
      type ="email"
      placeholder="Email"
      value={email}
      onChange={(event) => setEmail(event.target.value)}
    />
        <input 
      type="password"
      placeholder="password"
      value={password}
      onChange={(event) => setPassword(event.target.value)}
      />
      <button type="submit">Log in</button> 
      </form>
      <ExpenseList />
  </div>
)
}
export default App        // Makes the component importable by other files. main.jsx does import App from './App.jsx'