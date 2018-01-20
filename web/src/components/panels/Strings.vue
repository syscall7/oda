<template>
  <div>
    <div class="oda-sidebar-title">Strings</div>
    <div class="input-group">
      <span class="input-group-addon">Filter</span>
      <input type="text" class="form-control" placeholder="Substring" v-model="filterValue">
    </div>
    <div class="sidebar-scroll-container" style="position:absolute; top:80px; bottom: 0px; left: 0px; right: 0px; overflow: scroll;">
      <table class="table table-striped sidebar-table table-condensed" id="strings-table">
        <thead>
        <tr>
          <th class="col-sm-4" style="width:1%">Address</th>
          <th class="col-sm-4" style="text-align: left; width:100%">String</th>
        </tr>
        </thead>
        <tbody class="scrollContent">
        <tr v-for="string in filteredStrings">
          <td class="str-vma" style="width:1%">
                            <span class="clickable"
                                  @click="setAddress(string)">0x{{ string.addr.toString(16) }}</span>
          </td>
          <td class="string" style="text-align: left; width:100%">{{ string.string }}</td>
        </tr>
        </tbody>
      </table>

      <div v-if="filteredStrings.length == 0">
        <em>No strings found</em>
      </div>
    </div>
  </div>
</template>
<script>
  import _ from 'lodash'
  import {bus, NAVIGATE_TO_ADDRESS} from '../../bus'

  export default {
    name: 'Strings',
    data () {
      return {
        filterValue: null
      }
    },
    computed: {
      filteredStrings: function () {
        let ordered = _(this.$store.state.strings).sortBy('vma')
        if (this.filterValue) {
          let filterValue = this.filterValue
          ordered = ordered.filter(function (symbol) {
            return symbol.string.toLowerCase().indexOf(filterValue.toLowerCase()) !== -1
          })
        }
        return ordered.value()
      }
    },
    methods: {
      setAddress: function (symbol) {
        bus.$emit(NAVIGATE_TO_ADDRESS, { address: symbol.addr })
      }
    }
  }
</script>

<style scoped>
  .clickable {
    color: #0088CC;
    text-decoration: none;
    cursor: pointer;
  }

  .clickable:hover {
    text-decoration: underline;
  }

  #strings-table {
    font-size: 0.85rem;
  }

  .table td {
    padding: 3px 8px;
  }
</style>
