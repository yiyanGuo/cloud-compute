import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 300000
})

export function errorMessage(error) {
  return error?.response?.data?.detail || error?.response?.data?.message || error.message || '请求失败'
}
