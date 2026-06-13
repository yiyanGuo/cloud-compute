<template>
  <section>
    <div class="page-header">
      <div>
        <p class="eyebrow">订单管理</p>
        <h1>订单查询与明细</h1>
      </div>
      <button @click="loadOrders">刷新</button>
    </div>

    <div class="toolbar">
      <input v-model="filters.keyword" placeholder="搜索订单号或客户" @keyup.enter="loadOrders" />
      <select v-model="filters.status" @change="loadOrders">
        <option value="">全部状态</option>
        <option value="paid">已支付</option>
        <option value="shipped">已发货</option>
        <option value="completed">已完成</option>
        <option value="cancelled">已取消</option>
      </select>
      <button @click="loadOrders">查询</button>
    </div>

    <div v-if="message" class="message">{{ message }}</div>

    <div class="grid order-layout">
      <div class="panel">
        <table>
          <thead>
            <tr>
              <th>订单号</th>
              <th>客户</th>
              <th>金额</th>
              <th>状态</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="order in orders"
              :key="order.id"
              :class="{ selected: detail?.id === order.id }"
              @click="loadDetail(order.id)"
            >
              <td>{{ order.order_no }}</td>
              <td>{{ order.customer_name }}</td>
              <td>{{ money(order.total_amount) }}</td>
              <td><span class="tag">{{ statusText(order.status) }}</span></td>
              <td>{{ formatDate(order.order_time) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="panel detail-panel">
        <div class="panel-title">订单明细</div>
        <template v-if="detail">
          <div class="detail-head">
            <strong>{{ detail.order_no }}</strong>
            <span>{{ detail.customer_name }} · {{ statusText(detail.status) }}</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>商品</th>
                <th>数量</th>
                <th>单价</th>
                <th>小计</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in detail.items" :key="item.id">
                <td>{{ item.product_name }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ money(item.unit_price) }}</td>
                <td>{{ money(item.line_total) }}</td>
              </tr>
            </tbody>
          </table>
        </template>
        <div v-else class="empty">选择左侧订单查看明细</div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ordersApi } from '../api/services'
import { errorMessage } from '../api/client'

const orders = ref([])
const detail = ref(null)
const message = ref('')
const filters = reactive({ keyword: '', status: '' })

async function loadOrders() {
  message.value = ''
  try {
    orders.value = await ordersApi.list({
      keyword: filters.keyword || undefined,
      status: filters.status || undefined
    })
    if (orders.value.length > 0) {
      await loadDetail(orders.value[0].id)
    } else {
      detail.value = null
    }
  } catch (error) {
    message.value = errorMessage(error)
  }
}

async function loadDetail(id) {
  try {
    detail.value = await ordersApi.detail(id)
  } catch (error) {
    message.value = errorMessage(error)
  }
}

function statusText(status) {
  return {
    paid: '已支付',
    shipped: '已发货',
    completed: '已完成',
    cancelled: '已取消'
  }[status] || status
}

function money(value) {
  return `¥${Number(value || 0).toFixed(2)}`
}

function formatDate(value) {
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

onMounted(loadOrders)
</script>
