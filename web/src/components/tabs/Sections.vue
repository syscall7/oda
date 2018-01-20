<template>
  <div class="container" style="padding:8px">
    <table class="sections-table" style="min-width:750px; font-size:14px;">
      <tbody>
      <tr>
        <th>Name</th>
        <th>Size</th>
        <th>VMA</th>
        <th>Flags</th>
        <th>Alignment</th>
      </tr>

      <tr class="even" v-for="section in sections">
        <td><span class="clickable" @click="setSection(section)">{{ section.name }}</span></td>
        <td align="right">{{ section.size }} bytes</td>
        <td
          align="right"
          style="font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;"
          class="clickable"
          @click="setSection(section)">0x{{ section.vma | hex }}</td>
        <td align="left">
                <span v-for="flag in section.flags"
                      v-bind:class="['badge', 'badge-pill', getFlagLabel(flag)]"
                      v-b-popover.hover="flag.desc" :title="flag.name"
                      placement="top"
                      style="margin-right:5px;">
                     {{ getFlagText(flag.name) }}
                                    </span>
        </td>
        <td align="right">2<sup>0</sup></td>
      </tr>

      </tbody>
    </table>
  </div>
</template>

<script>
  import Vue from 'vue'
  import {mapState} from 'vuex'
  import {bus, NAVIGATE_TO_ADDRESS, OPEN_LISTING_TAB} from '../../bus'

  var labels = ['badge-primary', 'badge-success', 'badge-danger', 'badge-warning', 'badge-info', 'badge-secondary']
  var labelIndex = 0
  var flagLabelMap = []
  function getFlagLabel (flag) {
    var label

    if (flagLabelMap[flag] === undefined) {
      flagLabelMap[flag] = labels[labelIndex]
      labelIndex = (labelIndex + 1) % labels.length
    }

    label = flagLabelMap[flag]

    return label
  }

  export default {
    name: 'Sections',
    data () {
      return {}
    },
    methods: {
      getFlagText: function (flag) {
        var s = flag.split('_')
        return s[s.length - 1]
      },
      getFlagLabel (flag) {
        return getFlagLabel(flag.name)
      },
      setSection: function (section) {
        bus.$emit(OPEN_LISTING_TAB)
        Vue.nextTick()
          .then(function () {
            bus.$emit(NAVIGATE_TO_ADDRESS, { address: section.vma })
          })
      }

    },
    computed: mapState(['projectName', 'binary', 'sections'])
  }
</script>

<style scope>
  .clickable {
    color: #0088CC;
    text-decoration: none;
    cursor: pointer;
  }

  .clickable:hover {
    text-decoration: underline;
  }

  .sections-table td, .sections-table th
  {
    padding:3px 10px 3px 10px;
  }

  .sections-table th
  {
    background-color:#92C1F0;
  }

  .sections-table tr.odd td
  {
    background-color:#C8DEFF;
  }
</style>

