<template>
  <div>
    <b-modal ref="gotoAddressModal" size="lg" @ok="ok" title="Goto Address" no-fade @hidden="onHidden">
      <div class="form-group">
        <label for="gotoAddressInput">Goto an Address/Symbol Name</label>
        <div class="dropdown">
        <input ref="inputField" type="text"
               v-on:keyup.enter="ok"
               class="form-control"
               id="gotoAddressInput"
               placeholder="Address ..."
               v-model="address">
          <div class="dropdown-menu" aria-labelledby="dropdownMenu2" style="display:block; width: 100%;"
               v-if="autocompleteItems.length > 0">
            <button class="dropdown-item"
                    type="button"
                    @click="setSymbol(symbol)"
                    v-for="symbol in autocompleteItems">
              {{symbol.name}} <small class="symbol-address">0x{{symbol.vma | hex}}</small>
            </button>
          </div>
        </div>

      </div>
    </b-modal>
  </div>
</template>

<script>
  import {bus, SHOW_GOTOADDRESS_MODAL, MODAL_HIDDEN, NAVIGATE_TO_ADDRESS} from '../../bus'
  import _ from 'lodash'

  export default {
    name: 'GotoAddressModal',
    data () {
      return {
        address: null
      }
    },
    methods: {
      onHidden () {
        bus.$emit(MODAL_HIDDEN)
      },
      setSymbol (symbol) {
        this.address = symbol.name
        this.ok()
      },
      ok () {
        let symbolName = _.find(this.$store.state.symbols, { name: this.address })
        if (symbolName) {
          bus.$emit(NAVIGATE_TO_ADDRESS, { address: symbolName.vma })
        } else {
          bus.$emit(NAVIGATE_TO_ADDRESS, { address: parseInt(this.address, 16) })
        }
        this.$refs.gotoAddressModal.hide()
      }
    },
    computed: {
      autocompleteItems () {
        if (!this.address || this.address.length === 0) {
          return []
        }
        return _.filter(this.$store.state.symbols, (symbol) => {
          return symbol.name.indexOf(this.address) !== -1
        }).slice(0, 10)
      }
    },
    created () {
      bus.$on(SHOW_GOTOADDRESS_MODAL, (event) => {
        this.address = null
        this.$refs.gotoAddressModal.show()

        setTimeout(() => {
          this.$refs.inputField.focus()
        }, 1)
      })
    }
  }
</script>

<style scoped>
  .symbol-address {
    color: #adadad;
  }
</style>
