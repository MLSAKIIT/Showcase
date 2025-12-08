import { useState } from 'react'
import UploadForm from './components/UploadForm'
import JobList from './components/JobList'
import JobDetails from './components/JobDetails'
import './App.css'

function App() {
  const [selectedJobId, setSelectedJobId] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleUploadSuccess = (jobId) => {
    setSelectedJobId(jobId)
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Resume Processing Pipeline
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Upload resumes, process with AI, and generate deployable portfolios
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Upload & Job List */}
          <div className="lg:col-span-1 space-y-6">
            <UploadForm onUploadSuccess={handleUploadSuccess} />
            <JobList 
              selectedJobId={selectedJobId}
              onSelectJob={setSelectedJobId}
              refreshTrigger={refreshTrigger}
            />
          </div>

          {/* Right Column - Job Details */}
          <div className="lg:col-span-2">
            {selectedJobId ? (
              <JobDetails 
                jobId={selectedJobId}
                onRefresh={() => setRefreshTrigger(prev => prev + 1)}
              />
            ) : (
              <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                Select a job to view details
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App

