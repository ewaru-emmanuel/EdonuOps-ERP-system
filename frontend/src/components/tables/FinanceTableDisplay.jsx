import React from 'react';

const FinanceTableDisplay = ({ title, data, columns, loading, error }) => {
  const formatValue = (value, column) => {
    if (column.format) return column.format(value);
    if (column.cell) return column.cell(value);
    return value;
  };

  return (
    <div className="p-6 bg-white rounded-xl shadow-md">
      <h3 className="text-xl font-semibold text-gray-700 mb-4">{title}</h3>
      
      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 rounded-md">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {!loading && !error && data.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {columns.map((column, index) => (
                  <th
                    key={index}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {column.header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.map((item, itemIndex) => (
                <tr key={itemIndex} className="hover:bg-gray-50">
                  {columns.map((column, colIndex) => (
                    <td
                      key={colIndex}
                      className="px-6 py-4 whitespace-nowrap text-sm"
                    >
                      {formatValue(item[column.accessor], column)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !error && data.length === 0 && (
        <div className="p-4 text-center text-gray-500">
          No {title.toLowerCase()} data available
        </div>
      )}
    </div>
  );
};

export default FinanceTableDisplay;