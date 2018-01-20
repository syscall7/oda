<template>
  <div class="sidebar-content" id="hex-sidebar-scroll">
    <div class="oda-sidebar-title">Live View</div>

    <div class="alert alert-info">
      Set the platform below. Then watch the disassembly window update as you type hex bytes in the
      text area. You can also upload an ELF, PE, COFF, Mach-O, or other executable file from the <em>File</em> menu.
    </div>

    <div class="accordion" id="accordion3" style="padding-bottom:10px">
      <button id="platform-btn" type="button" class="btn btn-small btn-danger" @click="toggleOptionsView()">
        Platform: <span class="platform-option">{{ binaryOptions.architecture }}</span>
      </button>
      <div style="border: 1px solid #e5e5e5; border-radius: 5px; margin-top: 10px; width:95%;padding: 10px;" v-if="showBinaryOptions">
        <PlatformOptions
          :binary-options="binaryOptions"
          @options-updated="optionsUpdated($event)"></PlatformOptions>
      </div>
    </div>

    <div class="alert alert-warning" id="hex-alert" v-if="entryError">
      <button type="button" class="close" data-dismiss="alert">&times;</button>
      <strong>Warning!</strong> You can only disassemble hexadecimal characters, check your inputs.
    </div>

    <textarea class="sidebar-scroll-container-text form-control" id="hex"
              style="width:95%; margin-bottom: 5px; height:275px;"
              v-model="binaryText"></textarea>
  </div>
</template>


<script>
  import {mapState} from 'vuex'
  import _ from 'lodash'
  import PlatformOptions from '../PlatformOptions'
  import {bus, LIVE_ENTRY_CHANGED} from '../../bus'

  export default {
    name: 'LiveEntry',
    data () {
      return {
        binaryText: null,
        entryError: false,
        showBinaryOptions: false
      }
    },
    computed: mapState(['architectures', 'binaryOptions']),
    created: function () {
      this.binaryText = this.$store.state.binaryText
    },
    watch: {
      binaryText: _.debounce(async function (newValue, oldValue) {
        if (oldValue != null) {
          try {
            await this.$store.dispatch('setBinaryText', {binaryText: this.binaryText})
            this.entryError = false
            bus.$emit(LIVE_ENTRY_CHANGED)
          } catch (e) {
            this.entryError = true
          }
        }
      }, 500)
    },
    components: {
      PlatformOptions
    },
    methods: {
      toggleOptionsView () {
        this.showBinaryOptions = !this.showBinaryOptions
      },
      async optionsUpdated (options) {
        await this.$store.dispatch('setBinaryOptions', options)
        bus.$emit(LIVE_ENTRY_CHANGED)
        console.log('optionsUpdated', options)
      }
    }
  }
</script>


<style scoped>
  .sidebar-content {
    padding: 10px;
  }

  .oda-sidebar-title {
    font-size: 16px;
    font-weight: bold;
    border-bottom: 2px solid #ddd;
    margin-bottom: 10px;
  }
</style>
