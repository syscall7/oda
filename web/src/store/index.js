import Vue from 'vue'
import Vuex from 'vuex'
import * as types from './mutation-types'
import * as actions from './actions'
import _ from 'lodash'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    apiRoot: '',

    user: null,

    architectures: [],
    architectureOptions: [],
    endians: [],

    selectedDu: null,

    projectName: null,
    shortName: null,

    branches: null,
    branchesByAddr: null,

    structTypes: null,

    binary: null,
    revision: 0,
    sections: [],
    parcels: [],
    displayUnitsLength: 0,
    liveMode: false,
    symbols: [],
    functions: [],
    comments: [],
    strings: [],
    binaryOptions: {},
    binaryText: '',
    default_permission_level: null,

    /* First Attempt to store sparse array of DisplayUnits */
    displayUnits: [],
    inAnActiveDuLoad: false,

    activeUsers: [ ]
  },
  mutations: {
    [types.LOAD_ODBFILE] (state, {odbFile, startingDisplayUnits}) {
      state.architectures = odbFile.architectures.sort()
      state.endians = odbFile.endians

      state.user = odbFile.user

      state.sections = odbFile.sections
      state.parcels = odbFile.parcels
      state.projectName = odbFile.project_name
      state.displayUnitsLength = odbFile.displayUnits.size
      state.default_permission_level = odbFile.default_permission_level
      // state.selectedAddress = odbFile.parcels[0].vma_start

      state.binary = odbFile.binary
      state.symbols = odbFile.symbols
      state.strings = odbFile.strings
      state.functions = odbFile.functions
      state.comments = odbFile.comments
      state.liveMode = odbFile.live_mode
      state.displayUnits = Array(state.displayUnitsLength)
      state.binaryOptions = state.binary.options
      state.binaryText = state.binary.text

      state.structTypes = odbFile.structTypes
      state.structFieldTypes = odbFile.structFieldTypes

      _.each(startingDisplayUnits, (du, i) => {
        Vue.set(state.displayUnits, i, du)
      })
    },

    [types.SET_SHORTNAME] (state, {shortName}) {
      state.shortName = shortName
    },

    [types.CACHE_DISPLAYUNITS] (state, {start, displayUnits}) {
      _.each(displayUnits, (du, i) => {
        Vue.set(state.displayUnits, start + i, du)
      })
    },

    [types.SET_SELECTED_DU] (state, {du}) {
      state.selectedDu = du
    },

    [types.SET_BINARYTEXT] (state, {binaryText}) {
      state.binaryText = binaryText
    },

    [types.CLEAR_AND_SET_DISPLAYUNITS] (state, {start, displayUnits}) {
      state.displayUnits.splice(0)
      _.each(displayUnits, (du, i) => {
        Vue.set(state.displayUnits, start + i, du)
      })
    },

    [types.SET_BINARYOPTIONS] (state, {architecture, baseAddress, endian, selectedOpts}) {
      state.binaryOptions.architecture = architecture
      state.binaryOptions.base_address = baseAddress
      state.binaryOptions.endina = endian
      state.binaryOptions.selected_opts = selectedOpts
    },

    [types.SET_PARCELS] (state, {parcels}) {
      state.parcels = parcels
    },

    [types.UPDATE_USER] (state, {user}) {
      state.user = user
    },

    [types.MAKE_COMMENT] (state, {comment, vma}) {
      var index = _.findIndex(state.comments, { vma: vma })
      if (index !== -1) {
        Vue.set(state.comments, index, {
          comment: comment,
          vma: vma
        })
      } else {
        state.comments.push({
          comment: comment,
          vma: vma
        })
      }
    },

    [types.SET_DEFAULT_PERMISSION_LEVEL] (state, {permissionLevel}) {
      state.default_permission_level = permissionLevel
    },

    [types.SET_ACTIVE_USERS] (state, {activeUsers}) {
      state.activeUsers = activeUsers
    },

    [types.UPDATE_USER_POSITION] (state, {username, address}) {
      console.log('UPDATE_USER_POSITION', username, address)
      let user = _.find(state.activeUsers, {username: username})
      if (user) {
        if (user.lastReportedPosition) {
          user.lastReportedPosition.address = address
        } else {
          Vue.set(user, 'lastReportedPosition', {
            username,
            address
          })
        }
      }
    },

    [types.UPDATE_FUNCTION] (state, {vma, name, retval, args}) {
      let index = _.findIndex(state.functions, {vma: vma})
      if (index === -1) {
        console.log('UPDATE_FUNCTION creating', vma, name)
        state.functions.push({ vma, name, retval, args })
      } else {
        let f = state.functions[index]
        console.log('UPDATE_FUNCTION updating', vma, name)
        f.name = name
        f.retval = retval
        f.args = args
        Vue.set(state.functions, index, f)
      }

      let symbol = _.find(state.symbols, {vma: vma})
      if (symbol) {
        symbol.name = name
      }
    },

    [types.ADD_STRUCTURE] (state, {name}) {
      state.structTypes.push({
        fields: [],
        is_packed: true,
        name: name
      })
    },

    [types.SET_BRANCHES] (state, {branches}) {
      state.branches = branches
      state.branchesByAddr = {}

      _.each(branches, (branch, i) => {
        branch.id = i

        if (state.branchesByAddr[branch.srcAddr]) {
          state.branchesByAddr[branch.srcAddr].push(branch)
        } else {
          state.branchesByAddr[branch.srcAddr] = [branch]
        }

        if (state.branchesByAddr[branch.targetAddr]) {
          state.branchesByAddr[branch.targetAddr].push(branch)
        } else {
          state.branchesByAddr[branch.targetAddr] = [branch]
        }
      })
    },

    [types.DELETE_STRUCT] (state, {index}) {
      state.structTypes.splice(index, 1)
    }
  },
  actions: actions,
  getters: {
    isActiveUser: (state) => {
      return state.user && !state.user.is_lazy_user
    },
    functionsByAddress: function (state) {
      return _.keyBy(state.functions, 'vma')
    },
    commentsByAddress: function (state) {
      return _.keyBy(state.comments, 'vma')
    },
    selectedAddress: (state, getters) => {
      if (!state.selectedDu) {
        return 0
      }
      return state.selectedDu.vma
    },
    otherUsers: (state, getters) => {
      return _.reject(state.activeUsers.slice(0, 10), function (user) {
        return user.username === state.user.username
      })
    },
    branchesInRange: (state, getters) => (low, high) => {
      if ((high - low) > 1000) {
        // In cases where we're over a big range, might as well goto filtering branch list
        return _.filter(state.branches, (branch) => {
          if (branch.srcAddr > low && branch.srcAddr < high) {
            return true
          }
          if (branch.targetAddr > low && branch.targetAddr < high) {
            return true
          }
          return false
        })
      }

      const matchingBranches = []
      for (var i = low; i <= high; i++) {
        if (state.branchesByAddr[i]) {
          _.each(state.branchesByAddr[i], (branch) => { matchingBranches.push(branch) })
        }
      }
      const matching = _.uniqBy(matchingBranches, 'id')

      return matching
    },
    dusByRange: (state, getters) => (start, length) => {
      let dus = state.displayUnits.slice(start, start + length)

      for (var i = 0; i < length; i++) {
        if (dus[i] === undefined) {
          Vue.set(dus, i, {dummy: true})
        }
      }

      return dus
    }
  }
})
