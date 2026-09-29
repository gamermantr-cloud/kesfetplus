import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import * as api from './api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(undefined) // undefined = loading, null = logged out
  const [error, setError] = useState(null)

  const refresh = useCallback(async () => {
    if (!api.isLoggedIn()) {
      setUser(null)
      return
    }
    try {
      const me = await api.getMe()
      setUser(me)
    } catch {
      // token invalid/expired server-side
      api.setToken(null)
      setUser(null)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  async function doLogin(credentials) {
    setError(null)
    const loggedInUser = await api.login(credentials)
    setUser(loggedInUser)
    return loggedInUser
  }

  async function doRegister(payload) {
    setError(null)
    const newUser = await api.register(payload)
    setUser(newUser)
    return newUser
  }

  async function doLogout() {
    await api.logout()
    setUser(null)
  }

  async function doBlock(userId) {
    const { blocked_user_ids: blockedUserIds } = await api.blockUser(userId)
    setUser((u) => (u ? { ...u, blocked_user_ids: blockedUserIds } : u))
  }

  async function doUnblock(userId) {
    const { blocked_user_ids: blockedUserIds } = await api.unblockUser(userId)
    setUser((u) => (u ? { ...u, blocked_user_ids: blockedUserIds } : u))
  }

  const value = {
    user,
    isLoggedIn: Boolean(user),
    loading: user === undefined,
    error,
    login: doLogin,
    register: doRegister,
    logout: doLogout,
    block: doBlock,
    unblock: doUnblock,
    refresh,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
