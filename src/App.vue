<template>
  <div id="app">
    <AttentionHead/>
  </div>
</template>

<script>
import AttentionHead from './components/AttentionHead.vue'

export default {
  name: 'app',
  components: {
    AttentionHead
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
