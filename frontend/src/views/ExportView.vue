<script setup>
import { reactive, ref } from 'vue'
import { Download, FileSpreadsheet } from 'lucide-vue-next'

import { exportApi } from '../api/modules'
import MessageBar from '../components/MessageBar.vue'

const message = reactive({ text: '', type: 'info' })
const exporting = ref(false)
const exportType = ref('statistics')

const filters = reactive({
  startDate: '',
  endDate: ''
})

const exportOptions = [
  { value: 'appointments', label: '预约记录', description: '导出指定日期范围内的所有预约数据' },
  { value: 'scores', label: '成绩记录', description: '导出指定日期范围内的所有考试成绩' },
  { value: 'makeups', label: '补考记录', description: '导出指定日期范围内的所有补考记录' },
  { value: 'statistics', label: '综合统计报表', description: '导出预约、成绩、补考的汇总统计数据' }
]

function setMessage(text, type = 'info') {
  message.text = text
  message.type = type
}

function getExportParams() {
  const params = {}
  if (filters.startDate) params.startDate = filters.startDate
  if (filters.endDate) params.endDate = filters.endDate
  return params
}

async function handleExport() {
  exporting.value = true
  setMessage('')
  try {
    const params = getExportParams()
    switch (exportType.value) {
      case 'appointments':
        await exportApi.appointments(params)
        break
      case 'scores':
        await exportApi.scores(params)
        break
      case 'makeups':
        await exportApi.makeups(params)
        break
      case 'statistics':
        await exportApi.statistics(params)
        break
    }
    setMessage('导出成功，文件已开始下载', 'success')
  } catch (error) {
    setMessage(error.message || '导出失败', 'error')
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <section class="panel">
    <div class="panel-heading">
      <div>
        <h3>数据导出</h3>
        <p>按日期范围导出预约、成绩和补考数据为 CSV 格式。</p>
      </div>
      <FileSpreadsheet :size="20" />
    </div>

    <MessageBar :message="message.text" :type="message.type" />

    <div class="export-form">
      <div class="field-row">
        <label>
          <span>开始日期</span>
          <input v-model="filters.startDate" type="date" />
        </label>
        <label>
          <span>结束日期</span>
          <input v-model="filters.endDate" type="date" />
        </label>
      </div>

      <div class="export-options">
        <div class="options-label">选择导出类型</div>
        <div class="options-grid">
          <label
            v-for="option in exportOptions"
            :key="option.value"
            class="export-option"
            :class="{ active: exportType === option.value }"
          >
            <input v-model="exportType" type="radio" :value="option.value" />
            <div class="option-content">
              <div class="option-title">{{ option.label }}</div>
              <div class="option-desc">{{ option.description }}</div>
            </div>
          </label>
        </div>
      </div>

      <button class="primary-button" :disabled="exporting" @click="handleExport">
        <Download :size="18" />
        <span>{{ exporting ? '导出中...' : '导出 CSV' }}</span>
      </button>
    </div>
  </section>
</template>

<style scoped>
.export-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.field-row {
  display: flex;
  gap: 1rem;
}

.field-row label {
  flex: 1;
}

.export-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.options-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.export-option {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border: 1.5px solid var(--border-color);
  border-radius: 0.625rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--surface);
}

.export-option:hover {
  border-color: var(--primary-300);
  background: var(--primary-50);
}

.export-option.active {
  border-color: var(--primary-500);
  background: var(--primary-50);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.export-option input[type="radio"] {
  margin-top: 0.25rem;
  accent-color: var(--primary-500);
}

.option-content {
  flex: 1;
}

.option-title {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.option-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

@media (max-width: 640px) {
  .options-grid {
    grid-template-columns: 1fr;
  }

  .field-row {
    flex-direction: column;
  }
}
</style>
