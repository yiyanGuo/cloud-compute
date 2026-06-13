import { api } from './client'

export const dashboardApi = {
  get: () => api.get('/dashboard').then((res) => res.data)
}

export const productsApi = {
  list: (params = {}) => api.get('/products', { params }).then((res) => res.data),
  create: (payload) => api.post('/products', payload).then((res) => res.data),
  update: (id, payload) => api.put(`/products/${id}`, payload).then((res) => res.data),
  remove: (id) => api.delete(`/products/${id}`).then((res) => res.data),
  adjustStock: (id, delta) => api.post(`/products/${id}/stock`, { delta }).then((res) => res.data)
}

export const ordersApi = {
  list: (params = {}) => api.get('/orders', { params }).then((res) => res.data),
  detail: (id) => api.get(`/orders/${id}`).then((res) => res.data)
}

export const analysisApi = {
  seed: () => api.post('/analysis/seed').then((res) => res.data),
  run: () => api.post('/analysis/run').then((res) => res.data),
  runs: () => api.get('/analysis/runs').then((res) => res.data)
}
