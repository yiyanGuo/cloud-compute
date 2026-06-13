import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import DashboardView from './views/DashboardView.vue'
import ProductsView from './views/ProductsView.vue'
import OrdersView from './views/OrdersView.vue'
import AnalysisView from './views/AnalysisView.vue'
import './styles/main.css'

const routes = [
  { path: '/', name: 'dashboard', component: DashboardView },
  { path: '/products', name: 'products', component: ProductsView },
  { path: '/orders', name: 'orders', component: OrdersView },
  { path: '/analysis', name: 'analysis', component: AnalysisView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

createApp(App).use(router).mount('#app')
