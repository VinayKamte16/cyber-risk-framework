import { useEffect } from 'react'
import anime from 'animejs'

const TimeRangeSelector = ({ value, onChange }) => {
  useEffect(() => {
    // Animate selector appearance
    anime({
      targets: '.time-range-selector',
      translateY: [20, 0],
      opacity: [0, 1],
      duration: 800,
      easing: 'easeOutElastic(1, .8)'
    })
  }, [])

  return (
    <div className="card time-range-selector">
      <h2 className="text-xl font-semibold mb-4">Time Range</h2>
      <div className="grid grid-cols-3 gap-2">
        {['day', 'week', 'month'].map((range) => (
          <button
            key={range}
            onClick={() => onChange(range)}
            className={`btn ${
              value === range
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {range.charAt(0).toUpperCase() + range.slice(1)}
          </button>
        ))}
      </div>
    </div>
  )
}

export default TimeRangeSelector 