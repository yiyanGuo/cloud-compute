<template>
  <div ref="chartRef" class="chart"></div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: {
    type: Object,
    required: true
  }
})

const chartRef = ref(null)
let chart = null

function render() {
  if (!chart && chartRef.value) {
    chart = echarts.init(chartRef.value)
  }
  if (chart) {
    chart.setOption(props.option, true)
  }
}

function resize() {
  chart?.resize()
}

onMounted(() => {
  render()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
})

watch(
  () => props.option,
  () => render(),
  { deep: true }
)
</script>
