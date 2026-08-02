import { useState } from "react";

function LoginForm({ onLoggedIn }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");


    async function handleSubmit(event) {
      event.preventDefault();
      const formBody = new URLSearchParams();          // Builds the form encoded body
      formBody.append("username", email);
      formBody.append("password", password);

      const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formBody,
      });

      if (response.ok) {
        const data = await response.json();
        onLoggedIn(data.access_token); // <- report success UP to App
      } else {
        console.log("Login Failed:", response.status);
      }
    }

    return(
        
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    className="border border-slate-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    className="border border-slate-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button type="submit" className="bg-blue-600 text-white rounded-md py-2 font-medium hover:bg-blue-700 transition-colors">
                    Log in
                </button>
            </form>
    );
}

export default LoginForm;