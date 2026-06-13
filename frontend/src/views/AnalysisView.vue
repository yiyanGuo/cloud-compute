<template>
  <section>
    <div class="page-header">
      <div>
        <p class="eyebrow">分析任务</p>
        <h1>Spark 批处理</h1>
      </div>
      <div class="button-row">
        <button :disabled="busy" @click="seed">初始化模拟数据</button>
        <button class="primary" :disabled="busy" @click="run">运行 Spark 分析</button>
      </div>
    </div>

    <div v-if="message" class="message">{{ message }}</div>

    <div class="panel">
      <div class="panel-title">最近运行记录</div>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>状态</th>
            <th>开始时间</th>
            <th>结束时间</th>
            <th>消息</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="run in runs" :key="run.id">
            <td>{{ run.id }}</td>
            <td><span :class="['tag', run.status]">{{ statusText(run.status) }}</span></td>
            <td>{{ formatDate(run.started_at) }}</td>
            <td>{{ run.finished_at ? formatDate(run.finished_at) : '-' }}</td>
            <td class="log-cell">{{ run.message }}</td>
          </tr>
          <tr v-if="runs.length === 0">
            <td colspan="5" class="empty">暂无运行记录</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { analysisApi } from '../api/services'
import { errorMessage } from '../api/client'

const busy = ref(false)
const message = ref('')
const runs = ref([])

async function seed() {
  busy.value = true
  message.value = ''
  try {
    const result = await analysisApi.seed()
    message.value = result.message
    await loadRuns()
  } catch (error) {
    message.value = errorMessage(error)
  } finally {
    busy.value = false
  }
}

async function run() {
  busy.value = true
  message.value = 'Spark 分析运行中，请等待任务完成'
  try {
    const result = await analysisApi.run()
    message.value = result.status === 'success' ? 'Spark 分析完成' : result.message
    await loadRuns()
  } catch (error) {
    message.value = errorMessage(error)
  } finally {
    busy.value = false
  }
}

async function loadRuns() {
  try {
    runs.value = await analysisApi.runs()
  } catch (error) {
    message.value = errorMessage(error)
  }
}

function statusText(status) {
  return {
    running: '运行中',
    success: '成功',
    failed: '失败'
  }[status] || status
}

function formatDate(value) {
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

onMounted(loadRuns)
</script>
