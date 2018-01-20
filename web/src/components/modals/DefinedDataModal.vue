<template>
  <div>
    <b-modal ref="definedDataModal" size="lg" @ok="ok" title="Create Struct Variable" no-fade @hidden="onHidden">
      <div class="form-group">
        <label for="varName">Create Variable at  0x{{address | hex}}</label>
        <input ref="varName" type="text"
               v-on:keyup.enter="ok"
               class="form-control"
               id="varName"
               placeholder=""
               v-model="varName">
      </div>

      <div class="form-group">
        <label for="fieldType">Select Variable Type</label>
        <select id="fieldType" class="form-control" v-model="dataType">
          <option v-for="structType in structTypes">{{ structType.name }}</option>
        </select>
      </div>
    </b-modal>
  </div>
</template>

<script>
  import {bus, SHOW_DEFINED_DATA_MODAL, MODAL_HIDDEN} from '../../bus'

  export default {
    name: 'DefinedDataModal',
    data () {
      return {
        address: null,
        varName: 'StructVarName',
        dataType: null
      }
    },
    methods: {
      onHidden () {
        bus.$emit(MODAL_HIDDEN)
      },
      ok () {
        this.$store.dispatch('createStructDefinedData', {
          structName: this.dataType,
          varName: this.varName,
          addr: this.address
        })
      }
    },
    computed: {
      structTypes () {
        return this.$store.state.structTypes
      }
    },
    created () {
      bus.$on(SHOW_DEFINED_DATA_MODAL, (event) => {
        this.address = event.addr
        this.$refs.definedDataModal.show()
        /* if (self.$store.getters.commentsByAddress[self.address]) {
          self.comment = self.$store.getters.commentsByAddress[self.address].comment
        } else {
          self.comment = ''
        }
        self.$refs.commentModal.show()
        setTimeout(() => {
          self.$refs.inputField.setSelectionRange(0, self.comment.length)
          self.$refs.inputField.focus()
        }, 1)  */
      })
    }
  }
</script>

<style scoped></style>

