import { api } from './http'

export const appointmentApi = {
  list: () => api.get('/api/appointments'),
  create: (payload) => api.post('/api/appointments', payload),
  updateStatus: (id, status) => api.patch(`/api/appointments/${id}`, { status })
}

export const examApi = {
  questions: (subject) => api.get(`/api/exams/questions?subject=${encodeURIComponent(subject)}`),
  submit: (payload) => api.post('/api/exams/submit', payload)
}

export const scoreApi = {
  list: (params = {}) => {
    const query = new URLSearchParams(params)
    const suffix = query.toString() ? `?${query}` : ''
    return api.get(`/api/scores${suffix}`)
  }
}

export const makeupApi = {
  list: () => api.get('/api/makeups'),
  create: (payload) => api.post('/api/makeups', payload),
  update: (id, payload) => api.patch(`/api/makeups/${id}`, payload)
}

export const ruleApi = {
  list: () => api.get('/api/rules'),
  update: (id, payload) => api.patch(`/api/rules/${id}`, payload)
}

export const exportApi = {
  appointments: (params = {}) => {
    const query = new URLSearchParams(params)
    const suffix = query.toString() ? `?${query}` : ''
    return api.download(`/api/export/appointments${suffix}`, '预约记录.csv')
  },
  scores: (params = {}) => {
    const query = new URLSearchParams(params)
    const suffix = query.toString() ? `?${query}` : ''
    return api.download(`/api/export/scores${suffix}`, '成绩记录.csv')
  },
  makeups: (params = {}) => {
    const query = new URLSearchParams(params)
    const suffix = query.toString() ? `?${query}` : ''
    return api.download(`/api/export/makeups${suffix}`, '补考记录.csv')
  },
  statistics: (params = {}) => {
    const query = new URLSearchParams(params)
    const suffix = query.toString() ? `?${query}` : ''
    return api.download(`/api/export/statistics${suffix}`, '统计报表.csv')
  }
}
