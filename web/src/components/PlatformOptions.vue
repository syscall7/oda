<template>
  <form role="form">
    <div class="form-group row">
      <label class="col-sm-3 col-form-label">
        Arch <span ng-show="options.architecture == 'UNKNOWN!'">*</span>
      </label>

      <div class="col-sm-9">
        <select class="input-small form-control"
                v-model="architecture">
          <option v-for="architecture in architectures" v-bind:value="architecture">
            {{architecture}}
          </option>
        </select>
      </div>
    </div>
    <div class="form-group row">
      <label class="col-sm-4 col-form-label">Base Address</label>

      <div class="col-sm-8">
        <div class="input-group">
          <input name="base_address"
                 v-model="baseAddress"
                 type="text" placeholder="0x00000000"
                 class="input-small form-control"
                 ng-disabled="architectureLocked"
          >
          <span class="input-group-addon"><span @click="setBaseAddress()">Apply</span></span>
        </div>
      </div>
    </div>
    <div class="form-group row">
      <label class="col-sm-4 col-form-label">Endian</label>

      <div class="col-sm-8">
        <select class="input-small form-control"
                v-model="endian">
          <option v-for="endian in endians" v-bind:value="endian.name">
            {{endian.name}}
          </option>
        </select>
      </div>
    </div>

    <div v-for="ao in architectureOptions">
      <div v-if="ao.type=='CHOICE'" class="form-group row">
        <label class="col-sm-4 col-form-label">{{ao.name}}</label>

        <div class="col-sm-8">
          <select class="input-small form-control" :value="valueFor(ao)" @change="updateMessage(ao, $event)">
            <option v-for="choice in ao.values" v-bind:value="choice">
              {{choice}}
            </option>
          </select>
        </div>
      </div>
      <div v-else>
        <!-- {{ao}} -->
      </div>
    </div>

  </form>
</template>


<script>
  import {getArchitectureOptions} from '../api/oda'
  import _ from 'lodash'

  export default {
    name: 'PlatformOptions',
    data () {
      return {
        architectureOptions: null,
        architecture: this.binaryOptions.architecture,
        baseAddress: this.binaryOptions.base_address || this.binaryOptions.baseAddress,
        endian: this.binaryOptions.endian,
        selectedOpts: this.binaryOptions.selectedOpts || []
      }
    },
    props: [
      'binaryOptions'
    ],
    watch: {
      binaryOptions () {
        this.architecture = this.binaryOptions.architecture
        this.baseAddress = this.binaryOptions.base_address
        this.endian = this.binaryOptions.endian
        this.selectedOpts = this.binaryOptions.selectedOpts
      },
      async architecture (value) {
        this.architectureOptions = null
        this.$emit('options-updated', {
          architecture: value,
          endian: this.endian,
          baseAddress: parseInt(this.baseAddress),
          selectedOpts: this.selectedOpts
        })

        let options = await getArchitectureOptions(this.architecture)
        this.architectureOptions = options.options
      },
      endian (value) {
        this.$emit('options-updated', {
          architecture: this.architecture,
          endian: value,
          baseAddress: parseInt(this.baseAddress),
          selectedOpts: this.selectedOpts
        })
      }
    },
    methods: {
      setBaseAddress () {
        this.$emit('options-updated', {
          baseAddress: parseInt(this.baseAddress),
          endian: this.endian,
          architecture: this.architecture,
          selectedOpts: this.selectedOpts
        })
      },
      valueFor (ao) {
        let opt = _.find(this.selectedOptsByArchitectureOptions, { name: ao.name })
        if (opt) {
          return opt.selectedOpt
        }
        return 'DEFAULT'
      },
      updateMessage (ao, e) {
        let goodOptions = _.reject(this.selectedOptsByArchitectureOptions, {name: ao.name})
        goodOptions.push({
          name: ao.name,
          selectedOpt: e.target.value
        })
        this.selectedOpts = _(goodOptions).map('selectedOpt').reject((v) => { return v === 'DEFAULT' }).value()

        this.$emit('options-updated', {
          baseAddress: parseInt(this.baseAddress),
          endian: this.endian,
          architecture: this.architecture,
          selectedOpts: this.selectedOpts
        })
      }
    },
    async created () {
      if (this.architecture) {
        let options = await getArchitectureOptions(this.architecture)
        this.architectureOptions = options.options
      }
    },
    computed: {
      architectures () {
        return this.$store.state.architectures
      },
      endians () {
        return this.$store.state.endians
      },
      selectedOptsByArchitectureOptions () {
        const self = this
        return _.map(this.selectedOpts, (opt) => {
          let ao = _.find(self.architectureOptions, (ao) => {
            return _.find(ao.values, (v) => { return v === opt }) /* ao.values.contains(opt) */ //
          })
          return {
            name: ao.name,
            selectedOpt: opt
          }
        })
      }
    }
  }
</script>

<style scoped>

</style>
