<template>
  <div>
    <div class="panel-header">
      Decompiler
      <div style="position: absolute; right: 8px; top: 2px;">
        <button class="btn btn-sm" style="padding: 0.05rem 0.3rem;" @click="hideWindow">
          <i class="fa fa-window-close fa-lg"></i>
        </button>
      </div>
    </div>

    <div v-if="error">
      {{error}}
    </div>

    <div v-if="loading">
      Loading
    </div>

    <div v-else style="position: absolute; overflow: scroll; top: 34px; bottom:0px; left: 0px; right: 0px; font-size:12px;">
      <div v-if="decompiledResults">
        <pre v-highlightjs="decompiledResults.source"><code class="cpp"></code></pre>
      </div>
      <div v-else>
        Select a code address.
      </div>
    </div>
  </div>
</template>

<script>
  import {decompiled} from '../api/oda'
  import {bus, HIDE_DECOMPILER_WINDOW} from '../bus'
  export default {
    name: 'Decompiler',
    data () {
      return {
        decompiledResults: null,
        loading: false,
        error: null
      }
    },
    computed: {
      selectedAddress () {
        return this.$store.getters.selectedAddress
      },
      firstDu () {
        return this.$store.state.displayUnits[0]
      }
    },
    methods: {
      hideWindow () {
        bus.$emit(HIDE_DECOMPILER_WINDOW)
      },
      async load () {
        if (this.loading) {
          return
        }

        if (this.decompiledResults === null ||
          !(this.decompiledResults.start < this.selectedAddress && this.selectedAddress < this.decompiledResults.end)
        ) {
          this.loading = true
          console.log('SETTING DECOMPILED RESULTS')
          try {
            this.decompiledResults = await decompiled(this.selectedAddress)
          } catch (e) {
            if (e) {
              console.log('Decompiler Error', e.response)
              this.error = e.response.data.error
            }
          } finally {
            this.loading = false
          }
        }
      }
    },
    watch: {
      selectedAddress () {
        this.load()
      },
      firstDu () {
        this.load()
      }
    }
  }
</script>

<style scoped>
  .panel-header {
    padding: 4px;
    font-size: 1rem;
    background-color: #ddd;
    border-bottom: 1px solid #444;
  }
</style>

<style>
  .hljs {
    background: white;
  }
</style>
