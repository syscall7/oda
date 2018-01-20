<template>
  <div id="app">
    <notifications group="oda" />

    <Navigation></Navigation>

    <router-view/>
  </div>
</template>

<script>
  import Navigation from './components/Navigation'
  import { bus, API_ERROR } from './bus'

  export default {
    name: 'app',
    components: {
      Navigation
    },
    created () {
      let self = this
      bus.$on(API_ERROR, function (error) {
        self.$notify({
          group: 'oda',
          type: 'error',
          title: 'API Error',
          duration: 10000,
          text: `${error.message}.`
        })
      })
    }
  }
</script>

<style>
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
  }

  .error {
    background: #E54D42;
  }
</style>
