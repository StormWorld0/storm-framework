import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(
  defineConfig({
    title: "Storm Framework",
    description: "Official Documentation for Storm Framework",
    cleanUrls: true,
    head: {
      ['meta', { name: 'google-site-verification=vlUvyI8dmnhudIOixjC7aFeGNTdOH6up1M15D8JCMck' }]
    },
    sitemap: {
      hostname: 'https://storm-framework.pages.dev'
    },
    mermaid: {
      theme: 'dark',
    },

    themeConfig: {
      logo: { src: '/storm.svg', height: 24 },
      nav: [
        { text: 'Home', link: '/' },
        { text: 'Documentation', link: '/README' }
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
            { text: 'Linux Standard Setup', link: '/storm-framework.wiki/INSTALLATION-LINUX' },
            { text: 'Docker Setup', link: '/storm-framework.wiki/INSTALLATION-DOCKER' },
            { text: 'Termux Setup', link: '/storm-framework.wiki/INSTALLATION-TERMUX' },
            { text: 'Venv Setup', link: '/storm-framework.wiki/INSTALLATION-VENV' },
          ]
        },
        {
          text: 'Core Engine & API',
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
        },
        {
          text: 'Architecture',
          collapsed: false,
          items: [
            { text: 'Flow And Arch', link: '/storm-framework.wiki/FlowAndArch.md' },
          ]
        }
      ],

      socialLinks: [
        { icon: 'github', link: 'https://github.com/StormWorld0/storm-framework' },
        { icon: 'docker', link: 'https://hub.docker.com/r/stormworld0/storm-framework' }
      ],

      search: {
        provider: 'local',
      },

      footer: {
        message: 'Released under the GPL License.',
        copyright: 'Copyright © StormWorld0, zxelzy.',
      },
    },
  }),
)
