import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { CloudArrowUpIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import axios from 'axios'
import { FileData } from '../types'

interface FileUploadProps {
  onUploadSuccess: (data: FileData) => void
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]

    if (!file.name.endsWith('.csv')) {
      toast.error('Please upload a CSV file')
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    setUploadProgress(0)

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0
          setUploadProgress(progress)
        },
      })

      if (response.data.success) {
        toast.success('File uploaded successfully!')
        onUploadSuccess(response.data.data)
      }
    } catch (error: any) {
      console.error('Upload error:', error)
      toast.error(error.response?.data?.error || 'Upload failed')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }, [onUploadSuccess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
    disabled: uploading,
  })

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
        ${isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'}
        ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      <input {...getInputProps()} />

      <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />

      {uploading ? (
        <div className="space-y-2">
          <p className="text-sm text-gray-600">Uploading...</p>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="text-xs text-gray-500">{uploadProgress}%</p>
        </div>
      ) : isDragActive ? (
        <p className="text-sm text-gray-600">Drop the CSV file here...</p>
      ) : (
        <div>
          <p className="text-sm text-gray-600">
            Drag and drop a CSV file here, or click to select
          </p>
          <p className="text-xs text-gray-500 mt-2">Maximum file size: 50MB</p>
        </div>
      )}
    </div>
  )
}