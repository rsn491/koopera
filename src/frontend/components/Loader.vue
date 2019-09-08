<template>
  <div v-bind:class="show ? 'd-flex justify-content-center' : 'd-none'">
    <div class='spinner-border color-dark'/>
  </div>
</template>

<script>

export default {
  name: 'Loader',
  props: {
    show: Boolean,
  },
};

</script>
