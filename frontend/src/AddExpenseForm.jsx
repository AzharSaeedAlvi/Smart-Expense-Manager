import {useState} from 'react';

// Helper for pre-filled todays date

function getTodayString() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2,"0");
  return `${year}-${month}-${day}`;
}

function AddExpenseForm({ onAdded, onAuthError }) {
    const [description, setDescription] = useState("");
    const [amount, setAmount] = useState("");
    const [spentOn, setSpentOn] = useState(getTodayString());
    const [category, setCategory] = useState("");

    async function handleAdd(event) {
        event.preventDefault();
        const token = localStorage.getItem("token");

        const response = await fetch("http://localhost:8000/expenses", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
    },
            body: JSON.stringify({
              description,
              amount,
              spent_on: spentOn,
              category: category.trim() || null,
            }),
        });

        if (response.status === 401) {
            onAuthError();
            return;
        }

        if (response.ok) {
            setDescription("");
            setAmount("");
            setSpentOn(getTodayString());
            setCategory("");
            onAdded(); // Notify parent component that a new expense has been added and refreshes ExpenseList
        } else {
            console.error("Add failed", response.status);
        }
    }

    return (
      <form
        onSubmit={handleAdd}
        className="mb-8 flex flex-col gap-4 rounded-lg bg-gray-50 p-4"
      >
        <h3 className="text-lg font-semibold text-gray-900">
          Add a new expense
        </h3>

        <input
          id="description"
          type="text"
          placeholder="Description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 "
        />
        <input
          id="amount"
          type="number"
          step="0.01"
          placeholder="Amount"
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 "
        />
        <input
          id="spent_on"
          type="date"
          placeholder="Spent On"
          value={spentOn}
          onChange={(event) => setSpentOn(event.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input 
          id="category"
          type="text"
          placeholder="Category (optional)"
          value={category}
          onChange={(event) => setCategory(event.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        <button
          type="submit"
          className="rounded-md bg-blue-600 py-2 font-medium text-white transition-colors hover:bg-blue-700"
        >
          Add Expense
        </button>
      </form>
    );
}

export default AddExpenseForm;