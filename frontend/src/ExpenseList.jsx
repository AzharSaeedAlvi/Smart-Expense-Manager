import {useState, useEffect} from 'react'



function ExpenseList() {
    const [expenses, setExpenses] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const [description, SetDescription] = useState('')
    const [amount, setAmount] = useState('')
    const [spentOn, setSpentOn] = useState('')

    useEffect(() => {
        async function fetchExpenses() {
            const token = localStorage.getItem('token')
            try{
                
                const response = await fetch('http://localhost:8000/expenses', {
                    headers: {Authorization: `Bearer ${token}`},
                })
                if(!response.ok) {
                    throw new Error(`Request Failed: ${response.status}`)
                }    
                const data = await response.json()
                console.log('Expenses:', data)
                setExpenses(data)
                } catch (err) {
                    setError('Could not load expenses. Please try again.')
                    console.log(err)
                }finally {
                    setLoading(false)
                }
        }
        fetchExpenses()
    }, [])


    // Stub Submit Handler 

    function handleAdd(event) {
        event.preventDefault()
        console.log('Would add:', {description, amount, spent_on: spentOn })
    }


    return (
        <div>
            <h2>My Expenses</h2>
            
            <form onSubmit = {handleAdd}>
                <input
                type = "text"
                placeholder = "Description"
                value = {description}
                onChange = {(event) => SetDescription(event.target.value)}
                />
                <input
                type="number"
                step="0.01"
                placeholder="Amount"
                value={amount}
                onChange = {(event) => setAmount(event.target.value)}
                />
                <input
                type = "date"
                value = {spentOn}
                onChange = {(event) => setSpentOn(event.target.value)}
                />
                <button type = "submit"> Add Expense </button>
            </form>
            
            {loading && <p>Loading expenses...</p>}
            {error && <p style ={{color : 'red'}}> {error}</p>}
            {!loading && error && expenses.length === 0 && (
                <p> No expense yet. Add your first one above.</p>
            )}
            {!loading && !error && expenses.length > 0 && (
                <ul>
                    {expenses.map((expense) => (
                        <li key={expense.id}>
                            {expense.description} - {expense.amount} on {expense.spent_on}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
}

export default ExpenseList