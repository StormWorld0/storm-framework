import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Storm Framework",
  description: "Official Documentation for Storm Framework",
  cleanUrls: true, // Menghilangkan ekstensi .html dari URL

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Wiki Docs', link: '/storm-framework.wiki/INSTALLATION-LINUX' }
    ],

    sidebar: [
      {
        text: 'Overview',
        items: [
          { text: 'Getting Started', link: '/README' }
        ]
      },
      {
        text: 'Installation Guides',
        collapsed: false,
        items: [
          { text: 'Linux Installation', link: '/storm-framework.wiki/INSTALLATION-LINUX' },
          { text: 'Docker Setup', link: '/storm-framework.wiki/INSTALLATION-DOCKER' },
          { text: 'Termux Setup', link: '/storm-framework.wiki/INSTALLATION-TERMUX' },
          { text: 'VirtualEnv (VENV)', link: '/storm-framework.wiki/INSTALLATION-VENV' },
        ]
      },
      {
        text: 'Core Engine & Architecture',
        collapsed: false,
        items: [
          { text: 'CRS Engine', link: '/storm-framework.wiki/CRS-ENGINE' },
          { text: 'Caller Binary', link: '/storm-framework.wiki/CALLER-BINARY' },
          { text: 'Logger System', link: '/storm-framework.wiki/LOGGER' },
        ]
      },
      {
        text: 'Developer & Modules',
        collapsed: false,
        items: [
          { text: 'Module Guide', link: '/storm-framework.wiki/MODULE-GUIDE' },
          { text: 'Plugin Overview', link: '/storm-framework.wiki/PLUGIN' },
          { text: 'Plugin Development', link: '/storm-framework.wiki/PLUGIN-DEV' },
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/StormWorld0/Storm-Framework' }
    ]
  }
})
