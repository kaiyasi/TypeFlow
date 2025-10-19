export function setAppMeta(title: string, description: string, image: string = '/logo.png') {
  if (title) document.title = title

  const ensureMeta = (selector: string, createAttrs: Record<string, string>) => {
    let el = document.querySelector(selector) as HTMLMetaElement | null
    if (!el) {
      el = document.createElement('meta') as HTMLMetaElement
      Object.entries(createAttrs).forEach(([k, v]) => el!.setAttribute(k, v))
      document.head.appendChild(el)
    }
    return el
  }

  // Standard description
  const descMeta = ensureMeta('meta[name="description"]', { name: 'description' })
  descMeta.setAttribute('content', description)

  // Open Graph
  const ogTitle = ensureMeta('meta[property="og:title"]', { property: 'og:title' })
  ogTitle.setAttribute('content', title)
  const ogDesc = ensureMeta('meta[property="og:description"]', { property: 'og:description' })
  ogDesc.setAttribute('content', description)
  const ogImage = ensureMeta('meta[property="og:image"]', { property: 'og:image' })
  ogImage.setAttribute('content', image)

  // Twitter
  const twTitle = ensureMeta('meta[name="twitter:title"]', { name: 'twitter:title' })
  twTitle.setAttribute('content', title)
  const twDesc = ensureMeta('meta[name="twitter:description"]', { name: 'twitter:description' })
  twDesc.setAttribute('content', description)
  const twImage = ensureMeta('meta[name="twitter:image"]', { name: 'twitter:image' })
  twImage.setAttribute('content', image)
}

export function setHtmlLang(lang: string) {
  if (lang) {
    document.documentElement.setAttribute('lang', lang)
  }
}

