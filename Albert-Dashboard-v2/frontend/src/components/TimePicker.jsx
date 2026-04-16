import { useState, useMemo } from 'react';
import { Clock } from 'lucide-react';
import { parseISO, isToday } from 'date-fns';

function buildTimeOptions(stepMinutes = 30) {
  const options = [];
  for (let hour = 0; hour < 24; hour += 1) {
    for (let minute = 0; minute < 60; minute += stepMinutes) {
      const h = hour.toString().padStart(2, '0');
      const m = minute.toString().padStart(2, '0');
      options.push(`${h}:${m}`);
    }
  }
  return options;
}

const TIME_OPTIONS = buildTimeOptions(30);

export default function TimePicker({ label = 'Run Time', value, onChange, date }) {
  const [isOpen, setIsOpen] = useState(false);

  const options = useMemo(() => {
    if (!date) return TIME_OPTIONS;

    try {
      const targetDate = parseISO(date);
      if (!isToday(targetDate)) return TIME_OPTIONS;

      const now = new Date();
      const currentMinutes = now.getHours() * 60 + now.getMinutes();

      return TIME_OPTIONS.filter((time) => {
        const [h, m] = time.split(':');
        const minutes = parseInt(h, 10) * 60 + parseInt(m, 10);
        return minutes >= currentMinutes;
      });
    } catch {
      return TIME_OPTIONS;
    }
  }, [date]);

  const displayValue = useMemo(() => {
    if (!value || !options.includes(value)) return 'Select time';
    const [h, m] = value.split(':');
    const hour = parseInt(h, 10);
    const period = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 === 0 ? 12 : hour % 12;
    return `${hour12}:${m} ${period}`;
  }, [value, options]);

  const toggleOpen = () => setIsOpen((prev) => !prev);

  const handleSelect = (time) => {
    if (onChange) {
      onChange(time);
    }
    setIsOpen(false);
  };

  return (
    <div className="space-y-2 relative">
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-slate-100">
          {label}
        </label>
      )}
      <button
        type="button"
        onClick={toggleOpen}
        className="w-full flex items-center justify-between gap-2 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-left hover:border-hpe-green/70 focus:outline-none focus:ring-2 focus:ring-hpe-green/70 focus:ring-offset-1 focus:ring-offset-gray-50 dark:focus:ring-offset-slate-950"
      >
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-gray-500 dark:text-slate-400" />
          <span className={value ? 'text-gray-900 dark:text-slate-50' : 'text-gray-400 dark:text-slate-500'}>
            {displayValue}
          </span>
        </div>
        <span className="text-[10px] uppercase tracking-wide text-gray-400 dark:text-slate-500">
          Time
        </span>
      </button>
      {isOpen && (
        <div className="absolute z-20 mt-1 w-40 max-h-60 overflow-y-auto rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-lg py-2 text-sm">
          {options.length === 0 ? (
            <div className="px-3 py-1.5 text-xs text-gray-500 dark:text-slate-400">
              No times remaining today
            </div>
          ) : (
            options.map((time) => (
              <button
                key={time}
                type="button"
                onClick={() => handleSelect(time)}
                className={`w-full px-3 py-1.5 text-left hover:bg-gray-100 dark:hover:bg-slate-800 ${
                  value === time
                    ? 'text-hpe-green font-medium bg-hpe-green/5'
                    : 'text-gray-800 dark:text-slate-100'
                }`}
              >
                {(() => {
                  const [h, m] = time.split(':');
                  const hour = parseInt(h, 10);
                  const period = hour >= 12 ? 'PM' : 'AM';
                  const hour12 = hour % 12 === 0 ? 12 : hour % 12;
                  return `${hour12}:${m} ${period}`;
                })()}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
