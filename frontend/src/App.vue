<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">EC</div>
        <div>
          <strong>电商分析平台</strong>
          <span>Spark + openGauss</span>
        </div>
      </div>
      <nav class="nav">
        <RouterLink to="/">运营看板</RouterLink>
        <RouterLink to="/products">商品管理</RouterLink>
        <RouterLink to="/orders">订单管理</RouterLink>
        <RouterLink to="/analysis">分析任务</RouterLink>
      </nav>
    </aside>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>
