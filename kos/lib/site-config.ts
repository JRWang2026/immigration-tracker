export const SITE_CONFIG = {
  name: "KOS",
  fullName: "Knowledge Operating System",
  author: "王工",
  tagline: {
    zh: "制造数字化转型 · 竞争情报研究",
    en: "Manufacturing Digitalization · Competitive Intelligence Research",
  },
  description: {
    zh: "面向申博的个人研究交互平台——专利分析、代码实验室、3D展示、知识管理",
    en: "Personal research platform for PhD applications — patent analysis, code lab, 3D viewer, knowledge management",
  },
} as const;

export const NAV_ITEMS = [
  { key: "home", href: "", labelKey: "home" },
  { key: "patent", href: "/patent", labelKey: "patent" },
  { key: "code", href: "/code", labelKey: "code" },
  { key: "threeD", href: "/3d", labelKey: "threeD" },
  { key: "research", href: "/research", labelKey: "research" },
  { key: "intelligence", href: "/intelligence", labelKey: "intelligence" },
  { key: "knowledge", href: "/knowledge", labelKey: "knowledge" },
  { key: "draw", href: "/draw", labelKey: "draw" },
] as const;
