import { useState, useMemo } from 'react';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react';
import {
  format,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  addDays,
  addMonths,
  isSameMonth,
  isSameDay,
  parseISO,
  isBefore,
  startOfDay,
} from 'date-fns';

export default function DatePicker({ label = 'Schedule Date', value, onChange }) {
  const initialDate = useMemo(() => {
    if (value) {
      try {
        return parseISO(value);
      } catch {
        return new Date();
      }
    }
    return new Date();
  }, [value]);

  const [currentMonth, setCurrentMonth] = useState(startOfMonth(initialDate));
  const [isOpen, setIsOpen] = useState(false);

  const selectedDate = useMemo(() => {
    if (!value) return null;
    try {
      return parseISO(value);
    } catch {
      return null;
    }
  }, [value]);

  const toggleOpen = () => setIsOpen((prev) => !prev);

  const handlePrevMonth = () => {
    setCurrentMonth((prev) => addMonths(prev, -1));
  };

  const handleNextMonth = () => {
    setCurrentMonth((prev) => addMonths(prev, 1));
  };

  const handleSelectDay = (day) => {
    if (!onChange) return;
    onChange(format(day, 'yyyy-MM-dd'));
    setIsOpen(false);
  };

  const renderHeader = () => (
    <div className="flex items-center justify-between mb-2">
      <button
        type="button"
        onClick={handlePrevMonth}
        className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-slate-800 text-gray-600 dark:text-slate-200"
      >
        <ChevronLeft className="w-4 h-4" />
      </button>
      <div className="text-sm font-medium text-gray-900 dark:text-slate-50">
        {format(currentMonth, 'MMMM yyyy')}
      </div>
      <button
        type="button"
        onClick={handleNextMonth}
        className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-slate-800 text-gray-600 dark:text-slate-200"
      >
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );

  const renderDaysOfWeek = () => {
    const days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];
    return (
      <div className="grid grid-cols-7 text-[10px] uppercase tracking-wide text-gray-400 dark:text-slate-500 mb-1">
        {days.map((day) => (
          <div key={day} className="text-center py-1">
            {day}
          </div>
        ))}
      </div>
    );
  };

  const renderCells = () => {
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(monthStart);
    const startDate = startOfWeek(monthStart, { weekStartsOn: 1 });
    const endDate = endOfWeek(monthEnd, { weekStartsOn: 1 });

    const today = startOfDay(new Date());

    const rows = [];
    let days = [];
    let day = startDate;

    while (day <= endDate) {
      for (let i = 0; i < 7; i += 1) {
        const cloneDay = day;
        const isCurrentMonth = isSameMonth(day, monthStart);
        const isSelected = selectedDate && isSameDay(day, selectedDate);
        const isDisabled = isBefore(startOfDay(cloneDay), today);

        days.push(
          <button
            type="button"
            key={format(cloneDay, 'yyyy-MM-dd')}
            onClick={!isDisabled ? () => handleSelectDay(cloneDay) : undefined}
            disabled={isDisabled}
            className={`mx-auto my-0.5 flex h-7 w-7 items-center justify-center rounded-full text-xs transition
              ${isDisabled
                ? 'text-gray-300 dark:text-slate-600 opacity-60 cursor-not-allowed'
                : isSelected
                  ? 'bg-hpe-green text-white shadow-sm'
                  : isCurrentMonth
                    ? 'text-gray-900 dark:text-slate-100 hover:bg-gray-100 dark:hover:bg-slate-800'
                    : 'text-gray-300 dark:text-slate-600 hover:bg-gray-100/40 dark:hover:bg-slate-800/40'}
            `}
          >
            {format(cloneDay, 'd')}
          </button>,
        );
        day = addDays(day, 1);
      }
      rows.push(
        <div key={format(addDays(day, -1), 'yyyy-MM-dd')} className="grid grid-cols-7">
          {days}
        </div>,
      );
      days = [];
    }

    return <div className="space-y-1">{rows}</div>;
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
          <CalendarIcon className="w-4 h-4 text-gray-500 dark:text-slate-400" />
          <span className={value ? 'text-gray-900 dark:text-slate-50' : 'text-gray-400 dark:text-slate-500'}>
            {value ? format(selectedDate || initialDate, 'dd MMM yyyy') : 'Select date'}
          </span>
        </div>
        <span className="text-[10px] uppercase tracking-wide text-gray-400 dark:text-slate-500">
          Calendar
        </span>
      </button>
      {isOpen && (
        <div className="absolute z-20 mt-1 w-64 rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-lg p-3">
          {renderHeader()}
          {renderDaysOfWeek()}
          {renderCells()}
        </div>
      )}
    </div>
  );
}
