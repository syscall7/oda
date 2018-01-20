import axios from 'axios/index'
import store from '../store/index'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

export async function whoami () {
  const response = await axios.get('/odaweb/api/user/who_am_i/', { })
  return response.data
}

export async function signup (username, email, password1, password2) {
  const response = await axios.post(store.state.apiRoot + '/odaweb/auth/registration/', {
    username, email, password1, password2
  })
  return response.data
}

export async function login (username, password) {
  const response = await axios.post(store.state.apiRoot + '/odaweb/auth/login/', {
    username, password
  })
  return response.data
}

export async function reset (email) {
  const response = await axios.post(store.state.apiRoot + '/odaweb/auth/password/reset/', {
    email
  })
  return response.data
}

export async function logout () {
  const response = await axios.post(store.state.apiRoot + '/odaweb/auth/logout/')
  return response.data
}
