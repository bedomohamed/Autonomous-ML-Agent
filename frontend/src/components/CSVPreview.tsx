import { FileData } from '../types'

interface CSVPreviewProps {
  data: FileData
}

export default function CSVPreview({ data }: CSVPreviewProps) {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <p className="text-sm text-gray-600">
            File: <span className="font-medium">{data.filename}</span>
          </p>
          <p className="text-sm text-gray-600">
            Shape: <span className="font-medium">{data.shape.rows} rows × {data.shape.columns} columns</span>
          </p>
        </div>
        <div className="text-sm text-gray-500">
          Showing first {Math.min(50, data.preview.length)} rows
        </div>
      </div>

      <div className="overflow-x-auto border rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {data.columns.map((column) => (
                <th
                  key={column}
                  className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.preview.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                {data.columns.map((column) => (
                  <td key={column} className="px-4 py-2 text-sm text-gray-900 whitespace-nowrap">
                    {row[column] !== null && row[column] !== undefined
                      ? String(row[column])
                      : <span className="text-gray-400 italic">null</span>}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}