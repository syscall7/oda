<template>
  <div>
    <b-modal ref="configureUploadModal" size="lg"
             :ok-disabled='!formValid' @ok="ok" title="Configure File Upload">
      <div v-if="loading">
        <div class="card bg-light mb-3">
          <div class="card-body">
            <h5 class="card-title"><i class="fa fa-spinner fa-spin"></i> Processing Your File Upload ...</h5>
            <p class="card-text">Processing files can take a minute, <strong>especially for ida imports</strong>.
              You'll be redirected once the import is complete. </p>
          </div>
        </div>
      </div>
      <div v-else>
        <div v-if="binaryOptions">

          <div class="alert alert-success">
            ODA detected the object file format as {{ fileData.target }}:
            <ul>
              <li v-for="f in fileData.file_format">{{ f }}</li>
            </ul>
            <br>
            Please select from the platform options below:
          </div>

          <PlatformOptions :binary-options="binaryOptions"
                           @options-updated="optionsUpdated($event)"></PlatformOptions>
        </div>
      </div>
    </b-modal>
  </div>
</template>

<script>
  import {bus, SHOW_CONFIGURE_FILE_MODAL} from '../../bus'
  import PlatformOptions from '../PlatformOptions'
  import {setBinaryOptions} from '../../api/oda'

  export default {
    name: 'ConfigureUploadModal',
    data () {
      return {
        loading: false,
        binaryOptions: null,
        fileData: null
      }
    },
    methods: {
      async ok (e) {
        this.loading = true
        e.preventDefault()

        await setBinaryOptions(
          this.binaryOptions.architecture,
          this.binaryOptions.baseAddress,
          this.binaryOptions.endian,
          this.binaryOptions.selectedOpts,
          this.fileData.short_name)

        this.$refs.configureUploadModal.hide()
        this.$router.push({path: `/odaweb/${this.fileData.short_name}`})
        this.loading = false
      },
      optionsUpdated (options) {
        this.binaryOptions = options
      }
    },
    computed: {
      formValid () {
        if (this.loading) {
          return false
        }
        return this.binaryOptions && this.binaryOptions.architecture && this.binaryOptions.architecture !== 'UNKNOWN!'
      }
    },
    created () {
      const self = this
      bus.$on(SHOW_CONFIGURE_FILE_MODAL, function (options) {
        this.binaryOptions = null
        this.fileData = null

        console.log(SHOW_CONFIGURE_FILE_MODAL, options)
        self.fileData = options.fileInfo
        self.binaryOptions = {
          architecture: options.fileInfo.arch,
          baseAddress: 0,
          endian: 'DEFAULT',
          selectedOpts: []
        }
        self.$refs.configureUploadModal.show()
      })
    },
    components: {
      PlatformOptions
    }
  }
</script>
