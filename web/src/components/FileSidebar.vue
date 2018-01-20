<template>
  <div>
    <div
      style="position:absolute; left:0px; width: 41px; top: 0px; bottom: 0px; background-color: whiteSmoke; border-right: 1px solid #222;">
      <ul class="icon-list">
        <li><a
          @click="setSelectedPanel('symbols')"
          v-bind:class="{ 'active-link': selectedPanel == 'symbols' }">
          <i class="fa fa-list"></i>
        </a></li>
        <li><a @click="setSelectedPanel('strings')"
               v-bind:class="{ 'active-link': selectedPanel == 'strings' }">
          <i class="fa fa-font"></i>
        </a></li>
        <li><a
          @click="setSelectedPanel('findBytes')"
          v-bind:class="{ 'active-link': selectedPanel == 'findBytes' }">
          <i class="fa fa-search"></i>
        </a></li>
        <li><a @click="setSelectedPanel('structures')"
               v-bind:class="{ 'active-link': selectedPanel == 'structures' }">
          <i class="fa fa-text-width"></i>
        </a></li>

        <li><a @click="setSelectedPanel('operations')"
               v-bind:class="{ 'active-link': selectedPanel == 'operations' }">
          <i class="fa fa-code-fork"></i>
        </a></li>
      </ul>
    </div>

    <div style="position: absolute; left: 41px; right: 0px; top: 0px; bottom: 0px; padding: 10px; overflow:scroll;">
      <div v-if="selectedPanel == 'symbols'">
        <Symbols></Symbols>
      </div>
      <div v-if="selectedPanel == 'strings'">
        <Strings></Strings>
      </div>
      <div v-if="selectedPanel == 'findBytes'">
        <FindBytes></FindBytes>
      </div>
      <div v-if="selectedPanel == 'structures'">
        <Structures></Structures>
      </div>
      <div v-if="selectedPanel == 'operations'">
        <Operations></Operations>
      </div>
    </div>
  </div>
</template>

<script>
  import {bus, CLOSE_SIDEBAR, SHOW_FINDBYTES_PANEL, SHOW_STRINGS_PANEL, SHOW_SYMBOLS_PANEL} from '../bus'
  import Symbols from './panels/Symbols'
  import Strings from './panels/Strings'
  import FindBytes from './panels/FindBytes'
  import Structures from './panels/Structures'
  import Operations from './panels/Operations'

  export default {
    name: 'FileSidebar',
    data () {
      return {
        selectedPanel: 'symbols'
      }
    },
    methods: {
      setSelectedPanel (panel) {
        if (panel === this.selectedPanel) {
          bus.$emit(CLOSE_SIDEBAR)
        } else {
          this.selectedPanel = panel
        }
      }
    },
    components: {
      Symbols, Strings, FindBytes, Structures, Operations
    },
    created () {
      bus.$on(SHOW_FINDBYTES_PANEL, () => {
        this.selectedPanel = 'findBytes'
      })
      bus.$on(SHOW_STRINGS_PANEL, () => {
        this.selectedPanel = 'strings'
      })
      bus.$on(SHOW_SYMBOLS_PANEL, () => {
        this.selectedPanel = 'symbols'
      })
    }
  }
</script>

<style scoped>
  .icon-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  .icon-list li {
    text-align: center;
    font-size: 16px;
    position: relative;
    margin: 0px;
    padding: 0px;
  }

  .icon-list li a {
    display: inline-block;
    width: 40px;
    height: 40px;
    line-height: 40px;
    vertical-align: center;
    color: #999;
    text-decoration: none;
    font-size: 20px;
    padding: 0;
  }

  .active-link {
    text-shadow: rgba(0, 0, 0, 0.2) 0px -1px 0px !important;
    background-color: rgb(0, 92, 230) !important;
    color: white !important;
  }

  > > > .oda-sidebar-title {
    font-size: 16px;
    font-weight: bold;
    border-bottom: 2px solid #ddd;
    margin-bottom: 10px;
  }
</style>
