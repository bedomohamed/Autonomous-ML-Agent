import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import { Card } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { CloudUpload } from 'lucide-react'
import { FileData } from '../types'
import { useUploadFile } from '../hooks/api'

interface FileUploadProps {
  onUploadSuccess: (data: FileData) => void
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [uploadProgress, setUploadProgress] = useState(0)
  const uploadMutation = useUploadFile()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]

    if (!file.name.endsWith('.csv')) {
      toast.error('Please upload a CSV file')
      return
    }

    setUploadProgress(0)

    uploadMutation.mutate(
      {
        file,
        onUploadProgress: setUploadProgress
      },
      {
        onSuccess: (response) => {
          if (response.success) {
            toast.success('File uploaded successfully!')
            onUploadSuccess(response.data)
          }
        },
        onError: (error: any) => {
          console.error('Upload error:', error)
          toast.error(error.response?.data?.error || 'Upload failed')
        },
        onSettled: () => {
          setUploadProgress(0)
        }
      }
    )
  }, [uploadMutation, onUploadSuccess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
    disabled: uploadMutation.isPending,
  })

  return (
    <Card
      {...getRootProps()}
      className={`relative border-2 border-dashed p-12 text-center cursor-pointer transition-all duration-200 group
        ${isDragActive
          ? 'border-primary bg-primary/5 scale-[1.02] shadow-lg'
          : 'border-muted-foreground/25 hover:border-primary/50 hover:bg-accent/50'
        }
        ${uploadMutation.isPending ? 'opacity-60 cursor-not-allowed' : 'hover:shadow-apple-lg'}
        rounded-apple-lg bg-card`}
    >
      <input {...getInputProps()} />

      {/* Upload Icon */}
      <div className={`mx-auto mb-6 transition-all duration-200 ${isDragActive ? 'scale-110' : 'group-hover:scale-105'}`}>
        <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors duration-200
          ${isDragActive ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary'}`}>
          <CloudUpload size={32} />
        </div>
      </div>

      {uploadMutation.isPending ? (
        <div className="space-y-4">
          <div className="space-y-2">
            <p className="text-body text-foreground font-medium">
              {uploadProgress < 50 ? 'Validating CSV format...' :
               uploadProgress < 90 ? 'Uploading to secure cloud storage...' :
               'Finalizing upload...'}
            </p>
            <p className="text-footnote text-muted-foreground">
              {uploadProgress < 50 ? 'Checking data structure and format' :
               uploadProgress < 90 ? 'Securely storing your data in AWS S3' :
               'Generating preview and finishing up'}
            </p>
          </div>

          {/* Progress Bar */}
          <div className="max-w-xs mx-auto space-y-2">
            <div className="flex justify-between text-caption text-muted-foreground">
              <span>Progress</span>
              <span>{uploadProgress}%</span>
            </div>
            <Progress value={uploadProgress} className="w-full h-2" />
          </div>

          {/* Animated Dots */}
          <div className="flex justify-center space-x-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-2 h-2 bg-primary rounded-full animate-pulse"
                style={{ animationDelay: `${i * 0.2}s` }}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <p className={`text-body font-medium transition-colors duration-200
              ${isDragActive ? 'text-primary' : 'text-foreground'}`}>
              {isDragActive ? 'Drop your CSV file here' : 'Upload CSV File'}
            </p>
            <p className="text-footnote text-muted-foreground mt-2">
              {isDragActive
                ? 'Release to upload your data'
                : 'Drag and drop your file here, or click to browse'
              }
            </p>
          </div>

          {/* File Requirements */}
          <div className="inline-flex items-center space-x-4 text-caption text-muted-foreground">
            <div className="flex items-center space-x-1">
              <div className="w-1 h-1 bg-muted-foreground rounded-full" />
              <span>CSV files only</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-1 h-1 bg-muted-foreground rounded-full" />
              <span>Max 50MB</span>
            </div>
          </div>
        </div>
      )}

      {/* Subtle Background Pattern */}
      <div className="absolute inset-0 opacity-5 pointer-events-none rounded-apple-lg overflow-hidden">
        <div className="w-full h-full" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='hsl(214 100% 50%)' fill-opacity='1'%3E%3Cpath d='M30 30c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10zm10 0c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>
    </Card>
  )
}