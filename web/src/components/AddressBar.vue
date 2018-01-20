<template>
  <div>
    <div id="slider" style="margin-top:0px; margin-bottom: 0px; margin-left: 10px; margin-right: 10px; border: 0px; clear:both;">
      <canvas id="addr-bar-canvas">You need to upgrade your browser or enable javascript to view this site!</canvas>
    </div>

    <!-- <div style="position: fixed; bottom: 100px; left: 10px; color:white; background-color: black; z-index:1000;">
      <h1>OTHER SUERS</h1>
      <div v-for="user in otherUsers">
        {{user}}
      </div>
    </div>
    -->
  </div>
</template>

<script>
  import _ from 'lodash'
  import {AddressNavBar} from '../lib/addrbar'
  import {bus, ADDRESS_AT_TOP_CHANGED, NAVIGATE_TO_ADDRESS} from '../bus'

  export default {
    name: 'AddressBar',
    data () {
      return {
        addressNavBar: null
      }
    },
    computed: {
      parcels () {
        return this.$store.state.parcels
      },
      otherUsers () {
        return this.$store.getters.otherUsers
      }
    },
    watch: {
      parcels (parcels) {
        this.addressNavBar.setParcels(parcels)
      },
      otherUsers: {
        handler (otherUsers) {
          console.log('ACTIVE USERS CHANGED', otherUsers)
          let self = this
          this.addressNavBar.clearUsers()
          _.each(otherUsers, (otherUser) => {
            self.addressNavBar.addUser(otherUser.username)
            if (otherUser.lastReportedPosition) {
              self.addressNavBar.updateUser(otherUser.username, otherUser.lastReportedPosition.address)
            }
          })
        },
        deep: true
      }
    },
    mounted: function () {
      var self = this
      this.addressNavBar = new AddressNavBar('#addr-bar-canvas', this.$store.state.sections, this.parcels)
      this.addressNavBar.onChange(function (address) {
        bus.$emit(NAVIGATE_TO_ADDRESS, { address: address })
      })

      bus.$on(ADDRESS_AT_TOP_CHANGED, function (address) {
        self.addressNavBar.setAddress(address)
      })
    }
  }
</script>

<style scoped>

</style>


