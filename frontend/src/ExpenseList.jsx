import {useState, useEffect} from 'react'



function ExpenseList() {
    const [expenses, setExpenses] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const [description, setDescription] = useState('')
    const [amount, setAmount] = useState('')
    const [spentOn, setSpentOn] = useState('')

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
                // console.log('Expenses:', data)
                setExpenses(data)
                } catch (err) {
                    setError('Could not load expenses. Please try again.')
                    console.error(err)
                }finally {
                    setLoading(false)
                }
        }

        useEffect(() => {
            fetchExpenses()
        }, [])


    // Stub Submit Handler 

    async function handleAdd(event) {
        event.preventDefault()
        const token = localStorage.getItem('token')
        const response = await fetch('http://localhost:8000/expenses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
                description: description,
                amount: amount,
                spent_on: spentOn,
            }),
        })
        if(response.ok) {
            setDescription('')
            setAmount('')
            setSpentOn('')
            fetchExpenses()
        }else {
                    console.error('Add failed', response.status)
        }
    }


    return (
        <div>
            <h2>My Expenses</h2>
            
            <form onSubmit = {handleAdd}>
                <input
                type = "text"
                placeholder = "Description"
                value = {description}
                onChange = {(event) => setDescription(event.target.value)}
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