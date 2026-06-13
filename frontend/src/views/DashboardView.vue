<template>
  <section>
    <div class="page-header">
      <div>
        <p class="eyebrow">运营看板</p>
        <h1>销售与库存概览</h1>
      </div>
      <button class="primary" :disabled="loading" @click="loadData">刷新数据</button>
    </div>

    <div v-if="message" class="message">{{ message }}</div>

    <div class="metric-grid">
      <div class="metric">
        <span>累计销售额</span>
        <strong>{{ money(data.summary.total_sales) }}</strong>
      </div>
      <div class="metric">
        <span>订单数</span>
        <strong>{{ data.summary.order_count }}</strong>
      </div>
      <div class="metric">
        <span>商品数</span>
        <strong>{{ data.summary.product_count }}</strong>
      </div>
      <div class="metric danger">
        <span>库存预警</span>
        <strong>{{ data.summary.inventory_alert_count }}</strong>
      </div>
    </div>

    <div class="grid two">
      <div class="panel">
        <div class="panel-title">近 30 日销售趋势</div>
        <EChart :option="dailyOption" />
      </div>
      <div class="panel">
        <div class="panel-title">分类销售额</div>
        <EChart :option="categoryOption" />
      </div>
    </div>

    <div class="grid two">
      <div class="panel">
        <div class="panel-title">热销商品 Top 10</div>
        <EChart :option="productOption" />
      </div>
      <div class="panel">
        <div class="panel-title">库存预警</div>
        <table>
          <thead>
            <tr>
              <th>商品</th>
              <th>分类</th>
              <th>库存</th>
              <th>安全库存</th>
              <th>等级</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in data.inventory_alerts" :key="item.product_id">
              <td>{{ item.product_name }}</td>
              <td>{{ item.category }}</td>
              <td>{{ item.current_stock }}</td>
              <td>{{ item.safety_stock }}</td>
              <td><span :class="['tag', item.alert_level]">{{ alertText(item.alert_level) }}</span></td>
            </tr>
            <tr v-if="data.inventory_alerts.length === 0">
              <td colspan="5" class="empty">暂无库存预警，请先运行 Spark 分析</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import EChart from '../components/EChart.vue'
import { dashboardApi } from '../api/services'
import { errorMessage } from '../api/client'

const loading = ref(false)
const message = ref('')
const data = reactive({
  summary: {
    total_sales: 0,
    order_count: 0,
    product_count: 0,
    inventory_alert_count: 0
  },
  daily_sales: [],
  product_sales: [],
  category_sales: [],
  inventory_alerts: [],
  last_analysis_at: null
})

const dailyOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 48, right: 18, top: 24, bottom: 36 },
  xAxis: { type: 'category', data: data.daily_sales.map((item) => item.sales_date.slice(5, 10)) },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'line',
      smooth: true,
      areaStyle: {},
      data: data.daily_sales.map((item) => Number(item.sales_amount))
    }
  ]
}))

const categoryOption = computed(() => ({
  tooltip: { trigger: 'item' },
  series: [
    {
      type: 'pie',
      radius: ['42%', '72%'],
      data: data.category_sales.map((item) => ({
        name: item.category,
        value: Number(item.sales_amount)
      }))
    }
  ]
}))

const productOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 86, right: 18, top: 24, bottom: 28 },
  xAxis: { type: 'value' },
  yAxis: {
    type: 'category',
    data: data.product_sales.map((item) => item.product_name).reverse()
  },
  series: [
    {
      type: 'bar',
      data: data.product_sales.map((item) => Number(item.sales_amount)).reverse()
    }
  ]
}))

async function loadData() {
  loading.value = true
  message.value = ''
  try {
    const result = await dashboardApi.get()
    Object.assign(data, result)
  } catch (error) {
    message.value = errorMessage(error)
  } finally {
    loading.value = false
  }
}

function money(value) {
  return `¥${Number(value || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function alertText(level) {
  return level === 'critical' ? '严重' : '预警'
}

onMounted(loadData)
</script>
