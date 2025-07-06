import { useState, useEffect } from 'react'
import { PlusIcon } from '@heroicons/react/24/solid'
import anime from 'animejs'

const TransactionForm = ({ onSubmit, currentUser }) => {
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    type: 'expense',
    date: new Date().toISOString().split('T')[0]
  })

  useEffect(() => {
    // Animate form appearance
    anime({
      targets: '.transaction-form',
      translateY: [20, 0],
      opacity: [0, 1],
      duration: 800,
      easing: 'easeOutElastic(1, .8)'
    })
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      ...formData,
      amount: parseFloat(formData.amount),
      user: currentUser
    })
    setFormData({
      amount: '',
      description: '',
      type: 'expense',
      date: new Date().toISOString().split('T')[0]
    })
  }

  return (
    <div className="card transaction-form">
      <h2 className="text-xl font-semibold mb-4">Add Transaction</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Amount
          </label>
          <input
            type="number"
            step="0.01"
            value={formData.amount}
            onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
            className="input"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <input
            type="text"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="input"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Type
          </label>
          <select
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            className="input"
          >
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Date
          </label>
          <input
            type="date"
            value={formData.date}
            onChange={(e) => setFormData({ ...formData, date: e.target.value })}
            className="input"
            required
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary w-full flex items-center justify-center gap-2"
        >
          <PlusIcon className="h-5 w-5" />
          Add Transaction
        </button>
      </form>
    </div>
  )
}

export default TransactionForm 