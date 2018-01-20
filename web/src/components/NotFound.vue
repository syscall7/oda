<template>
  <div style="position:absolute; top:38px; bottom: 0; left: 0; right: 0;" class="cover-container">
  <div class="cover-container d-flex h-100 p-3 mx-auto flex-column text-center">
    <main role="main" class="inner cover">
      <h1 class="cover-heading">404</h1>
      <p class="lead">This page could not be found? Are you sure you're in the right place?</p>

    </main>
  </div>
  </div>
</template>

<script>
  export default {
    data () {
      return {}
    }
  }
</script>

<style scoped>
  .cover-heading {
    font-size: 10rem;
  }

  .lead {
    font-size: 2rem;
  }

  .cover-container {
    background-color: #173352;
    color: #f5f5f5;
  }
</style>
