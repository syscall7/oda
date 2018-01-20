<template>
  <div class="split-box">
    <div
      v-if="mode=='left'"
      @mousemove="dragMove"
      @mouseup="dragEnd"
      @mouseleave="dragEnd">
      <div :style="{ width: split + 'px' }"
           style="position: absolute; width: 349px; min-width: 36px; display: block; left: 0px; top: 0px; bottom: 0px; overflow:hidden">
        <div style="height:100%; overflow:scroll;">
          <slot name="left"></slot>
        </div>
      </div>
      <div :style="{ left: split + 'px' }"
           @mousedown.prevent="dragStart($event, 'left')"
           class="splitter vertical w-resize splitterRealtime"
           style="width: 1px; left: 349px; top: 0px; bottom: 0px; position: absolute; z-index:500;">
        <div> </div>
      </div>
      <div :style="{ left: split + 'px', right: splitRight + 'px' }"
           style="position: absolute; left: 349px; top: 0px; bottom: 0px;">
        <div style="position: absolute; left:0; right:0; top:0; bottom:0;">
          <slot name="center"></slot>
        </div>
      </div>

      <div :style="{ right: splitRight + 'px' }"
           @mousedown.prevent="dragStart($event, 'right')"
           class="splitter vertical w-resize splitterRealtime"
           v-if="splitRight > 0"
           style="width: 1px; right: 349px; top: 0px; bottom: 0px; position: absolute; z-index:500;">
        <div></div>
      </div>

      <div :style="{ width: splitRight +'px'}"
           v-if="splitRight > 0"
           style="position:absolute; top:0px; bottom: 0px; right: 0px;">
        <slot name="right"></slot>
      </div>
    </div>
  </div>
</template>

<script>
  import {bus, CLOSE_SIDEBAR, SHOW_DECOMPILER_WINDOW, HIDE_DECOMPILER_WINDOW} from '../bus'

  export default {
    name: 'HelloWorld',
    data () {
      return {
        mode: 'left',
        startX: 0,
        minSplit: 20,
        dragging: false,
        split: parseInt(this.splitX),
        splitRight: 0
      }
    },
    props: ['splitX'],
    methods: {
      dragStart (e, side) {
        this.dragging = side
        this.startX = e.pageX
        if (side === 'left') {
          this.startSplit = this.split
        } else if (side === 'right') {
          this.startSplit = this.splitRight
        }
      },
      dragMove (e) {
        if (this.dragging === 'left') {
          const dx = e.pageX - this.startX

          if ((this.startSplit + dx) < this.minSplit) {
            this.split = this.minSplit
          } else {
            this.split = this.startSplit + dx
          }
        } else if (this.dragging === 'right') {
          const dx = e.pageX - this.startX

          if ((this.startSplit - dx) < this.minSplit) {
            this.splitRight = this.minSplit
          } else {
            this.splitRight = this.startSplit - dx
          }
        }
      },
      dragEnd () {
        this.dragging = false
      }
    },
    created: function () {
      let self = this
      bus.$on(CLOSE_SIDEBAR, function (data) {
        if (self.split !== 40) {
          self.split = 40
        } else {
          self.split = parseInt(self.splitX)
        }
      })

      bus.$on(SHOW_DECOMPILER_WINDOW, function (data) {
        self.splitRight = 300
      })

      bus.$on(HIDE_DECOMPILER_WINDOW, (data) => {
        self.splitRight = 0
      })
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .w-resize {
    cursor: ew-resize;
  }
  .splitter.vertical div {
    width: 3px;
    margin-left: -3px;
    background-color: #eee;
    height: 100%;
  }
</style>

