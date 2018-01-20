import io from 'socket.io-client'
import store from './store'
import * as types from './store/mutation-types'
import {bus, ADDRESS_AT_TOP_CHANGED} from './bus'

export class Realtime {
  constructor (url) {
    this.url = url
    this.username = store.state.user.username
    this.shortName = store.state.shortName
    console.log('new store created', this.username, this.shortName)
    this.connect()

    bus.$on(ADDRESS_AT_TOP_CHANGED, (address) => {
      this.emitAddressChange(address)
    })
  }

  connect () {
    this.socket = io(this.url)
    this.socket.on('connect', () => {
      this.onConnect()
    })

    this.socket.on('users', (data) => {
      this.updateUsers(data)
    })

    this.socket.on('document.update', (data) => {
      this.documentUpdate(data)
    })

    this.socket.on('user.position.update', (data) => {
      this.handlePositionUpdate(data)
    })
  }

  emitAddressChange (address) {
    if (this.socket) {
      this.socket.emit('user.position.update', {
        username: store.state.user.username,
        address: address
      })
    }
  }

  onConnect (socket) {
    this.socket.emit('subscribe', {
      username: this.username,
      room: this.shortName
    })
  }

  documentUpdate (data) {
    console.log('document.update', data)
    store.commit(data.msg, data.payload)
  }

  emit (msg, payload) {
    if (!this.socket) {
      console.log('Tied to emit without a socket')
      return
    }

    this.socket.emit('document.update', {
      msg: msg,
      payload: payload
    })
  }

  handlePositionUpdate (data) {
    store.dispatch('updateUserPosition', data)
  }

  updateUsers (data) {
    console.log('ACTIVE_USERS: ' + JSON.stringify(data))
    store.commit(types.SET_ACTIVE_USERS, {activeUsers: data.users})
  }

  close () {
    this.socket.disconnect()
  }
}
