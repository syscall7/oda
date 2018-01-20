<template>
  <div tabindex="0">
    <div style="position:absolute; right: -10px; top:-10px; z-index:1000" v-if="isLoadingDus">
      <img src="../assets/loading.gif" style="height:64px;">
    </div>
    <div style="position: absolute; right: 10px; top; 20px; z-index:1000; display: none;">
      <div>{{ highlightedAddress | hex }}</div>
      <div>{{ locationStack }}</div>
    </div>
    <div
      class="listing disassembly-viewport"
      style="background-color:#bbb; position: absolute; left: 0; right: 0px; top: 0; bottom: 0; overflow: hidden">

      <div style="position:absolute; top:0px; left:0px; width: 125px; bottom: 0px; z-index:10;">
        <BranchLines :rendered-dus="renderedDus"></BranchLines>
      </div>

      <div v-for="(du, index) in renderedDus"
           style="height:15px;"
           class="display-line"
           @contextmenu.prevent="showContextMenu(index, $event)"
           @click="setSelectedLine(index, $event)"
           v-bind:class="{ 'active-listing-line': index === selectedLine }">
        <div class="cell-branch"></div>
        <div class="listing-contents">
          <table>
            <tr v-if="!du.dummy">
              <td>{{ du.section_name }} </td>
              <td>:{{ du.vma | hex}}</td>
              <td style="padding-left:8px;" class="rawBytes">
                <div style="width:120px; overflow:hidden">{{ du.rawBytes }}</div>
              </td>
              <td><div class="insn" v-html="du.instStr"></div></td>
              <td><div v-if="du.comment" class="comment"> ; {{du.comment}}</div></td>
            </tr>
          </table>
           <!-- : {{ du.vma | hex}} {{ du.rawBytes }} {{ du.comment }} <span v-html="du.instStr"></span> -->
        </div>
      </div>

    </div>

    <div class="disassembly-scroll">
      <div style="overflow:scroll" :style="{height:height+'px'}">
      </div>
    </div>

    <ContextMenu ref="menu">
      <div class="dropdown-menu" aria-labelledby="dropdownMenuButton"  style="display:block;">
        <h6 class="dropdown-header">ODA Commands 0x{{ highlightedAddress | hex }} isCode: {{ highlightedDu.isCode}}</h6>
        <button class="dropdown-item listing-context-menu-item" @click="makeComment()">
          Comment
          <div class="context-menu-key-shortcut">;</div>
        </button>
        <button class="dropdown-item listing-context-menu-item" @click="editFunction()" v-if="highlightedDu.isCode">
          Create/Edit Function
          <div class="context-menu-key-shortcut">t</div>
        </button>
        <button class="dropdown-item listing-context-menu-item" @click="codeToData()"  v-if="highlightedDu.isCode">
          Code -> Data
          <div class="context-menu-key-shortcut">d</div>
        </button>
        <button class="dropdown-item listing-context-menu-item" @click="dataToCode()" v-if="!highlightedDu.isCode">
          Data -> Code
          <div class="context-menu-key-shortcut">c</div>
        </button>
        <button class="dropdown-item listing-context-menu-item" @click="createString()" v-if="!highlightedDu.isCode">
          ASCII String
          <div class="context-menu-key-shortcut">a</div>
        </button>
      </div>
    </ContextMenu>

  </div>
</template>

<script>
  import 'jquery-mousewheel'
  import $ from 'jquery'
  import _ from 'lodash'
  import * as types from '../store/mutation-types'
  import {
    bus,
    EVENT_SCROLLED,
    ADDRESS_AT_TOP_CHANGED,
   // LIVE_ENTRY_CHANGED,
    NAVIGATE_TO_ADDRESS,
    MODAL_HIDDEN,
    SHOW_COMMENT_MODAL,
    SHOW_GOTOADDRESS_MODAL, SHOW_FUNCTION_MODAL, SHOW_DEFINED_DATA_MODAL
  } from '../bus'
  import {Scroller} from '../lib/scroller'
  import {vmaToLda} from '../api/oda'
  import ContextMenu from './ContextMenu'
  import BranchLines from './BranchLines'

  const MAX_CROSSREFS = 20

  let Keypress = require('keypress.js/keypress-2.1.4.min')

  var scroller = null

  function intToHex (value) {
    var stringValue = value.toString(16)
    var s = '000000000' + stringValue
    return s.substr(s.length - 8)
  }

  export default {
    name: 'Listing',
    components: {
      ContextMenu,
      BranchLines
    },
    data () {
      return {
        locationStack: [],
        loading: false,
        height: 100,

        topInstLogicalDuNum: 0,
        vma: 0,

        numLinesShown: 0,
        addressAtTop: null,

        selectedLine: 0,

        isLoadingDus: false
      }
    },
    computed: {
      renderedDus () {
        if (this.numLinesShown === 0) {
          return []
        }

        let duss = this.$store.getters.dusByRange(this.topInstLogicalDuNum, this.numLinesShown)

        let listOfRenderedDus = _.map(duss, (du) => { return this.renderDu(du) })

        // Hack to avoid dealing with live mode (avoid reloading when DUs is less then some max
        if (this.$store.state.displayUnitsLength > 500) {
          for (var i = 0; i < listOfRenderedDus.length; i++) {
            if ((_.some(listOfRenderedDus[i], {dummy: true}))) {
              if (!this.isLoadingDus) {
                this.isLoadingDus = true
                let from = Math.max(0, this.topInstLogicalDuNum - 150)
                this.$store.dispatch('loadDu', {addr: from, units: 500}).then(() => {
                  this.isLoadingDus = false
                })
                break
              }
            }
          }
        }

        let top = listOfRenderedDus[0]
        scroller.setTopInstructionLength(top.length)
        if (top.length > 1) {
          listOfRenderedDus[0] = top.slice(top.length * this.vma)
        }

        let rendered = _.flatten(listOfRenderedDus)

        var topDu = rendered[0]
        if (!topDu.dummy && this.addressAtTop !== topDu.vma) {
          this.addressAtTop = topDu.vma
          bus.$emit(ADDRESS_AT_TOP_CHANGED, topDu.vma)
        }
        return rendered
      },
      highlightedDu () {
        if (!this.renderedDus[this.selectedLine]) {
          return {}
        }
        return this.renderedDus[this.selectedLine]
      },
      highlightedAddress () {
        if (this.highlightedDu) {
          return this.highlightedDu.vma
        }

        return null
      }
    },
    methods: {
      showContextMenu (index, event) {
        this.setSelectedLine(index, event)
        this.$refs.menu.open(event)
      },
      onClick (opt) {
        console.log('Clicked', opt)
      },
      setSelectedLine (index, $event) {
        let isXref = $($event.target).hasClass('xref-location')
        if (isXref) {
          this.locationStack.push(this.highlightedAddress)
          bus.$emit(NAVIGATE_TO_ADDRESS, { address: $($event.target).data('addr') })
        } else {
          this.selectedLine = index
        }
      },
      dataToCode () {
        this.$store.dispatch('dataToCode', { addr: this.highlightedAddress })
      },
      codeToData () {
        this.$store.dispatch('codeToData', { addr: this.highlightedAddress })
      },
      makeComment () {
        console.log('Make Comment')
        bus.$emit(SHOW_COMMENT_MODAL, { addr: this.highlightedAddress })
      },
      gotoAddress () {
        bus.$emit(SHOW_GOTOADDRESS_MODAL)
      },
      editFunction () {
        bus.$emit(SHOW_FUNCTION_MODAL, { addr: this.highlightedAddress })
      },
      createString () {
        this.$store.dispatch('createString', { addr: this.highlightedAddress })
      },
      handleResize () {
        console.log('RESIZEING')
        this.numLinesShown = scroller.numLinesShown()
      },
      makeDefinedData () {
        bus.$emit(SHOW_DEFINED_DATA_MODAL, { addr: this.highlightedAddress })
      },
      undefineData () {
        this.$store.dispatch('undefineData', { addr: this.highlightedAddress })
      },
      renderDu (du) {
        if (du.dummy) {
          return [{dummy: true}]
        }

        let comment = this.$store.getters.commentsByAddress[du.vma]
        let func = this.$store.getters.functionsByAddress[du.vma]

        let k = []

        if (func) {
          k.push({
            section_name: du.section_name,
            isCode: du.isCode,
            vma: du.vma
          }, {
            section_name: du.section_name,
            isCode: du.isCode,
            vma: du.vma,
            instStr: `; =============== F U N C T I O N ====================================`
          })

          // Currently xrefs are dup'ed over vma?
          let uniqCrossRef = _.uniqBy(du.crossRef, 'vma')
          for (var i = 0; (i < uniqCrossRef.length) && (i < MAX_CROSSREFS); i++) {
            k.push({
              section_name: du.section_name,
              isCode: du.isCode,
              vma: du.vma,
              instStr: `; CODE XREF: <span data-addr="${uniqCrossRef[i].vma}" class='xref-location'>0x${intToHex(uniqCrossRef[i].vma)}</span>`
            })
          }
          k.push({
            section_name: du.section_name,
            isCode: du.isCode,
            vma: du.vma
          }, {
            section_name: du.section_name,
            isCode: du.isCode,
            vma: du.vma,
            rawBytes: '',
            instStr: `<span class="function-return">${func.retval}</span> <span class="function-name">${func.name}</span> (${func.args})`
          }, {
            section_name: du.section_name,
            isCode: du.isCode,
            vma: du.vma
          })
        }

        if (du.isBranch) {
          k.push({
            section_name: du.section_name,
            isCode: du.isCode,
            vma: du.vma
          }, {
            section_name: du.section_name,
            isCode: du.isCode,
            vma: du.vma,
            instStr: `<div style="margin-left: -40px;">loc_${intToHex(du.vma)}:</div>`
          }, {
            section_name: du.section_name,
            isCode: du.isCode,
            vma: du.vma,
            comment: _.get(comment, 'comment'),
            instStr: du.instStr
          })
        } else if (du.targetRef) {
          let targetFunction = this.$store.getters.functionsByAddress[du.targetRef.vma]
          let targetName = `loc_${intToHex(du.targetRef.vma)}`
          if (targetFunction) {
            targetName = targetFunction.name
          }

          k.push({
            section_name: du.section_name,
            isCode: du.isCode,
            vma: du.vma,
            rawBytes: du.rawBytes,
            comment: _.get(comment, 'comment'),
            instStr: `${du.instStr} <span data-addr="${du.targetRef.vma}" class="xref-location">${targetName}</span>`
          })
        } else {
          k.push({
            section_name: du.section_name,
            isCode: du.isCode,
            vma: du.vma,
            rawBytes: du.rawBytes,
            comment: _.get(comment, 'comment'),
            instStr: du.instStr
          })
        }

        return k
      }
    },
    created: async function () {
      let self = this

      bus.$on(NAVIGATE_TO_ADDRESS, async function (event) {
        console.log('NAVIGATE_TO_ADDRESS', event.address.toString(16), event.lda)
        var lda = event.lda
        if (lda === undefined) {
          lda = await vmaToLda(event.address)
        }

        self.topInstLogicalDuNum = lda
        self.vma = 0

        scroller.setTop(self.topInstLogicalDuNum)

        self.selectedLine = 0
      })

      bus.$on(MODAL_HIDDEN, function () {
        self.$el.focus()
      })
    },
    watch: {
      highlightedDu (du) {
        if (!du.dummy) {
          this.$store.commit(types.SET_SELECTED_DU, { du })
        }
      }
    },
    mounted: function (elem) {
      window.addEventListener('resize', _.debounce(this.handleResize, 250))

      var self = this
      var listener = new Keypress.Listener(this.$el)

      listener.simple_combo('down', function () {
        if (self.selectedLine + 8 > self.numLinesShown) {
          self.topInstLogicalDuNum += 1
          self.vma = 0
        } else {
          self.selectedLine += 1
        }
      })

      listener.simple_combo('c', () => {
        self.dataToCode()
      })

      listener.simple_combo('d', () => {
        self.codeToData()
      })

      listener.simple_combo(';', () => {
        self.makeComment()
      })

      listener.simple_combo('g', () => {
        self.gotoAddress()
      })

      listener.simple_combo('t', () => {
        self.editFunction()
      })

      listener.simple_combo('a', () => {
        self.createString()
      })

      listener.simple_combo('u', () => {
        self.undefineData()
      })

      listener.simple_combo('v', () => {
        self.makeDefinedData()
      })

      listener.simple_combo('up', function () {
        if (self.selectedLine - 6 < 0) {
          self.topInstLogicalDuNum -= 1
          self.vma = 0
        } else {
          self.selectedLine -= 1
        }
      })

      listener.simple_combo('esc', function () {
        if (self.locationStack.length > 0) {
          var location = self.locationStack.pop()
          bus.$emit(NAVIGATE_TO_ADDRESS, { address: location })
        }
      })

      var lines = this.$store.state.displayUnitsLength
      var viewportLineHeight = 15
      var scrollLineHeight = viewportLineHeight * 1.0
      this.height = lines * viewportLineHeight
      scroller = new Scroller(viewportLineHeight)

      this.numLinesShown = scroller.numLinesShown()
      bus.$on(EVENT_SCROLLED, _.debounce((data) => {
        var fractionalScrollInLines = data.scrollTop / scrollLineHeight
        self.topInstLogicalDuNum = Math.floor(fractionalScrollInLines)
        self.vma = fractionalScrollInLines % 1
      }, 5))
    }
  }
</script>


<style scoped>
  .disassembly-scroll {
    position: absolute;
    background-color: rgba(255, 255, 255, 0.2);
    top: 0px;
    right: 0px;
    bottom: 0px;
    width: 14px;
    overflow: scroll;
  }

  .listing {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
    font-size: 14px;
    background-color: white;
  }

  .display-line {
    background-color: white;
    line-height: 15px;
  }

  .cell-branch {
    color: #093C83;
    background-color: #f3f3f3;
    font-family: DejaVuSansMono;
    text-align: right;
    height: 15px;
    width: 125px;
    left: 0px;
    position: absolute;
  }

  .section {
    position: absolute;
    left: 125px;
    width: 140px;
    text-align: right;
    white-space: nowrap;
    overflow: hidden;
  }

  .vma {
    position: absolute;
    left: 265px;
    width: 100px;
  }

  .rawBytes {
    color: gray;
    overflow: hidden;
  }

  .instStr {
    position: absolute;
    left: 500px;
    width: 2000px;
    color: gray;
  }

  .listing-contents {
    position: absolute;
    width:1800px;
    left: 125px;
  }



</style>

<style>

  .listing-context-menu-item {
    margin-right: 20px;
    position: relative;
  }

  .context-menu-key-shortcut {
    position: absolute;
    right: 10px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
    font-size: 80%;
    top: 5px;
    margin-left: 8px;
    padding: 2px 8px 2px 8px;
    background: -moz-linear-gradient(-90deg, white 0%, #e3e3e3 100%) repeat scroll 0 0 white;
    border: 1px solid #aaa;
    border-radius: 3px;
  }

  .instruction {
    color: #093C83;
  }

  .comment {
    color: #009933;
    white-space: nowrap;
  }

  .function-return {
    font-style: italic;
  }

  .function-name {
    font-weight: bold;
  }

  .insn {
    color: #093c83;
  }

  .xref-location {
    /* http://stackoverflow.com/questions/20376008/how-to-underline-text-and-change-mouse-cursor-to-pointer-in-ace-editor */
    /* border-bottom: 1px solid black; */
    font-weight: bold;
    color: #08c;
    cursor: pointer !important;
    pointer-events: auto;
  }

  .xref-location:hover {
    /* http://stackoverflow.com/questions/20376008/how-to-underline-text-and-change-mouse-cursor-to-pointer-in-ace-editor */
    /* border-bottom: 1px solid black; */
    color: #005580;
    text-decoration: underline;
  }

  .active-listing-line {
    background-color: #FFB !important;
  }

  .active-listing-line div {
    background-color: #FFB !important;
  }

</style>
