import { useState, useEffect } from 'react'
import { getJobStatus, deployJob } from '../api/client'

function JobDetails({ jobId, onRefresh }) {
  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deploying, setDeploying] = useState(false)

  useEffect(() => {
    fetchJobStatus()
    const interval = setInterval(() => {
      if (job?.status === 'pending' || job?.status === 'processing') {
        fetchJobStatus()
      }
    }, 3000) // Poll every 3 seconds if processing

    return () => clearInterval(interval)
  }, [jobId])

  const fetchJobStatus = async () => {
    try {
      setLoading(true)
      const data = await getJobStatus(jobId)
      setJob(data)
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch job status')
    } finally {
      setLoading(false)
    }
  }

  const handleDeploy = async () => {
    if (!confirm('Deploy this resume to Vercel?')) return

    setDeploying(true)
    try {
      await deployJob(jobId)
      alert('Deployment started! Check the job status for updates.')
      fetchJobStatus()
      if (onRefresh) onRefresh()
    } catch (err) {
      alert(err.response?.data?.detail || err.message || 'Deployment failed')
    } finally {
      setDeploying(false)
    }
  }

  if (loading && !job) {
    return (
      <div className="bg-white rounded-lg shadow p-8">
        <div className="text-center text-gray-500">Loading job details...</div>
      </div>
    )
  }

  if (error && !job) {
    return (
      <div className="bg-white rounded-lg shadow p-8">
        <div className="text-red-600">Error: {error}</div>
      </div>
    )
  }

  if (!job) return null

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-blue-100 text-blue-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Job #{job.job_id}</h2>
          <p className="text-sm text-gray-500 mt-1">
            Created: {new Date(job.created_at).toLocaleString()}
          </p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(job.status)}`}>
          {job.status.toUpperCase()}
        </span>
      </div>

      {job.error_message && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          <strong>Error:</strong> {job.error_message}
        </div>
      )}

      {/* Artifacts */}
      {Object.keys(job.artifacts || {}).length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Artifacts</h3>
          <div className="space-y-2">
            {Object.entries(job.artifacts).map(([type, url]) => (
              <div key={type} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <span className="font-medium text-gray-700 capitalize">{type.replace('_', ' ')}</span>
                </div>
                {type === 'preview' ? (
                  <a
                    href={url.startsWith('http') ? url : `http://localhost:8000${url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Preview →
                  </a>
                ) : (
                  <a
                    href={url.startsWith('http') ? url : `http://localhost:8000${url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Download
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      {job.status === 'completed' && (
        <div className="flex gap-3">
          {job.artifacts?.preview && (
            <a
              href={job.artifacts.preview.startsWith('http') ? job.artifacts.preview : `http://localhost:8000${job.artifacts.preview}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 text-center transition-colors"
            >
              View Preview
            </a>
          )}
          <button
            onClick={handleDeploy}
            disabled={deploying}
            className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 
              disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {deploying ? 'Deploying...' : 'Deploy to Vercel'}
          </button>
        </div>
      )}

      {/* Logs */}
      {job.logs && job.logs.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Processing Logs</h3>
          <div className="bg-gray-50 rounded p-4 max-h-64 overflow-y-auto">
            <div className="space-y-2 font-mono text-sm">
              {job.logs.map((log, idx) => (
                <div key={idx} className="text-gray-700">
                  <span className="text-gray-500">[{log.timestamp}]</span>{' '}
                  <span className={`${log.role === 'assistant' ? 'text-blue-600' : 'text-gray-800'}`}>
                    {log.content}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Refresh Button */}
      <button
        onClick={fetchJobStatus}
        className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-200 transition-colors"
      >
        Refresh Status
      </button>
    </div>
  )
}

export default JobDetails

