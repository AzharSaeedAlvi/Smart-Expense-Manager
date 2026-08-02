import { useState } from "react"

import ExpenseList  from "./ExpenseList"
import LoginForm from "./LoginForm"

function App() {           // A component, capital A is required. React treats lowercase names as plain HTML tags, not components.
const [token, setToken] = useState(localStorage.getItem('token'))    
// The value inside useState is the initial value of the state variable. Here, we are initializing the token state with the value stored in localStorage (if any). This allows us to persist the user's login state across page reloads.

function handleLoginSuccess(newToken) {
  localStorage.setItem('token', newToken) 
    setToken(newToken);
}

function handleLogout() {
  localStorage.removeItem("token"); // Remove the token from localStorage
  setToken(null);
}

if(token) {
  return (
    <div>
      <h1 className="text-3xl font-bold text-blue-600"> Smart Expense Manager</h1>
      <button onClick={handleLogout}>Logout</button>
      <ExpenseList onAuthError={handleLogout} />
      {/*OnAuthError is a prop that we are passing to the ExpenseList component. It is a function that will be called when the user is not authorized (i.e., when the token is invalid or expired). This allows us to handle the logout process from within the ExpenseList component. */}
    </div>
  );
}

return(
  <div
    <h1 className="text-3xl font-bold text-blue-600">Smart Expense Manager</h1>
    <LoginForm onLoggedIn={handleLoginSuccess} />
      </div>
)
}
export default App        // Makes the component importable by other files. main.jsx does import App from './App.jsx'