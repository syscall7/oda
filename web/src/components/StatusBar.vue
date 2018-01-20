<template>
  <div class="status-bar">
    [normal] ONLINE DISASSEMBLER 4EVER!
    <div style="position:absolute; right: 10px; top:2px;">
      | {{ projectName }} : {{ binary.options.architecture }} ({{ binary.size | prettyBytes }})
      | 0x{{ selectedAddress | hex }}
    </div>
  </div>
</template>

<script>
  export default {
    name: 'StatusBar',
    data () {
      return {
      }
    },
    computed: {
      projectName: function () {
        return this.$store.state.projectName
      },
      binary: function () {
        return this.$store.state.binary
      },
      selectedAddress: function () {
        return this.$store.getters.selectedAddress
      }
    }
  }
</script>

<style scoped>
  .status-bar {
    padding-top:2px;
    padding-left: 4px;
    position: absolute;
    bottom: 0px;
    height: 20px;
    left: 0px;
    right: 0px;
    background-color: rgb(245, 245, 245);
    color: gray;
    font-size: 12px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  }
</style>
