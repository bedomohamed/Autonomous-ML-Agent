import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Target, CheckCircle } from 'lucide-react'

interface ColumnSelectorProps {
  columns: string[]
  selectedColumn: string
  onColumnSelect: (column: string) => void
}

export default function ColumnSelector({
  columns,
  selectedColumn,
  onColumnSelect,
}: ColumnSelectorProps) {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-headline text-foreground mb-1">
          Target Column for Prediction
        </label>
        <p className="text-footnote text-muted-foreground">
          Choose the column you want to predict or classify
        </p>
      </div>

      <div className="max-w-sm">
        <Select value={selectedColumn} onValueChange={onColumnSelect}>
          <SelectTrigger className="w-full rounded-apple border-border shadow-apple hover:shadow-apple-lg transition-all duration-200 focus:ring-2 focus:ring-primary/20 focus:border-primary">
            <div className="flex items-center space-x-3">
              <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                selectedColumn ? 'bg-primary' : 'bg-muted-foreground'
              }`} />
              <SelectValue
                placeholder="Select a column..."
                className={`text-callout ${selectedColumn ? 'text-foreground font-medium' : 'text-muted-foreground'}`}
              />
            </div>
          </SelectTrigger>
          <SelectContent className="rounded-apple border-border shadow-apple-xl bg-popover/95 backdrop-blur-xl">
            {columns.map((column, index) => (
              <SelectItem
                key={column}
                value={column}
                className="cursor-pointer focus:bg-accent/50 rounded-apple transition-all duration-150"
              >
                <div className="flex items-center space-x-3 w-full">
                  <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                    selectedColumn === column ? 'bg-primary' : 'bg-muted-foreground'
                  }`} />
                  <div className="flex-1">
                    <p className="text-callout truncate">
                      {column}
                    </p>
                    <p className="text-caption text-muted-foreground">
                      Column {index + 1}
                    </p>
                  </div>
                  {selectedColumn === column && (
                    <CheckCircle size={14} className="text-primary" />
                  )}
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {selectedColumn && (
        <div className="animate-fade-in">
          <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/20">
            <Target size={12} className="mr-1" />
            Target: {selectedColumn}
          </Badge>
        </div>
      )}
    </div>
  )
}