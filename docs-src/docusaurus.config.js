module.exports = {
  title: "Annotell",
  tagline: "API Documentation of Annotell Platform APIs",
  url: "https://annotell.com",
  baseUrl: "/",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/favicon.ico",
  organizationName: "annotell", // Usually your GitHub org/user name.
  projectName: "annotell-python", // Usually your repo name.
  themeConfig: {
    navbar: {
      logo: {
        alt: "Annotell Logo",
        src: "img/annotell-logo.svg",
      },
      items: [
        {
          to: "docs/",
          activeBasePath: "docs",
          label: "API",
          position: "left",
        },
        {
          href: "https://github.com/annotell/annotell-python",
          label: "GitHub",
          position: "right",
        },
      ],
    },
  },
  presets: [
    [
      "@docusaurus/preset-classic",
      {
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          // Please change this to your repo.
          editUrl:
            "https://github.com/annotell/annotell-python/edit/gh-pages/annotell-sdk/",
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      },
    ],
  ],
};
