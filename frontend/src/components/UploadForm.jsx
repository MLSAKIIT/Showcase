import { useState } from 'react'
import { uploadResume } from '../api/client'

function UploadForm({ onUploadSuccess }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      const allowedExtensions = ['.pdf', '.png', '.jpg', '.jpeg', '.docx']
      const fileExt = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'))
      
      if (allowedTypes.includes(selectedFile.type) || allowedExtensions.some(ext => fileExt === ext)) {
        setFile(selectedFile)
        setError(null)
      } else {
        setError('Invalid file type. Please upload PDF, PNG, JPG, or DOCX files.')
        setFile(null)
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError(null)
    setSuccess(null)

    try {
      const result = await uploadResume(file)
      setSuccess(`Resume uploaded! Job ID: ${result.job_id}`)
      setFile(null)
      e.target.reset()
      
      if (onUploadSuccess) {
        onUploadSuccess(result.job_id)
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Upload Resume
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select File (PDF, PNG, JPG, DOCX)
          </label>
          <input
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.png,.jpg,.jpeg,.docx"
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100
              cursor-pointer"
            disabled={uploading}
          />
        </div>

        {file && (
          <div className="text-sm text-gray-600">
            Selected: <span className="font-medium">{file.name}</span>
            <span className="ml-2 text-gray-400">
              ({(file.size / 1024 / 1024).toFixed(2)} MB)
            </span>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {success}
          </div>
        )}

        <button
          type="submit"
          disabled={!file || uploading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 
            disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? 'Uploading...' : 'Upload & Process'}
        </button>
      </form>
    </div>
  )
}

export default UploadForm

