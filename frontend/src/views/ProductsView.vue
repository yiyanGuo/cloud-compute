<template>
  <section>
    <div class="page-header">
      <div>
        <p class="eyebrow">商品管理</p>
        <h1>商品与库存维护</h1>
      </div>
      <button class="primary" @click="startCreate">新增商品</button>
    </div>

    <div class="toolbar">
      <input v-model="filters.keyword" placeholder="搜索商品或分类" @keyup.enter="loadProducts" />
      <button @click="loadProducts">查询</button>
    </div>

    <div v-if="message" class="message">{{ message }}</div>

    <div class="panel">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>商品</th>
            <th>分类</th>
            <th>价格</th>
            <th>库存</th>
            <th>安全库存</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td>{{ product.id }}</td>
            <td>{{ product.name }}</td>
            <td>{{ product.category }}</td>
            <td>{{ money(product.price) }}</td>
            <td>{{ product.current_stock }}</td>
            <td>{{ product.safety_stock }}</td>
            <td><span class="tag">{{ product.status === 'active' ? '上架' : '下架' }}</span></td>
            <td class="actions">
              <button @click="startEdit(product)">编辑</button>
              <button @click="adjust(product, 10)">入库 +10</button>
              <button @click="adjust(product, -10)">出库 -10</button>
              <button class="danger-button" @click="remove(product)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="editing" class="modal-mask">
      <form class="modal" @submit.prevent="save">
        <h2>{{ form.id ? '编辑商品' : '新增商品' }}</h2>
        <label>商品名称<input v-model="form.name" required /></label>
        <label>分类<input v-model="form.category" required /></label>
        <label>价格<input v-model.number="form.price" type="number" min="0.01" step="0.01" required /></label>
        <label>当前库存<input v-model.number="form.current_stock" type="number" min="0" required /></label>
        <label>安全库存<input v-model.number="form.safety_stock" type="number" min="0" required /></label>
        <label>
          状态
          <select v-model="form.status">
            <option value="active">上架</option>
            <option value="inactive">下架</option>
          </select>
        </label>
        <div class="modal-actions">
          <button type="button" @click="editing = false">取消</button>
          <button class="primary" type="submit">保存</button>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { productsApi } from '../api/services'
import { errorMessage } from '../api/client'

const products = ref([])
const message = ref('')
const editing = ref(false)
const filters = reactive({ keyword: '' })
const form = reactive(emptyForm())

function emptyForm() {
  return {
    id: null,
    name: '',
    category: '',
    price: 1,
    current_stock: 0,
    safety_stock: 0,
    status: 'active'
  }
}

async function loadProducts() {
  message.value = ''
  try {
    products.value = await productsApi.list({ keyword: filters.keyword || undefined })
  } catch (error) {
    message.value = errorMessage(error)
  }
}

function startCreate() {
  Object.assign(form, emptyForm())
  editing.value = true
}

function startEdit(product) {
  Object.assign(form, product)
  editing.value = true
}

async function save() {
  message.value = ''
  const payload = {
    name: form.name,
    category: form.category,
    price: form.price,
    current_stock: form.current_stock,
    safety_stock: form.safety_stock,
    status: form.status
  }
  try {
    if (form.id) {
      await productsApi.update(form.id, payload)
    } else {
      await productsApi.create(payload)
    }
    editing.value = false
    await loadProducts()
  } catch (error) {
    message.value = errorMessage(error)
  }
}

async function adjust(product, delta) {
  message.value = ''
  try {
    await productsApi.adjustStock(product.id, delta)
    await loadProducts()
  } catch (error) {
    message.value = errorMessage(error)
  }
}

async function remove(product) {
  message.value = ''
  try {
    const result = await productsApi.remove(product.id)
    message.value = result.message
    await loadProducts()
  } catch (error) {
    message.value = errorMessage(error)
  }
}

function money(value) {
  return `¥${Number(value || 0).toFixed(2)}`
}

onMounted(loadProducts)
</script>
