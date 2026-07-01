// app/intelligence/page.tsx
// KOS 学术网站新增页面：自动化情报中心
// 从 public/data/seek-nz_latest.json 读取本地 Agent 输出

import fs from "fs/promises";
import path from "path";

interface Job {
  title: string;
  company: string;
  location: string;
  salary: string;
  url: string;
  score: number;
  anzsco_code: string;
  anzsco_name: string;
  immigration_path: string;
  suggested_skills: string;
}

interface SeekFeed {
  meta: {
    title: string;
    description: string;
    last_updated: string;
  };
  data: {
    date: string;
    email_count: number;
    total_jobs: number;
    tier1_jobs: Job[];
  };
}

async function loadSeekFeed(): Promise<SeekFeed | null> {
  try {
    const filePath = path.join(process.cwd(), "public", "data", "seek-nz_latest.json");
    const text = await fs.readFile(filePath, "utf-8");
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export default async function IntelligencePage() {
  const feed = await loadSeekFeed();

  return (
    <main className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">自动化情报中心</h1>
      <p className="text-gray-600 mb-6">
        由本地私人 Agent 每日自动扫描并同步：SEEK NZ 绿名单岗位、全球移民政策、德国博士岗位。
      </p>

      {feed ? (
        <section className="mb-10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">{feed.meta.title}</h2>
            <span className="text-sm text-gray-500">
              更新于 {new Date(feed.meta.last_updated).toLocaleString("zh-CN")}
            </span>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            扫描 {feed.data.email_count} 封邮件，去重 {feed.data.total_jobs} 个岗位，
            Tier1 匹配 {feed.data.tier1_jobs.length} 个。
          </p>

          {feed.data.tier1_jobs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-gray-100 text-left">
                    <th className="p-3 border">匹配度</th>
                    <th className="p-3 border">职位</th>
                    <th className="p-3 border">公司</th>
                    <th className="p-3 border">地点</th>
                    <th className="p-3 border">薪资</th>
                    <th className="p-3 border">ANZSCO</th>
                  </tr>
                </thead>
                <tbody>
                  {feed.data.tier1_jobs.map((job) => (
                    <tr key={job.url} className="hover:bg-gray-50">
                      <td className="p-3 border font-bold text-blue-700">{job.score}</td>
                      <td className="p-3 border">
                        <a href={job.url} target="_blank" rel="noreferrer" className="text-blue-600 underline">
                          {job.title}
                        </a>
                      </td>
                      <td className="p-3 border">{job.company}</td>
                      <td className="p-3 border">{job.location}</td>
                      <td className="p-3 border">{job.salary}</td>
                      <td className="p-3 border">
                        {job.anzsco_code} {job.anzsco_name}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500">今日无 Tier1 高匹配岗位。</p>
          )}
        </section>
      ) : (
        <p className="text-red-500">暂无 Agent 数据。请先运行本地 Agent。</p>
      )}

      <section className="text-sm text-gray-500 border-t pt-4">
        <p>
          数据源：<code>public/data/seek-nz_latest.json</code>，由{" "}
          <code>local_agent/seek_email_agent.py</code> 生成。
        </p>
      </section>
    </main>
  );
}
