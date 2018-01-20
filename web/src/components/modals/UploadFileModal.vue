<template>
  <div>
    <b-modal ref="fileUploadModal" size="lg" @ok="ok" :ok-disabled="!formValid">
      <div slot="modal-title">
        <i class="fa fa-lg fa-upload"></i> Open File
      </div>
      <div class="alert alert-info" role="alert">
        <p>You can upload any kind of binary to disassemble, including ELF, PE, and raw files.
        You can set a default access control on uploaded file, and this can be changed later using the "share" button.</p>
        <p>Currently anonymous upload are allowed. However, <strong>create an account</strong> and log in to enable <strong>private access</strong>
          and <strong>delete capability</strong> to uploaded files</p>
      </div>
      <form v-if="!loading">
        <div class="form-group">
          <b-form-file v-model="file" ref="fileinput" choose-label="Choose File ..." @change="fileSelected"></b-form-file>
        </div>
        <div class="form-group">
          <label for="projectName">Project Name</label>
          <input type="text" class="form-control" id="projectName" v-model="projectName" placeholder="Select a file ...">
        </div>
        <div class="form-group">
          <label for="projectName">Sharing Mode</label>
          <select class="form-control" id="sharingMode" v-model="defaultSharingMode">
            <option value="read">Public Read (Everyone with a link can view)</option>
            <option value="edit">Public Edit (Everyone with a link can edit)</option>
            <option value="none" disabled v-if="!isActiveUser">Private (Only you can view) -- Log In To Enable This Option </option>
            <option value="none" v-if="isActiveUser">Private (Only you can view)</option>
          </select>
        </div>
      </form>
      <div v-if="loading">
        <h2 class="text-info">Loading ...</h2>
        <div style="width:106px; height:94px; display:inline-block; margin-left: 300px;">
          <img src="../../assets/oda.png" style="position:absolute; z-image:0;"/>
          <img src="../../assets/oda.gif" style="position:absolute; z-image:1;"/>
        </div>
      </div>
    </b-modal>
  </div>
</template>

<script>
  import {bus, SHOW_FILE_UPLOAD_MODAL, SHOW_CONFIGURE_FILE_MODAL} from '../../bus'
  import {uploadFile} from '../../api/oda'

  function parseFilename (fullPath) {
    if (fullPath.indexOf('/') > -1) {
      return fullPath.substring(fullPath.lastIndexOf('/') + 1, fullPath.length)
    } else {
      return fullPath.substring(fullPath.lastIndexOf('\\') + 1, fullPath.length)
    }
  }

  export default {
    name: 'UploadFileModal',
    data () {
      return {
        file: null,
        projectName: null,
        defaultSharingMode: 'read',
        loading: false
      }
    },
    computed: {
      formValid () {
        return this.file && this.projectName
      },
      isActiveUser () {
        return this.$store.getters.isActiveUser
      }
    },
    methods: {
      fileSelected (e) {
        const filename = parseFilename(e.target.value)
        this.projectName = filename
        console.log('file selected', e)
      },
      async ok (bvEvt) {
        bvEvt.preventDefault()
        this.loading = true
        var fileInfo = await uploadFile(this.file, this.projectName, this.defaultSharingMode)
        this.$refs.fileUploadModal.hide()
        bus.$emit(SHOW_CONFIGURE_FILE_MODAL, { fileInfo })
      }
    },
    created () {
      const self = this
      bus.$on(SHOW_FILE_UPLOAD_MODAL, function () {
        self.file = null
        self.loading = false
        self.projectName = null
        if (self.$refs.fileinput) {
          self.$refs.fileinput.reset()
        }
        self.$refs.fileUploadModal.show()
      })
    }
  }
</script>
