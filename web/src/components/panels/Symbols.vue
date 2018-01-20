<template>
  <div>
    <div id="sidebar-label-symbols" class="oda-sidebar-title">Symbols</div>
    <div class="input-group">
      <span class="input-group-addon">Filter</span>
      <input type="text" class="form-control" placeholder="Substring" v-model="filterValue">
    </div>
    <div class="sidebar-scroll-container" style="position:absolute; top:80px; bottom: 0px; left: 0px; right: 0px; overflow: scroll;">
      <table class="table table-striped sidebar-table table-condensed" id="symbol-table">
        <thead>
        <tr>
          <th class="col-sm-4" style="width:1%">Address</th>
          <th class="col-sm-4" style="width:1%">Type</th>
          <th class="col-sm-4" style="width:100%; text-align: left;">Name</th>
        </tr>
        </thead>
        <tbody class="scrollContent">
        <tr v-for="symbol in filteredSymbols">
          <td style="width:1%">0x{{symbol.vma.toString(16)}}</td>
          <td style="width:1%">{{symbol.type}}</td>
          <td style="width:100%; text-align: left;">
            <span v-if="symbol.vma!==0" class="clickable"
                  @click="setAddress(symbol)">{{symbol.name}}</span>
            <span v-else>{{symbol.name}}</span>
          </td>
        </tr>
        </tbody>
      </table>

      <div v-if="filteredSymbols.length === 0">
        <em>No symbols availables</em>
      </div>
    </div>
  </div>
</template>


<script>
  import _ from 'lodash'
  import {bus, NAVIGATE_TO_ADDRESS} from '../../bus'

  export default {
    name: 'Symbols',
    data () {
      return {
        filterValue: null
      }
    },
    computed: {
      filteredSymbols: function () {
        let ordered = _(this.$store.state.symbols).sortBy('vma')
        if (this.filterValue) {
          let filterValue = this.filterValue
          ordered = ordered.filter(function (symbol) {
            return symbol.name.toLowerCase().indexOf(filterValue.toLowerCase()) !== -1
          })
        }
        return ordered.value()
      }
    },
    methods: {
      setAddress: function (symbol) {
        bus.$emit(NAVIGATE_TO_ADDRESS, { address: symbol.vma })
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

  #symbol-table {
    font-size: 0.85rem;
  }

  .table td {
    padding: 3px 8px;
  }
</style>
