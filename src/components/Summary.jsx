import { useEffect } from 'react'
import anime from 'animejs'

const Summary = ({ transactions }) => {
  const totalIncome = transactions
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + t.amount, 0)

  const totalExpenses = transactions
    .filter(t => t.type === 'expense')
    .reduce((sum, t) => sum + t.amount, 0)

  const netAmount = totalIncome - totalExpenses

  useEffect(() => {
    // Animate summary numbers
    anime({
      targets: '.total-amount',
      value: [0, netAmount],
      round: 1,
      duration: 1500,
      easing: 'easeOutElastic(1, .8)'
    })
  }, [netAmount])

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Summary</h2>
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <p className="text-sm text-gray-500">Income</p>
          <p className="text-2xl font-bold text-green-600 total-amount">
            ${totalIncome.toFixed(2)}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-500">Expenses</p>
          <p className="text-2xl font-bold text-red-600 total-amount">
            ${totalExpenses.toFixed(2)}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-500">Net</p>
          <p
            className={`text-2xl font-bold total-amount ${
              netAmount >= 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            ${netAmount.toFixed(2)}
          </p>
        </div>
      </div>
    </div>
  )
}

export default Summary 