import { useEffect, useState } from 'react'
import { useNavigationType } from 'react-router-dom'

const STORAGE_PREFIX = 'kp-restorable:'

function read(key) {
  try {
    const raw = sessionStorage.getItem(STORAGE_PREFIX + key)
    return raw === null ? undefined : JSON.parse(raw)
  } catch {
    return undefined
  }
}

function write(key, value) {
  try {
    sessionStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(value))
  } catch {
    // sessionStorage kullanılamıyor - sessizce yoksay
  }
}

/**
 * useState gibi davranır, ama geri (POP) navigasyonda son değeri hatırlar -
 * ör. bir kategori filtresi seçiliyken bir mekana girip geri dönüldüğünde
 * aynı filtre seçili kalır. Normal (PUSH) gidişte her zamanki gibi
 * initialValue'dan başlar - bkz. lib/useScrollRestoration.js, aynı POP/PUSH
 * ayrımını kullanır.
 */
export function useRestorableState(key, initialValue) {
  const navigationType = useNavigationType()
  const [value, setValue] = useState(() => {
    if (navigationType === 'POP') {
      const stored = read(key)
      if (stored !== undefined) return stored
    }
    return initialValue
  })

  useEffect(() => {
    write(key, value)
  }, [key, value])

  return [value, setValue]
}
