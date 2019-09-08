<template>
  <div id="app">
    <NavBar/>
    <div>
    <router-view/>
    </div>
  </div>
</template>

<script>

import NavBar from './components/NavBar.vue';

export default {
  name: 'App',
  components: {
    NavBar,
  },
};

</script>

<style>

:root {
  --darker:#295BB4;
  --dark:#5786C5;
  --normal:#61B0E2;
  --light:#C9B978;
  --lighter:#F8F7F8;
}

#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  background-color: #f8f9fa;
}

.border-lighter {
  border: 1px solid var(--lighter);
}

.box-container {
  background-color: white;
  border: 1px solid var(--dark);
  border-radius: 2px;
  padding: 16px 16px;
}

.color-dark {
  color: var(--dark);
}

</style>
