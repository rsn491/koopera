<template>
  <div id="app">
    <NavBar/>
    <div class='container'>
      <SubNav/>
      <router-view/>
    </div>
  </div>
</template>

<script>

import NavBar from './components/NavBar.vue';
import SubNav from './components/SubNav.vue';

export default {
  name: 'App',
  components: {
    NavBar,
    SubNav,
  },
};

</script>

<style>

:root {
  --darker:#295BB4;
  --dark:#5786C5;
  --normal:#61B0E2;
  --light:#c8c8c8;
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
  padding: 24px 32px;
}

.color-dark {
  color: var(--dark);
}

.github-image {
  background-size: contain;
  background-position-x: center;
  background-repeat: no-repeat;
  background-image: url(https://slack-files2.s3-us-west-2.amazonaws.com/avatars/2017-12-19/288981919427_f45f04edd92902a96859_512.png);
}

.koopera-image {
  background-size: contain;
  background-position-x: center;
  background-repeat: no-repeat;
  background-image: url(/img/icon.png);
}

</style>
