import { useEffect, useState } from 'react';
import { Loader2, Save, Plus } from 'lucide-react';
import { adhocLinksAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function AdhocLinkTable() {
  const [table, setTable] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await adhocLinksAPI.getTable();
        setTable(data);
      } catch (error) {
        toast.error('Failed to load adhoc link table');
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const addRow = () => {
    if (!table) return;
    const emptyRow = {};
    table.columns.forEach((c) => {
      emptyRow[c] = '';
    });
    setTable({ ...table, rows: [...table.rows, emptyRow] });
  };

  const updateCell = (rowIndex, columnId, value) => {
    if (!table) return;
    const rows = table.rows.map((row, idx) => {
      if (idx !== rowIndex) return row;
      return { ...row, [columnId]: value };
    });
    setTable({ ...table, rows });
  };

  const handleSave = async () => {
    if (!table) return;
    setIsSaving(true);
    try {
      await adhocLinksAPI.saveTable(table);
      toast.success('Adhoc link table saved');
    } catch (error) {
      toast.error('Failed to save adhoc link table');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="card flex items-center justify-center h-48 mt-4">
        <Loader2 className="w-6 h-6 animate-spin text-hpe-green" />
      </div>
    );
  }

  if (!table) {
    return null;
  }

  return (
    <div className="card mt-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-md font-semibold text-gray-900 dark:text-slate-50">
          Adhoc Link Search Table
        </h3>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={addRow}
            className="btn-secondary flex items-center gap-1 text-xs px-3 py-1.5"
          >
            <Plus className="w-3 h-3" />
            Add Row
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={isSaving}
            className="btn-primary flex items-center gap-1 text-xs px-3 py-1.5"
          >
            {isSaving ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-3 h-3" />
                Save
              </>
            )}
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-xs">
          <thead>
            <tr>
              {table.columns.map((col) => (
                <th
                  key={col}
                  className="px-2 py-1 text-left font-semibold bg-slate-900 text-slate-100 border-b border-slate-800"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row, rowIndex) => (
              <tr key={rowIndex} className="border-b border-gray-200 dark:border-slate-800">
                {table.columns.map((col) => {
                  const value = row[col] ?? '';
                  return (
                    <td key={col} className="px-2 py-1 align-middle">
                      <input
                        type="text"
                        value={value}
                        onChange={(e) => updateCell(rowIndex, col, e.target.value)}
                        className="w-full px-1.5 py-1 rounded border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100"
                      />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
