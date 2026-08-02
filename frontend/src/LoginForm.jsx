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
        <div>
            <form onSubmit={handleSubmit}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    />
                <button type="submit">Log in</button>
            </form>
        </div>  
    );
}

export default LoginForm;