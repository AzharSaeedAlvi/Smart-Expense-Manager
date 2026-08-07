import { useState, useEffect } from "react";

import AddExpenseForm from "./AddExpenseForm";

//Helper Function to make it easier to read percentages

function buildComparisonText(comparison) {
  if(comparison.change_percentage === null) {
    return "no previous-month spending to compare";
  }

  const percentage = Number(comparison.change_percentage);

  if(percentage > 0) {
    return `${Math.abs(percentage)}% more than last month`;
  }

  if(percentage < 0) {
  return `${Math.abs(percentage)}% less than last month`;
}

return "Spending is unchanged from last month";
  }

function ExpenseList({ onAuthError }) {
  const [expenses, setExpenses] = useState([]);
  const [monthlyTotal, setMonthlyTotal] = useState("0.00");
  const [monthComparison, setMonthComparison] = useState(null); //Display comparison state:
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
      if (response.status === 401) {
        onAuthError();
        return;
      }
      // We explictly checked for 401 before !response.ok because, if we didn't it would have been caught by the !response.ok and we would not have been able to call onAuthError() and handle the logout process.

      if (!response.ok) {
        throw new Error(`Request Failed: ${response.status}`);
      }
      const data = await response.json();
      // console.log('Expenses:', data)
      setExpenses(data);

      const totalResponse = await fetch(
        "http://localhost:8000/insights/monthly-total",
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );

      if (totalResponse.status == 401) {
        onAuthError();
        return;
      }

      if (!totalResponse.ok) {
        throw new Error(
          `Monthly total request failed: $(totalResponse.status)`,
        );
      }

      const totalData = await totalResponse.json();
      setMonthlyTotal(totalData.total);
      
      const comparisonResponse = await fetch(
        "http://localhost:8000/insights/month-over-month",
        {
          headers: {Authorization: `Bearer ${token}`},
        },
      );

      if(comparisonResponse.status === 401) {
        onAuthError();
        return;
      }

      if(!comparisonResponse.ok){
        throw new Error(
          `Month comparison request failed: ${comparisonResponse.status}`,
        );
      }

      const comparisonData = await comparisonResponse.json();
      setMonthComparison(comparisonData);

    } catch (err) {
      setError("Could not load expenses. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // State updates happen only after the awaited network request.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchExpenses();
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Stub Submit Handler

  async function handleDelete(id) {
    const token = localStorage.getItem("token");
    const response = await fetch(`http://localhost:8000/expenses/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.status === 401) {
      onAuthError();
      return;
    }
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
    if(response.status === 401) {
      onAuthError()
      return;
    }
    if (response.ok) {
      setEditingId(null); // Updating the setEditingID to null, exits the edit mode.
      fetchExpenses();
    } else {
      console.error("Update Failed", response.status);
    }
  }

  return (
    <div className="roundded-xl bg-white p-6 shadow-md">
      <h2 className="mb-6 text-2xl font-semibold text-gray-900">My Expenses</h2>
      {/*This is being handled in a AddExepnseForm.jsx file */}

      <div className="mb-6 rounded-lg bg-blue-50 p-4">
        <p className="text-sm font-medium text-blue-700">Spent this month</p>
        <p className="mt-1 text-3x1 font-bold text-blue-900">{monthlyTotal}</p>
      </div>

      {monthComparison && (
        <div className="mb-6 rounded-lg bg-slate-100 p-4">
          <p className="text-sm font-medium text-slate-600">
            Comapred with last month
          </p>

          <p className="mt-1 text-xl font-bold text-slate-900">
            {Math.abs(Number(monthComparison.change_amount)).toFixed(2)}
          </p>

          <p className="mt-1 text-sm text-slate-600">
            {/* {monthComparison.change_percentage === null
            ? "No previous-month spending to compare"
            : `${monthComparison.change_percentage}% change` } */}
            {buildComparisonText(monthComparison)}
          </p>
        </div>
      )}

      <AddExpenseForm onAdded={fetchExpenses} onAuthError={onAuthError} />

      {/* AddExpenseForm is a child component of ExpenseList. It is responsible for rendering the form to add a new expense. When a new expense is added, it calls the onAdded prop, which is a function passed down from ExpenseList. This function is responsible for refreshing the list of expenses by calling fetchExpenses() again. */}

      {loading && (
        <p className="py-8 text-center text-sm text-grey-500">
          Loading expenses...
        </p>
      )}

      {error && (
        <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p>
      )}

      {!loading && !error && expenses.length === 0 && (
        <p className="rounded-lg border border-dashed border-slate-300 py-8 text-center text-sm text-gray-500">
          No expense yet. Add your first one above.
        </p>
      )}
      {!loading && !error && expenses.length > 0 && (
        <ul className="flex flex-col gap-3">
          {expenses.map((expense) => (
            <li
              key={expense.id}
              className="rounded-lg border border-slate-200 p-4"
            >
              {editingId === expense.id ? (
                <div className="flex flex-col gap-3">
                  <input
                    className="rounded-md border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    type="text"
                    value={editDescription}
                    onChange={(event) => setEditDescription(event.target.value)}
                  />
                  <input
                    className="rounded-md border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    type="number"
                    step="0.1"
                    value={editAmount}
                    onChange={(event) => setEditAmount(event.target.value)}
                  />
                  <input
                    className="rounded-md border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    type="date"
                    value={editSpentOn}
                    onChange={(event) => setEditSpentOn(event.target.value)}
                  />
                  <div className="flex justify-end gap-2"></div>
                  <button
                    type="button"
                    onClick={() => handleUpdate(expense.id)}
                    className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={cancelEdit}
                    className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <>
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <label
                      htmlFor="description"
                      className="text-sm font-medium text-gray-700"
                    >
                      Description
                    </label>
                    <div className="grid min-w-0 flex-1 grid-cols gap-1 text-sm text-gray-700 sm:grid-cols-[minmax(0,1fr)_6rem_7rem] sm:gap-4">
                      <span className="truncate font-medium text-gray-900">
                        {expense.description}
                      </span>

                      <span className="sm:text-right">
                        <span className="font-medium text-gray-500 sm:hidden">
                          Amount:{" "}
                        </span>
                        {expense.amount}
                      </span>

                      <span className="sm:text-right">
                        <span className="font-medium text-gray-500 sm:hidden">
                          Date:{" "}
                        </span>
                        {expense.spent_on}
                      </span>
                    </div>

                    <div className="flex shrink-0 gap-2">
                      <button
                        type="button"
                        onClick={() => startEdit(expense)}
                        className="rounded-md border border-blue-200 px-3 py-1.5 text-sm font-medium text-blue-700 transition-colors hovering:bg-blue-50"
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="rounded-md border border-blue-200 px-3 py-1.5 text-sm font-medium text-red-700 transition-colors hover:bg-red-50"
                        onClick={() => handleDelete(expense.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
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
