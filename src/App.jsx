import { useState, useEffect } from 'react'
import { format, startOfDay, startOfWeek, startOfMonth } from 'date-fns'
import anime from 'animejs'
import TransactionForm from './components/TransactionForm'
import TransactionList from './components/TransactionList'
import Summary from './components/Summary'
import TimeRangeSelector from './components/TimeRangeSelector'

function App() {
  const [transactions, setTransactions] = useState([])
  const [timeRange, setTimeRange] = useState('day')
  const [user, setUser] = useState('user1') // Default to user1

  useEffect(() => {
    // Load transactions from localStorage
    const savedTransactions = localStorage.getItem('moneyJarTransactions')
    if (savedTransactions) {
      setTransactions(JSON.parse(savedTransactions))
    }
  }, [])

  useEffect(() => {
    // Save transactions to localStorage
    localStorage.setItem('moneyJarTransactions', JSON.stringify(transactions))
    
    // Animate totals
    anime({
      targets: '.total-amount',
      translateY: [20, 0],
      opacity: [0, 1],
      duration: 1000,
      easing: 'easeOutElastic(1, .8)'
    })
  }, [transactions])

  const addTransaction = (transaction) => {
    setTransactions([...transactions, { ...transaction, id: Date.now() }])
  }

  const deleteTransaction = (id) => {
    setTransactions(transactions.filter(t => t.id !== id))
  }

  const getFilteredTransactions = () => {
    const now = new Date()
    let startDate

    switch (timeRange) {
      case 'day':
        startDate = startOfDay(now)
        break
      case 'week':
        startDate = startOfWeek(now)
        break
      case 'month':
        startDate = startOfMonth(now)
        break
      default:
        startDate = startOfDay(now)
    }

    return transactions.filter(t => new Date(t.date) >= startDate)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-8">
          Money Jar
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-6">
            <TransactionForm onSubmit={addTransaction} currentUser={user} />
            <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
          </div>
          
          <div className="space-y-6">
            <Summary transactions={getFilteredTransactions()} />
            <TransactionList 
              transactions={getFilteredTransactions()} 
              onDelete={deleteTransaction}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App 