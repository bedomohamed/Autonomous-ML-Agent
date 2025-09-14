export interface FileData {
  filename: string
  storage_key: string
  columns: string[]
  preview: Record<string, any>[]
  shape: {
    rows: number
    columns: number
  }
}

export interface ProcessingResult {
  processed_storage_key: string
  statistics: {
    original_shape: [number, number]
    cleaned_shape: [number, number]
    removed_rows: number
    removed_columns: number
    null_values_before: number
    null_values_after: number
  }
  preprocessing_steps: string[]
  download_url?: string
}