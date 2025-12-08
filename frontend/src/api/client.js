import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadResume = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await client.post('/api/v1/resumes/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const getJobStatus = async (jobId) => {
  const response = await client.get(`/api/v1/jobs/${jobId}`)
  return response.data
}

export const deployJob = async (jobId) => {
  const response = await client.post(`/api/v1/jobs/${jobId}/deploy`)
  return response.data
}

export default client

