import { FileData } from '../types'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { FileCheck, Database, AlertCircle } from 'lucide-react'

interface CSVPreviewProps {
  data: FileData
}

export default function CSVPreview({ data }: CSVPreviewProps) {
  if (!data || !data.preview) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="flex items-center space-x-2 text-red-600">
          <AlertCircle size={20} />
          <span className="text-sm">No preview data available</span>
        </div>
      </div>
    )
  }

  const hasNulls = data.preview.some(row =>
    data.columns.some(col => row[col] === null || row[col] === undefined)
  )

  return (
    <div className="space-y-6">
      {/* File Info Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-end space-y-2 sm:space-y-0">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <FileCheck size={16} className="text-primary" />
            <p className="text-callout text-foreground font-medium">{data.filename}</p>
          </div>
          <p className="text-footnote text-muted-foreground">
            {data.shape.rows.toLocaleString()} rows × {data.shape.columns} columns
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-1.5 h-1.5 bg-primary rounded-full" />
          <span className="text-caption text-muted-foreground">
            Showing first {Math.min(50, data.preview.length)} rows
          </span>
        </div>
      </div>

      {/* Table Container */}
      <Card className="rounded-apple-lg shadow-apple-lg border-border">
        <CardContent className="p-0">
          <div className="relative overflow-hidden rounded-apple-lg">
            <div className="overflow-x-auto max-h-96">
              <Table>
                <TableHeader className="bg-muted/50 sticky top-0 z-10">
                  <TableRow className="border-b hover:bg-transparent">
                    {data.columns.map((column) => (
                      <TableHead
                        key={column}
                        className="px-4 py-3 text-caption font-semibold text-muted-foreground uppercase tracking-wider"
                      >
                        <div className="flex items-center space-x-2">
                          <span className="truncate">{column}</span>
                          {column.length > 15 && (
                            <div className="w-1 h-1 bg-muted-foreground rounded-full flex-shrink-0" />
                          )}
                        </div>
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.preview.map((row, rowIndex) => (
                    <TableRow
                      key={rowIndex}
                      className="hover:bg-muted/50 transition-colors duration-150 border-b border-border/50"
                    >
                      {data.columns.map((column) => (
                        <TableCell key={column} className="px-4 py-3 text-callout">
                          <div className="max-w-xs">
                            {row[column] !== null && row[column] !== undefined ? (
                              <span className="block truncate text-foreground">{String(row[column])}</span>
                            ) : (
                              <div className="flex items-center space-x-1">
                                <div className="w-1 h-1 bg-muted-foreground rounded-full" />
                                <span className="text-muted-foreground italic text-footnote">null</span>
                              </div>
                            )}
                          </div>
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {/* Gradient Fade for Scroll Indication */}
            <div className="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-t from-card to-transparent pointer-events-none" />
          </div>
        </CardContent>
      </Card>

      {/* Data Quality Indicators */}
      <div className="flex flex-wrap gap-3">
        <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/20">
          <Database size={12} className="mr-1" />
          {data.columns.length} columns
        </Badge>
        <Badge variant="secondary" className="bg-chart-2/10 text-chart-2 border-chart-2/20 hover:bg-chart-2/20">
          <FileCheck size={12} className="mr-1" />
          {data.shape.rows.toLocaleString()} rows
        </Badge>
        {hasNulls && (
          <Badge variant="secondary" className="bg-chart-3/10 text-chart-3 border-chart-3/20 hover:bg-chart-3/20">
            <AlertCircle size={12} className="mr-1" />
            Contains nulls
          </Badge>
        )}
      </div>
    </div>
  )
}