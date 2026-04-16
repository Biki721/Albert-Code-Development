import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, Save, Table, LayoutDashboard } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import ThemeToggle from '../components/ThemeToggle';
import { fixersAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function FixersPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const [workbook, setWorkbook] = useState(null);
  const [activeSheet, setActiveSheet] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fixersAPI.getWorkbook();
        setWorkbook(data);
        if (data.sheets && data.sheets.length > 0) {
          setActiveSheet(data.sheets[0].name);
        }
      } catch (error) {
        toast.error('Failed to load Fixers workbook');
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const activeSheetObj = workbook?.sheets?.find((s) => s.name === activeSheet) || null;

  const updateCell = (rowIndex, columnId, value) => {
    if (!workbook || !activeSheetObj) return;

    const sheets = workbook.sheets.map((sheet) => {
      if (sheet.name !== activeSheet) return sheet;
      const rows = sheet.rows.map((row, idx) => {
        if (idx !== rowIndex) return row;
        return { ...row, [columnId]: value };
      });
      return { ...sheet, rows };
    });

    setWorkbook({ ...workbook, sheets });
  };

  const handleSave = async () => {
    if (!workbook) return;
    setIsSaving(true);
    try {
      await fixersAPI.saveWorkbook(workbook);
      toast.success('Fixers workbook saved');
    } catch (error) {
      toast.error('Failed to save Fixers workbook');
    } finally {
      setIsSaving(false);
    }
  };

  const lastColumnId = activeSheetObj?.columns?.[activeSheetObj.columns.length - 1] || null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950">
      <header className="bg-white/90 dark:bg-slate-950/80 backdrop-blur border-b border-gray-200 dark:border-slate-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-6 w-20 border-4 border-hpe-green rounded-sm bg-transparent" />
            <div className="flex flex-col">
              <span className="text-lg font-semibold text-gray-900 dark:text-slate-50">
                Fixers Table
              </span>
              <span className="text-xs text-gray-600 dark:text-slate-400">
                Welcome, {user?.email}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="btn-secondary flex items-center gap-2"
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </button>
            <button
              onClick={handleLogout}
              className="btn-secondary flex items-center gap-2"
            >
              <Table className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold text-gray-900 dark:text-slate-50 flex items-center gap-2">
              <Table className="w-5 h-5 text-hpe-green" />
              Fixers List
            </h1>
            <p className="text-sm text-gray-600 dark:text-slate-400">
              Edit the Fixers workbook used by Albert.
            </p>
          </div>
          <button
            type="button"
            onClick={handleSave}
            disabled={isSaving || isLoading}
            className="btn-primary inline-flex items-center gap-2"
          >
            {isSaving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Save Changes
              </>
            )}
          </button>
        </div>

        {isLoading && (
          <div className="card flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-hpe-green" />
          </div>
        )}

        {!isLoading && !activeSheetObj && (
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-slate-300">
              No sheets found in Fixers_list.xlsx.
            </p>
          </div>
        )}

        {!isLoading && activeSheetObj && (
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {workbook.sheets.map((sheet) => (
                <button
                  key={sheet.name}
                  type="button"
                  onClick={() => setActiveSheet(sheet.name)}
                  className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                    sheet.name === activeSheet
                      ? 'bg-hpe-green text-white border-hpe-green'
                      : 'bg-white dark:bg-slate-900 text-gray-700 dark:text-slate-200 border-gray-300 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800'
                  }`}
                >
                  {sheet.name}
                </button>
              ))}
            </div>

            <div className="card overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr>
                    {activeSheetObj.columns.map((col) => (
                      <th
                        key={col}
                        className="px-3 py-2 text-left font-semibold bg-slate-900 text-slate-100 border-b border-slate-800"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {activeSheetObj.rows.map((row, rowIndex) => (
                    <tr key={rowIndex} className="border-b border-gray-200 dark:border-slate-800">
                      {activeSheetObj.columns.map((col) => {
                        const value = row[col] ?? '';
                        const editable = col === lastColumnId;
                        const isEmailColumn =
                          typeof col === 'string' && col.toLowerCase().includes('email');
                        const emailText = String(value || '');
                        const emails =
                          isEmailColumn && emailText
                            ? (emailText.match(/[^\s,;]+@[^\s,;]+/g) || [])
                                .map((v) => v.trim())
                                .filter(Boolean)
                            : null;

                        return (
                          <td key={col} className="px-3 py-2 align-middle">
                            {editable && isEmailColumn ? (
                              <textarea
                                value={emails && emails.length > 0 ? emails.join('\n') : emailText}
                                onChange={(e) => updateCell(rowIndex, col, e.target.value)}
                                rows={Math.min(4, Math.max(1, emails ? emails.length : 1))}
                                className="w-full px-2 py-1 rounded border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 text-xs resize-none"
                              />
                            ) : editable ? (
                              <input
                                type="text"
                                value={value}
                                onChange={(e) => updateCell(rowIndex, col, e.target.value)}
                                className="w-full px-2 py-1 rounded border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 text-xs"
                              />
                            ) : isEmailColumn && emails && emails.length > 0 ? (
                              <div className="flex flex-col gap-0.5">
                                {emails.map((item, idx) => (
                                  <span
                                    key={idx}
                                    className="text-xs text-gray-900 dark:text-slate-100"
                                  >
                                    {item}
                                  </span>
                                ))}
                              </div>
                            ) : (
                              <span className="text-xs text-gray-900 dark:text-slate-100 whitespace-pre-wrap">
                                {String(value)}
                              </span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
