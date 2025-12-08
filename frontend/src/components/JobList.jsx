import { useState, useEffect } from 'react'
import { getJobStatus } from '../api/client'

function JobList({ selectedJobId, onSelectJob, refreshTrigger }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)

  // Mock job IDs - in production, you'd fetch from an endpoint
  // For now, we'll track jobs from localStorage or just show selected job
  useEffect(() => {
    // In a real app, you'd have a GET /api/v1/jobs endpoint
    // For now, we'll just show the selected job if it exists
    if (selectedJobId) {
      setLoading(true)
      getJobStatus(selectedJobId)
        .then(job => {
          setJobs([job])
        })
        .catch(err => {
          console.error('Failed to fetch job:', err)
        })
        .finally(() => setLoading(false))
    }
  }, [selectedJobId, refreshTrigger])

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

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Jobs</h2>
        <div className="text-center text-gray-500 py-4">Loading...</div>
      </div>
    )
  }

  if (jobs.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Jobs</h2>
        <div className="text-center text-gray-500 py-4">
          No jobs yet. Upload a resume to get started.
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Jobs</h2>
      <div className="space-y-2">
        {jobs.map((job) => (
          <button
            key={job.job_id}
            onClick={() => onSelectJob(job.job_id)}
            className={`w-full text-left p-4 rounded-lg border-2 transition-colors ${
              selectedJobId === job.job_id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-900">
                Job #{job.job_id}
              </span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                {job.status}
              </span>
            </div>
            <div className="text-xs text-gray-500">
              {new Date(job.created_at).toLocaleString()}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

export default JobList

