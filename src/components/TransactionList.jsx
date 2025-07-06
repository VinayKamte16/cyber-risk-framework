import { useEffect } from 'react'
import { format } from 'date-fns'
import { TrashIcon } from '@heroicons/react/24/solid'
import anime from 'animejs'

const TransactionList = ({ transactions, onDelete }) => {
  useEffect(() => {
    // Animate list items
    anime({
      targets: '.transaction-item',
      translateX: [-20, 0],
      opacity: [0, 1],
      duration: 800,
      delay: anime.stagger(100),
      easing: 'easeOutElastic(1, .8)'
    })
  }, [transactions])

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
      <div className="space-y-4">
        {transactions.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No transactions yet</p>
        ) : (
          transactions.map((transaction) => (
            <div
              key={transaction.id}
              className="transaction-item flex items-center justify-between p-4 bg-gray-50 rounded-lg"
            >
              <div>
                <p className="font-medium">{transaction.description}</p>
                <p className="text-sm text-gray-500">
                  {format(new Date(transaction.date), 'MMM d, yyyy')}
                </p>
              </div>
              <div className="flex items-center gap-4">
                <span
                  className={`font-semibold ${
                    transaction.type === 'income' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {transaction.type === 'income' ? '+' : '-'}${Math.abs(transaction.amount).toFixed(2)}
                </span>
                <button
                  onClick={() => onDelete(transaction.id)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default TransactionList 