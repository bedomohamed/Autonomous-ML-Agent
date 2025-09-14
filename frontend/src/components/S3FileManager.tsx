import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Download, Cloud, FileText, Clock, Shield } from 'lucide-react'
import toast from 'react-hot-toast'
import { useDownloadUrl } from '../hooks/api'

interface S3FileManagerProps {
  s3Key: string
  filename: string
  uploadedAt?: string
  fileSize?: number
  onDownload?: () => void
}

export default function S3FileManager({
  s3Key,
  filename,
  uploadedAt,
  fileSize,
  onDownload
}: S3FileManagerProps) {
  const [triggerDownload, setTriggerDownload] = useState(false)

  // Only fetch download URL when user clicks download
  const { data: downloadData, isLoading, error, refetch } = useDownloadUrl(s3Key, triggerDownload)

  const handleDownload = async () => {
    if (!triggerDownload) {
      setTriggerDownload(true)
      // refetch will be triggered by the enabled condition change
    } else {
      // If we already have the download URL, use it
      if (downloadData?.success && downloadData.data?.download_url) {
        window.open(downloadData.data.download_url, '_blank')
        toast.success('Download started!')
        onDownload?.()
      } else {
        // Refetch if previous attempt failed
        refetch()
      }
    }
  }

  // Handle successful URL fetch
  if (triggerDownload && downloadData?.success && downloadData.data?.download_url) {
    // Auto-trigger download when URL is ready
    setTimeout(() => {
      if (downloadData.data?.download_url) {
        window.open(downloadData.data.download_url, '_blank')
        toast.success('Download started!')
        onDownload?.()
      }
      setTriggerDownload(false) // Reset for next download
    }, 100)
  }

  // Handle error
  if (triggerDownload && error) {
    toast.error((error as any).response?.data?.error || 'Download failed')
    setTriggerDownload(false)
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown size'
    const kb = bytes / 1024
    if (kb < 1024) return `${kb.toFixed(1)} KB`
    return `${(kb / 1024).toFixed(1)} MB`
  }

  const getTimestamp = () => {
    if (uploadedAt) return new Date(uploadedAt).toLocaleString()

    const match = s3Key.match(/uploads\/(\d{8}_\d{6})_/)
    if (match) {
      const timestamp = match[1]
      const date = `${timestamp.slice(0,4)}-${timestamp.slice(4,6)}-${timestamp.slice(6,8)}`
      const time = `${timestamp.slice(9,11)}:${timestamp.slice(11,13)}:${timestamp.slice(13,15)}`
      return new Date(`${date}T${time}`).toLocaleString()
    }

    return 'Recently'
  }

  return (
    <Card className="p-6 bg-gradient-to-br from-card to-card/50 border-border/50 rounded-apple-lg shadow-apple">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Cloud size={20} className="text-primary" />
            </div>
            <div>
              <h3 className="text-callout font-semibold text-foreground">Cloud Storage</h3>
              <p className="text-caption text-muted-foreground">Securely stored in AWS S3</p>
            </div>
          </div>

          <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-200">
            <Shield size={12} className="mr-1" />
            Secured
          </Badge>
        </div>

        {/* File Info */}
        <div className="bg-muted/30 rounded-apple p-4 space-y-3">
          <div className="flex items-center space-x-3">
            <FileText size={16} className="text-muted-foreground" />
            <div className="flex-1">
              <p className="text-footnote font-medium text-foreground truncate">{filename}</p>
              <p className="text-caption text-muted-foreground">Original filename</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-border/30">
            <div className="flex items-center space-x-2">
              <Clock size={14} className="text-muted-foreground" />
              <div>
                <p className="text-caption text-muted-foreground">Uploaded</p>
                <p className="text-footnote font-medium">{getTimestamp()}</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <FileText size={14} className="text-muted-foreground" />
              <div>
                <p className="text-caption text-muted-foreground">Size</p>
                <p className="text-footnote font-medium">{formatFileSize(fileSize)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* S3 Key Display (for developers/debugging) */}
        <details className="group">
          <summary className="text-caption text-muted-foreground cursor-pointer hover:text-foreground transition-colors">
            Show S3 Details
          </summary>
          <div className="mt-2 p-3 bg-muted/20 rounded-apple border border-border/30">
            <p className="text-caption text-muted-foreground mb-1">S3 Key:</p>
            <code className="text-footnote font-mono bg-background px-2 py-1 rounded border break-all">
              {s3Key}
            </code>
          </div>
        </details>

        {/* Download Button */}
        <Button
          onClick={handleDownload}
          disabled={isLoading}
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-medium rounded-apple shadow-apple hover:shadow-apple-lg transition-all duration-200"
        >
          <Download size={16} className="mr-2" />
          {isLoading ? 'Generating Download Link...' : 'Download File'}
        </Button>

        {/* Security Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-apple p-3">
          <div className="flex items-start space-x-2">
            <Shield size={16} className="text-blue-600 mt-0.5" />
            <div>
              <p className="text-caption font-medium text-blue-800">Secure Download</p>
              <p className="text-caption text-blue-700 mt-1">
                Download links are time-limited and expire after 1 hour for security.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}