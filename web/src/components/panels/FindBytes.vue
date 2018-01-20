<template>
  <div>

    <div class="oda-sidebar-title">Find Bytes</div>

    <!-- Find Pattern -->

    <div class="input-group">
      <input id="search-pattern" name="search-pattern" class="form-control"
             placeholder="search pattern" type="text" v-model="bytes"
             @keyup.enter="findBytes()"
      />
      <b-popover target="search-pattern" triggers="focus"
                 placement="bottom" title="Search Pattern"
                 ref="popover"><span v-html="searchHelp"></span></b-popover>

      <div class="input-group-btn">
        <button class="btn btn-primary" @click="findBytes()">Find</button>
      </div>
    </div>


    <div class="sidebar-scroll-container">
      <table class="table table-striped sidebar-table" id="find-results-table">
        <thead>
        <tr>
          <th>Address</th>
          <th>Section</th>
        </tr>
        </thead>
        <tbody class="scrollContent">
        <tr v-for="result in results">
          <td class="result-vma" style="width:1%">
            <span class="clickable" @click="setAddress(result.addr)">0x{{
              result.addr.toString(16) }}</span>
          </td>
          <td class="section" align="left">{{ result.section }}</td>
        </tr>
        </tbody>
      </table>

      <div ng-show="!data.results">
        <em>No results found</em>
      </div>
    </div>
  </div>
</template>

<script>
  import {findBytes} from '../../api/oda'
  import {bus, NAVIGATE_TO_ADDRESS} from '../../bus'

  export default {
    name: 'FindBytes',
    data () {
      return {
        bytes: null,
        results: [],
        searchHelp: 'To search for ASCII strings, use <b>double quotes</b>, as in:<br>' +
            '&nbsp;&nbsp;&nbsp;&nbsp;"this is some long string to find"<br><br>' +
            'To search for a sequnce of hex bytes, use one of the following formats:<br><br>' +
            '&nbsp;&nbsp;&nbsp;&nbsp;00 01 02 03 de ad be ef<br>' +
            '&nbsp;&nbsp;&nbsp;&nbsp;00010203deadbeef<br>'
      }
    },
    computed: {
      filteredStrings: function () {
        return this.symbols
      }
    },
    methods: {
      findBytes: async function () {
        this.results = await findBytes(this.bytes)
      },
      setAddress: function (addr) {
        bus.$emit(NAVIGATE_TO_ADDRESS, { address: addr })
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

  #find-results-table {
    font-size: 0.85rem;
  }

  .table td {
    padding: 3px 8px;
  }
</style>
