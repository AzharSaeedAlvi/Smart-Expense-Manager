import { useState } from "react";

import ExpenseList from "./ExpenseList";
import LoginForm from "./LoginForm";

function App() {
  // A component, capital A is required. React treats lowercase names as plain HTML tags, not components.
  const [token, setToken] = useState(localStorage.getItem("token"));
  // The value inside useState is the initial value of the state variable. Here, we are initializing the token state with the value stored in localStorage (if any). This allows us to persist the user's login state across page reloads.

  function handleLoginSuccess(newToken) {
    localStorage.setItem("token", newToken);
    setToken(newToken);
  }

  function handleLogout() {
    localStorage.removeItem("token"); // Remove the token from localStorage
    setToken(null);
  }

  if (token) {
    return (
      <div className="min-h-screen bg-slate-100">
        <header className="bg-white shadow-sm">
          <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
            <h1 className="text-2xl font-bold text-slate-800 mb-6 text-center">
              Smart Expense Manager
            </h1>
            <button
              onClick={handleLogout}
              className="text-sm text-slate-600 border border-slate-300 rounded-md px-3 py-1.5 jpver:bg-slate-50 hover:text-slate-900  transition-colors"
            >
              Logout
            </button>
          </div>
        </header>

        <main className="max-w-3xl mx-auto px-6 py-8">
          <ExpenseList onAuthError={handleLogout} />
        {/*OnAuthError is a prop that we are passing to the ExpenseList component. It is a function that will be called when the user is not authorized (i.e., when the token is invalid or expired). This allows us to handle the logout process from within the ExpenseList component. */}
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center">
      <div className="w-full max-w-sm bg-white rounded-xl shadow-md p-8 flex flex-col gap-6 ">
        <h1 className="text-2xl font-bold text-slate-800 mb-6 text-center">
          Smart Expense Manager
        </h1>
        <LoginForm onLoggedIn={handleLoginSuccess} />
      </div>
    </div>
  );
}
export default App; // Makes the component importable by other files. main.jsx does import App from './App.jsx'
