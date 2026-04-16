import { useState, useMemo, useEffect, useRef } from 'react';
import { Check, ChevronDown, X, Search } from 'lucide-react';

/**
 * Fancy multi / single select dropdown
 *
 * Props:
 * - label?: string
 * - placeholder?: string
 * - options: { value: string; label: string; description?: string }[]
 * - value: string[] | string
 * - onChange: (value: string[] | string) => void
 * - multiple?: boolean (default: true)
 */
export default function MultiSelect({
  label,
  placeholder = 'Select...',
  options,
  value,
  onChange,
  multiple = true,
}) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const containerRef = useRef(null);

  const selectedValues = useMemo(() => {
    if (multiple) {
      return Array.isArray(value) ? value : [];
    }
    return typeof value === 'string' && value ? [value] : [];
  }, [value, multiple]);

  const filteredOptions = useMemo(() => {
    if (!search) return options;
    const q = search.toLowerCase();
    return options.filter((opt) =>
      opt.label.toLowerCase().includes(q) ||
      (opt.description && opt.description.toLowerCase().includes(q))
    );
  }, [options, search]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    };

    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [open]);

  const handleToggleOption = (optionValue) => {
    if (multiple) {
      const current = new Set(selectedValues);
      if (current.has(optionValue)) {
        current.delete(optionValue);
      } else {
        current.add(optionValue);
      }
      onChange(Array.from(current));
    } else {
      const next = selectedValues[0] === optionValue ? '' : optionValue;
      onChange(next);
      setOpen(false);
    }
  };

  const clearSelection = (e) => {
    e.stopPropagation();
    onChange(multiple ? [] : '');
  };

  const displayLabel = useMemo(() => {
    if (selectedValues.length === 0) return placeholder;
    const selectedOptions = options.filter((opt) => selectedValues.includes(opt.value));
    if (!multiple) return selectedOptions[0]?.label || placeholder;

    if (selectedOptions.length <= 2) {
      return selectedOptions.map((o) => o.label).join(', ');
    }
    const [first, second, ...rest] = selectedOptions;
    return `${first.label}, ${second.label} +${rest.length}`;
  }, [selectedValues, options, multiple, placeholder]);

  return (
    <div className="w-full" ref={containerRef}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-slate-200 mb-1">
          {label}
        </label>
      )}
      <div className="relative">
        {/* Trigger */}
        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          className="w-full flex items-center justify-between px-3 py-2 rounded-lg border border-gray-300 dark:border-slate-700 bg-white/90 dark:bg-slate-900 text-left text-sm shadow-sm hover:bg-gray-50 dark:hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <span className={`truncate ${selectedValues.length === 0 ? 'text-gray-400 dark:text-slate-500' : 'text-gray-900 dark:text-slate-100'}`}>
            {displayLabel}
          </span>
          <span className="flex items-center gap-1 ml-2">
            {selectedValues.length > 0 && (
              <X
                className="w-3 h-3 text-gray-400 hover:text-gray-600 dark:hover:text-slate-200"
                onClick={clearSelection}
              />
            )}
            <ChevronDown className="w-4 h-4 text-gray-500 dark:text-slate-300" />
          </span>
        </button>

        {/* Dropdown */}
        {open && (
          <div className="absolute z-20 mt-2 w-full rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-lg max-h-72 overflow-hidden">
            <div className="p-2 border-b border-gray-100 dark:border-slate-800 flex items-center gap-2">
              <Search className="w-4 h-4 text-gray-400 dark:text-slate-500" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search..."
                className="w-full bg-transparent text-sm outline-none text-gray-900 dark:text-slate-100 placeholder-gray-400 dark:placeholder-slate-500"
              />
            </div>
            <div className="max-h-60 overflow-y-auto py-1">
              {filteredOptions.length === 0 ? (
                <div className="px-3 py-2 text-xs text-gray-500 dark:text-slate-400">
                  No options found
                </div>
              ) : (
                filteredOptions.map((opt) => {
                  const selected = selectedValues.includes(opt.value);
                  return (
                    <button
                      key={opt.value}
                      type="button"
                      onClick={() => handleToggleOption(opt.value)}
                      className={`w-full px-3 py-2 flex items-center justify-between text-sm hover:bg-primary-50 dark:hover:bg-slate-800 transition-colors ${
                        selected ? 'bg-primary-50 dark:bg-slate-800' : ''
                      }`}
                    >
                      <div className="flex flex-col items-start">
                        <span className="text-gray-900 dark:text-slate-100">
                          {opt.label}
                        </span>
                        {opt.description && (
                          <span className="text-xs text-gray-500 dark:text-slate-400">
                            {opt.description}
                          </span>
                        )}
                      </div>
                      {selected && (
                        <Check className="w-4 h-4 text-hpe-green" />
                      )}
                    </button>
                  );
                })
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
