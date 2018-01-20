import * as api from '../api/oda'
import * as auth from '../api/auth'

import {Realtime} from '../realtime'
import _ from 'lodash'
import Q from 'q'
import * as types from './mutation-types'

var realtime = null

function sendRealtimeUpdate (msg, payload) {
  if (realtime) {
    realtime.emit(msg, payload)
  }
}

function commitAndSendRealtimeUpdate ({commit, state}, msg, payload) {
  commit(msg, payload)
  payload.user = _.get(state, 'user.username')
  payload.timestamp = new Date()
  sendRealtimeUpdate(msg, payload)
}

export async function loadOdbFile ({commit}) {
  const odbFile = await api.loadOdbFile()
  const startingDisplayUnits = await api.loadDisplayUnits(0, 500)

  if (realtime) {
    realtime.close()
  }

  commit(types.LOAD_ODBFILE, {
    odbFile,
    startingDisplayUnits
  })

  commit(types.SET_BRANCHES, {
    branches: odbFile.branches
  })

  realtime = new Realtime('http://localhost:8080')
}

export function loadDu ({commit, state}, {addr, units}) {
  console.log('loadDu', addr, units)
  let slice = _.slice(state.displayUnits, addr, addr + units)
  if (slice.length > 0 && _.every(slice) && slice.length === units) {
    return Q.resolve(slice)
  }

  return api.loadDisplayUnits(addr, units).then((displayUnits) => {
    commit(types.CACHE_DISPLAYUNITS, {
      start: addr,
      displayUnits: displayUnits
    })
    return displayUnits
  })
}

export async function clearDisplayUnits ({commit, state}, {addr}) {
  var lda = await api.vmaToLda(addr)
  let start = Math.max(0, lda - 250)
  let displayUnits = await api.loadDisplayUnits(start, 600)

  api.loadBranches().then((branches) => {
    commit(types.SET_BRANCHES, {
      branches: branches
    })
  })

  commitAndSendRealtimeUpdate({commit, state}, types.CLEAR_AND_SET_DISPLAYUNITS, {
    start: start,
    displayUnits: displayUnits
  })
}

export async function setBinaryText ({commit, state, dispatch}, {binaryText}) {
  await api.setBinaryText(binaryText)

  commit(types.SET_BINARYTEXT, {
    binaryText
  })

  dispatch('clearDisplayUnits', {addr: 0})
  return true
}

export async function setBinaryOptions ({commit, state, dispatch}, {architecture, baseAddress, endian, selectedOpts}) {
  await api.setBinaryOptions(architecture, baseAddress, endian, selectedOpts)
  commit(types.SET_BINARYOPTIONS, {architecture, baseAddress, endian, selectedOpts})
  dispatch('clearDisplayUnits', {addr: 0})
  return true
}

export async function dataToCode ({commit, state, dispatch}, {addr}) {
  await api.dataToCode(addr)
  let parcels = await api.loadParcels()
  commitAndSendRealtimeUpdate({commit, state}, types.SET_PARCELS, { parcels })
  dispatch('clearDisplayUnits', {addr: addr})
}

export async function codeToData ({commit, state, dispatch}, {addr}) {
  await api.codeToData(addr)
  let parcels = await api.loadParcels()
  commitAndSendRealtimeUpdate({commit, state}, types.SET_PARCELS, { parcels })
  dispatch('clearDisplayUnits', {addr: addr})
}

export async function addComment ({commit, state}, {comment, vma}) {
  await api.makeComment(comment, vma)
  commitAndSendRealtimeUpdate({commit, state}, types.MAKE_COMMENT, {comment, vma})
}

export async function setDefaultSharingLevel ({commit, state}, {permissionLevel}) {
  await api.setDefaultPermissionLevel(permissionLevel)
  commit(types.SET_DEFAULT_PERMISSION_LEVEL, { permissionLevel })
}

export function updateUserPosition ({commit, state}, {username, address}) {
  commit(types.UPDATE_USER_POSITION, {username, address})
}

export async function createString ({commit, state, dispatch}, {addr}) {
  await api.createDefinedData(addr, 'builtin', 'ascii', 'string_' + addr.toString(16))
  dispatch('clearDisplayUnits', {addr: addr})
}

export async function undefineData ({commit, state, dispatch}, {addr}) {
  await api.undefineData(addr)
  dispatch('clearDisplayUnits', {addr: addr})
}

export async function createStructDefinedData ({commit, state, dispatch}, {addr, varName, structName}) {
  await api.createDefinedData(addr, 'struct', structName, varName)
  dispatch('clearDisplayUnits', {addr: addr})
}

export async function upsertFunction ({commit, state}, {vma, name, retval, args}) {
  let f = _.find(state.functions, {vma: vma})
  if (f) {
    await api.updateFunction(vma, name, retval, args)
  } else {
    await api.createFunction(vma, name, retval, args)
  }

  commitAndSendRealtimeUpdate({commit, state}, types.UPDATE_FUNCTION, {vma, name, retval, args})
}

export async function addStruct ({commit, state}, {name}) {
  await api.createStructure(name)
  commit(types.ADD_STRUCTURE, {name})
}

export async function deleteStruct ({commit, state}, {index}) {
  await api.deleteStructure(index)
  commit(types.DELETE_STRUCT, {index: index})
}

export async function updateStruct ({commit, state}, {index, struct}) {
  await api.updateStructure(index, struct)
}

export async function login ({commit, state}, {username, password}) {
  await auth.login(username, password)
  let whoami = auth.whoami()
  commit(types.UPDATE_USER, {user: whoami})
  return whoami
}
