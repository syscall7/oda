import axios from 'axios/index'
import {bus, API_ERROR} from '../bus'
import store from '../store/index'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

function error (e) {
  bus.$emit(API_ERROR, e)
  throw e
}

export async function loadOdbFile () {
  try {
    const response = await axios.get(store.state.apiRoot + '/odaweb/api/load', {
      params: {
        short_name: store.state.shortName,
        revision: store.state.revision
      }
    })
    return response.data
  } catch (e) {
    error({e, message: `loading an odb file ${store.state.shortName}`})
  }
}

export async function loadDisplayUnits (addr, units) {
  console.log('loading display units', addr, units)
  try {
    const response = await axios.get(store.state.apiRoot + '/odaweb/api/displayunits/', {
      params: {
        short_name: store.state.shortName,
        revision: store.state.revision,
        addr: addr,
        units: units,
        logical: true
      }
    })

    return response.data
  } catch (e) {
    error({e})
  }
}

export async function loadBranches () {
  try {
    const response = await axios.get(`/odaweb/api/masters/${store.state.shortName}/branches/`)
    return response.data.branches
  } catch (e) {
    error({e})
  }
}

export async function vmaToLda (vma) {
  try {
    const response = await axios.get(store.state.apiRoot + '/odaweb/api/displayunits/1/vmaToLda', {
      params: {
        short_name: store.state.shortName,
        revision: store.state.revision,
        vma: vma
      }
    })

    return response.data
  } catch (e) {
    error({e})
  }
}

export async function findBytes (bytes) {
  const response = await axios.get(store.state.apiRoot + '/odaweb/api/find/', {
    params: {
      short_name: store.state.shortName,
      revision: store.state.revision,
      bytes: bytes
    }
  })

  return response.data
}

export async function setBinaryText (binaryText) {
  try {
    const response = await axios.patch(store.state.apiRoot + '/odaweb/api/binarystrings/0/', {
      short_name: store.state.shortName,
      revision: store.state.revision,
      binary_string: binaryText
    })
    return response.data
  } catch (e) {
    error({e})
  }
}

export async function canEdit (shortName) {
  const response = await axios.get(`/odaweb/api/masters/${shortName}/can_edit/`)
  console.log('canEdit', response.data)
  return response.data
}

export async function copyOdaMaster (shortName) {
  const response = await axios.get(`/odaweb/api/masters/${shortName}/clone/`)
  return response.data
}

export async function getArchitectureOptions (arch) {
  if (arch === 'UNKNOWN!') {
    return Promise.resolve([])
  }
  try {
    const response = await axios.get(`/odaweb/api/disassembler/0/options/?arch=${arch}`)
    return response.data
  } catch (e) {
    error({e, message: `getting the architecture ${arch} options`})
  }
}

export async function setBinaryOptions (architecture, baseAddress, endian, selectedOpts, shortName, revision = 0) {
  if (!shortName) {
    shortName = store.state.shortName
  }

  try {
    const response = await axios.patch(`/odaweb/api/options/0/`, {
      architecture: architecture,
      base_address: baseAddress,
      endian: endian,
      selected_opts: selectedOpts,
      short_name: shortName,
      revision: revision
    })
    return response.data
  } catch (e) {
    error({e, message: 'set the binary options'})
  }
}

export async function uploadFile (file, projectName, defaultSharingMode) {
  try {
    let formData = new FormData()
    formData.append('filedata', file)
    formData.append('project_name', projectName)
    formData.append('default_sharing_level', defaultSharingMode)
    const response = await axios.post('/odaweb/_upload', formData)
    return response.data
  } catch (e) {
    error({e, message: 'upload a File'})
  }
}

export async function graph (addr) {
  const response = await axios.get(store.state.apiRoot + '/odaweb/api/graph', {
    params: {
      short_name: store.state.shortName,
      revision: store.state.revision,
      addr: addr
    }
  })
  return response.data
}

export async function loadParcels () {
  const response = await axios.get('/odaweb/api/parcels/', {
    params: {
      short_name: store.state.shortName,
      revision: store.state.revision
    }
  })
  return response.data
}

export async function dataToCode (addr) {
  try {
    const response = await axios.get('/odaweb/api/displayunits/1/makeCode/', {
      params: {
        short_name: store.state.shortName,
        revision: store.state.revision,
        vma: addr
      }
    })
    return response.data
  } catch (e) {
    error({e, message: e.response.data.detail})
  }
}

export async function codeToData (addr) {
  try {
    const response = await axios.get('/odaweb/api/displayunits/1/makeData/', {
      params: {
        short_name: store.state.shortName,
        revision: store.state.revision,
        vma: addr
      }
    })
    return response.data
  } catch (e) {
    error({e, message: 'change code to data'})
  }
}

export async function createDefinedData (addr, typeKind, typeName, varName) {
  try {
    const response = await axios.post('/odaweb/api/definedData/', {
      short_name: store.state.shortName,
      revision: store.state.revision,
      vma: addr,
      type_kind: typeKind,
      type_name: typeName,
      var_name: varName
    })
    return response.data
  } catch (e) {
    error({e, message: e.response.data.detail})
  }
}

export async function undefineData (addr) {
  try {
    const response = await axios.delete('/odaweb/api/definedData/0/', {
      data: {
        short_name: store.state.shortName,
        revision: store.state.revision,
        vma: addr
      }
    })
    return response.data
  } catch (e) {
    error({e, message: e.response.data.detail})
  }
}

export async function makeComment (comment, vma) {
  try {
    const response = await axios.post('/odaweb/api/comments/', {
      short_name: store.state.shortName,
      revision: store.state.revision,
      comment: comment,
      vma: vma
    })
    return response.data
  } catch (e) {
    error({e, message: 'adding a comment'})
  }
}

export async function loadOperations () {
  try {
    const response = await axios.get('/odaweb/api/operations/', {
      params: {
        short_name: store.state.shortName,
        revision: store.state.revision
      }
    })
    return response.data
  } catch (e) {
    error({e, message: 'Loading the operations...'})
  }
}

export async function decompiled (addr) {
  const response = await axios.get('/odaweb/api/decompiler', {
    params: {
      short_name: store.state.shortName,
      revision: store.state.revision,
      addr: addr
    }
  })
  return response.data
}

export async function setDefaultPermissionLevel (permissionLevel) {
  try {
    const response = await axios.post(`/odaweb/api/masters/${store.state.shortName}/set_default_permission_level/`, {
      permission_level: permissionLevel
    })
    return response.data
  } catch (e) {
    error({e, message: 'getting the decompiled results'})
  }
}

export async function createFunction (vma, name, retval, args) {
  try {
    const response = await axios.post(`/odaweb/api/displayunits/1/makeFunction/`, {
      short_name: store.state.shortName,
      revision: store.state.revision,
      vma: vma,
      name: name,
      retval: retval,
      args: args
    })
    return response.data
  } catch (e) {
    error({e, message: 'adding a new function'})
  }
}

export async function updateFunction (vma, name, retval, args) {
  try {
    const response = await axios.patch(`/odaweb/api/functions/0/`, {
      short_name: store.state.shortName,
      revision: store.state.revision,
      vma: vma,
      name: name,
      retval: retval,
      args: args
    })
    return response.data
  } catch (e) {
    error({e, message: 'updating an existing function'})
  }
}

export async function createStructure (name) {
  try {
    const response = await axios.post(`/odaweb/api/cstructs/`, {
      short_name: store.state.shortName,
      revision: store.state.revision,
      is_packed: true,
      name: name

    })
    return response.data
  } catch (e) {
    error({e, message: 'creating a structure definition'})
  }
}

export async function deleteStructure (index) {
  try {
    const response = await axios.delete(`/odaweb/api/cstructs/${index}/`, {
      data: {
        short_name: store.state.shortName,
        revision: store.state.revision
      }
    })
    return response.data
  } catch (e) {
    error({e, message: 'deleting a structure definition'})
  }
}

export async function updateStructure (index, structure) {
  try {
    let structFieldNames = []
    let structFieldTypes = []

    let numFields = structure.fields.length
    for (var i = 0; i < numFields; i++) {
      structFieldNames[i] = structure.fields[i].name
      structFieldTypes[i] = structure.fields[i].type
    }

    const response = await axios.get(`/odaweb/api/cstructs/${index}/modify/`, {
      params: {
        short_name: store.state.shortName,
        revision: store.state.revision,
        field_types: structFieldTypes,
        field_names: structFieldNames
      }
    })

    return response.data
  } catch (e) {
    error({e, message: 'deleting a structure definition'})
  }
}

export async function listMyDocuments () {
  try {
    const response = await axios.get(`/odaweb/api/masters/`)
    return response.data
  } catch (e) {
    error({e, message: 'deleting a structure definition'})
  }
}

export async function deleteDocument (shortName) {
  try {
    const response = await axios.delete(`/odaweb/api/masters/${shortName}/`)
    return response.data
  } catch (e) {
    error({e, message: 'deleting a structure definition'})
  }
}
