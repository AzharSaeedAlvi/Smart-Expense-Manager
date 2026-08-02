import {useState} from 'react';

function AddExpenseForm({ onAdded, onAuthError }) {
    const [description, setDescription] = useState("");
    const [amount, setAmount] = useState("");
    const [spentOn, setSpentOn] = useState("");

    async function handleAdd(event) {
        event.preventDefault();
        const token = localStorage.getItem("token");

        const response = await fetch("http://localhost:8000/expenses", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
    },
            body: JSON.stringify({description, amount, spent_on: spentOn}),
        });

        if (response.status === 401) {
            onAuthError();
            return;
        }

        if (response.ok) {
            setDescription("");
            setAmount("");
            setSpentOn("");
            onAdded(); // Notify parent component that a new expense has been added and refreshes ExpenseList
        } else {
            console.error("Add failed", response.status);
        }
    }

    return (
        <form onSubmit={handleAdd}>
            <input
                type="text"
                placeholder="Description"
                value={description} 
                onChange={(event) => setDescription(event.target.value)}
            />
            <input
                type="number"
                step="0.01"
                placeholder="Amount"
                value={amount}
                onChange={(event) => setAmount(event.target.value)}
            />
            <input
                type="date"
                placeholder="Spent On"
                value={spentOn}
                onChange={(event) => setSpentOn(event.target.value)}
            />
            <button type="submit">Add Expense</button>
        </form>
    );
}

export default AddExpenseForm;