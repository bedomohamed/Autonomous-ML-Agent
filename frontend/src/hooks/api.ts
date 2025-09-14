import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { FileData } from '../types'

// API endpoints
const API_BASE = '/api'

// Configure axios with longer timeout for AI operations
const api = axios.create({
  timeout: 120000, // 120 seconds timeout for E2B sandbox operations
  headers: {
    'Content-Type': 'application/json'
  }
})

// Types for API responses
interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
}

interface UploadResponse {
  success: boolean
  data: FileData
}

interface AnalysisData {
  experiment_id: string
  analysis: any
  preprocessing_prompt: string
  dataset_info: any
}


// Upload file mutation
export const useUploadFile = () => {
  return useMutation({
    mutationFn: async ({ file, onUploadProgress }: {
      file: File
      onUploadProgress?: (progress: number) => void
    }): Promise<UploadResponse> => {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post(`${API_BASE}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 seconds for file upload
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0
          onUploadProgress?.(progress)
        },
      })

      return response.data
    },
  })
}

// Analyze dataset mutation
export const useAnalyzeDataset = () => {
  return useMutation({
    mutationFn: async ({
      storageKey,
      targetColumn
    }: {
      storageKey: string
      targetColumn: string
    }): Promise<ApiResponse<AnalysisData>> => {
      const response = await api.post(`${API_BASE}/analyze-dataset`, {
        storage_key: storageKey,
        target_column: targetColumn
      })

      return response.data
    },
  })
}

// Generate preprocessing mutation
export const useGeneratePreprocessing = () => {
  return useMutation({
    mutationFn: async (analysisData: AnalysisData): Promise<ApiResponse<any>> => {
      const response = await api.post(`${API_BASE}/generate-preprocessing`, {
        experiment_id: analysisData.experiment_id,
        analysis_data: analysisData.analysis,
        preprocessing_prompt: analysisData.preprocessing_prompt,
        dataset_info: analysisData.dataset_info
      })

      return response.data
    },
  })
}

// Execute preprocessing mutation
export const useExecutePreprocessing = () => {
  return useMutation({
    mutationFn: async ({
      preprocessingCode,
      storageKey
    }: {
      preprocessingCode: string
      storageKey: string
    }): Promise<ApiResponse<any>> => {
      const response = await api.post(`${API_BASE}/execute-preprocessing`, {
        preprocessing_code: preprocessingCode,
        storage_key: storageKey
      })

      return response.data
    },
  })
}

// Train models mutation
export const useTrainModels = () => {
  return useMutation({
    mutationFn: async ({
      experimentId,
      processedStorageKey,
      targetColumn
    }: {
      experimentId: string
      processedStorageKey: string
      targetColumn: string
    }): Promise<ApiResponse<any>> => {
      const response = await api.post(`${API_BASE}/train-models`, {
        experiment_id: experimentId,
        processed_storage_key: processedStorageKey,
        target_column: targetColumn
      })

      return response.data
    },
  })
}

// Get download URL query
export const useDownloadUrl = (s3Key: string, enabled = true) => {
  return useQuery({
    queryKey: ['downloadUrl', s3Key],
    queryFn: async (): Promise<ApiResponse<{ download_url: string }>> => {
      const response = await api.get(`${API_BASE}/download/${encodeURIComponent(s3Key)}`)
      return response.data
    },
    enabled: enabled && !!s3Key,
    staleTime: 1000 * 60 * 30, // 30 minutes (since presigned URLs expire)
  })
}

// Get results query
export const useResults = (experimentId: string, enabled = true) => {
  return useQuery({
    queryKey: ['results', experimentId],
    queryFn: async (): Promise<ApiResponse<any>> => {
      const response = await api.get(`${API_BASE}/results/${experimentId}`)
      return response.data
    },
    enabled: enabled && !!experimentId,
  })
}