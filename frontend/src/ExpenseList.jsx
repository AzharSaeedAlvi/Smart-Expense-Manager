import { useState, useEffect } from "react";

function ExpenseList() {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [spentOn, setSpentOn] = useState("");

  // Edit States

  const [editingId, setEditingId] = useState(null);
  const [editDescription, setEditDescription] = useState("");
  const [editAmount, setEditAmount] = useState("");
  const [editSpentOn, setEditSpentOn] = useState("");

  async function fetchExpenses() {
    const token = localStorage.getItem("token");
    try {
      const response = await fetch("http://localhost:8000/expenses", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error(`Request Failed: ${response.status}`);
      }
      const data = await response.json();
      // console.log('Expenses:', data)
      setExpenses(data);
    } catch (err) {
      setError("Could not load expenses. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchExpenses();
  }, []);

  // Stub Submit Handler

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
        description: description,
        amount: amount,
        spent_on: spentOn,
      }),
    });
    if (response.ok) {
      setDescription("");
      setAmount("");
      setSpentOn("");
      fetchExpenses();
    } else {
      console.error("Add failed", response.status);
    }
  }

  async function handleDelete(id) {
    const token = localStorage.getItem("token");
    const response = await fetch(`http://Localhost:8000/expenses/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.ok) {
      fetchExpenses();
    } else {
      console.error("Delete failed", response.status);
    }
  }

  function startEdit(expense) {
    setEditingId(expense.id);
    setEditDescription(expense.description);
    setEditAmount(expense.amount);
    setEditSpentOn(expense.spent_on);
  }

  function cancelEdit() {
    setEditingId(null);
  }

  async function handleUpdate(id) {
    const token = localStorage.getItem("token");
    const response = await fetch(`http://localhost:8000/expenses/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        description: editDescription,
        amount: editAmount,
        spent_on: editSpentOn,
      }),
    });
    if (response.ok) {
      setEditingId(null); // Updating the setEditingID to null, exits the edit mode.
      fetchExpenses();
    } else {
      console.error("Update Failed", response.status);
    }
  }

  return (
    <div>
      <h2>My Expenses</h2>

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
          value={spentOn}
          onChange={(event) => setSpentOn(event.target.value)}
        />
        <button type="submit"> Add Expense </button>
      </form>

      {loading && <p>Loading expenses...</p>}
      {error && <p style={{ color: "red" }}> {error}</p>}
      {!loading && !error && expenses.length === 0 && (
        <p> No expense yet. Add your first one above.</p>
      )}
      {!loading && !error && expenses.length > 0 && (
        <ul>
          {expenses.map((expense) => (
            <li key={expense.id}>
              {editingId === expense.id ? (
                <>
                  <input
                    type="text"
                    value={editDescription}
                    onChange={(event) => setEditDescription(event.target.value)}
                  />
                  <input
                    type="number"
                    step="0.1"
                    value={editAmount}
                    onChange={(event) => setEditAmount(event.target.value)}
                  />
                  <input
                    type="date"
                    value={editSpentOn}
                    onChange={(event) => setEditSpentOn(event.target.value)}
                  />
                  <button onClick={() => handleUpdate(expense.id)}>Save</button>
                  <button onClick={cancelEdit}>Cancel</button>
                </>
              ) : (
                <>
                  {expense.description} - {expense.amount} on {expense.spent_on}
                  <button onClick={() => startEdit(expense)}>Edit</button>
                  <button onClick={() => handleDelete(expense.id)}>
                    Delete
                  </button>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default ExpenseList;
