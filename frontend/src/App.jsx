import { useState } from "react"

import ExpenseList  from "./ExpenseList"

function App() {           // A component, capital A is required. React treats lowercase names as plain HTML tags, not components.
const [email, setEmail] = useState('')
const [password, setPassword] = useState('')
const [token, setToken] = useState(localStorage.getItem('token'))    // The value inside useState is the initial value of the state variable. Here, we are initializing the token state with the value stored in localStorage (if any). This allows us to persist the user's login state across page reloads.

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
  setToken(data.access_token)
  console.log('Loggedin. Token stored.')
  } else{
  console.log('Login Failed:', response.status)
}
}

if(token) {
  return (
    <div>
      <h1> Smart Expense Manager</h1>
      <button onClick={handleLogout}>Logout</button>
      <ExpenseList onAuthError={handleLogout} />
      {/*OnAuthError is a prop that we are passing to the ExpenseList component. It is a function that will be called when the user is not authorized (i.e., when the token is invalid or expired). This allows us to handle the logout process from within the ExpenseList component. */}
    </div>
  );
}

function handleLogout() {
  localStorage.removeItem('token')   // Remove the token from localStorage
  setToken(null)
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
    
  </div>
)
}
export default App        // Makes the component importable by other files. main.jsx does import App from './App.jsx'