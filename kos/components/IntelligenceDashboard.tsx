"use client";

import { useEffect, useState } from "react";

interface Job {
  title: string;
  company: string;
  location: string;
  salary: string;
  url: string;
  score: number;
  reasons: string[];
  immigration_path: string;
  suggested_skills: string;
  anzsco_code: string;
  anzsco_name: string;
}

interface SeekData {
  date: string;
  email_count: number;
  total_jobs: number;
  tier1_jobs: Job[];
  all_jobs: Job[];
}

interface FeedData {
  meta: {
    title: string;
    description: string;
    last_updated: string;
  };
  data: SeekData;
}

export default function IntelligenceDashboard() {
  const [data, setData] = useState<FeedData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/seek-nz/latest.json")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json: FeedData) => {
        setData(json);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "加载失败");
        setLoading(false);
      });
  }, []);

  if (loading) return <div style={{ padding: "3rem 1.5rem", textAlign: "center" }}>正在加载情报数据…</div>;
  if (error) return <div style={{ padding: "3rem 1.5rem", textAlign: "center", color: "#dc2626" }}>加载失败: {error}</div>;
  if (!data) return null;

  const summary = data.data;
  const tier1 = summary.tier1_jobs;

  return (
    <div style={{ padding: "3rem 0 5rem" }}>
      <div className="container">
        <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--slate-800)", marginBottom: "0.5rem" }}>
            SEEK NZ 绿名单岗位追踪
          </h1>
          <p style={{ color: "var(--slate-500)", fontSize: "1.05rem" }}>
            数据来源：私人本地 Agent 每日扫描 QQ Mail · 绿名单 Tier1 ICT 聚焦
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
            gap: "1rem",
            marginBottom: "2.5rem",
          }}
        >
          <StatCard label="扫描邮件" value={summary.email_count} />
          <StatCard label="去重岗位" value={summary.total_jobs} />
          <StatCard label="Tier1 匹配" value={tier1.length} highlight />
          <StatCard label="更新日期" value={summary.date} />
        </div>

        {tier1.length > 0 && (
          <Section title="🏆 绿名单 Tier1 匹配岗位">
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
                <thead>
                  <tr style={{ background: "var(--slate-100)", textAlign: "left" }}>
                    <th style={th}>岗位</th>
                    <th style={th}>公司</th>
                    <th style={th}>地点</th>
                    <th style={th}>薪资</th>
                    <th style={th}>匹配度</th>
                    <th style={th}>ANZSCO</th>
                    <th style={th}>移民路径</th>
                  </tr>
                </thead>
                <tbody>
                  {tier1.map((job, idx) => (
                    <tr key={idx} style={{ borderBottom: "1px solid var(--slate-200)" }}>
                      <td style={td}>
                        <a href={job.url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--blue-700)", textDecoration: "none" }}>
                          {job.title}
                        </a>
                      </td>
                      <td style={td}>{job.company}</td>
                      <td style={td}>{job.location}</td>
                      <td style={td}>{job.salary || "—"}</td>
                      <td style={td}>
                        <span
                          style={{
                            background: job.score >= 70 ? "#dcfce7" : job.score >= 50 ? "#fef9c3" : "#fee2e2",
                            color: job.score >= 70 ? "#166534" : job.score >= 50 ? "#854d0e" : "#991b1b",
                            padding: "0.25rem 0.5rem",
                            borderRadius: "9999px",
                            fontWeight: 600,
                          }}
                        >
                          {job.score}
                        </span>
                      </td>
                      <td style={td}>
                        {job.anzsco_code}
                        <br />
                        <span style={{ color: "var(--slate-500)", fontSize: "0.8rem" }}>{job.anzsco_name}</span>
                      </td>
                      <td style={td}>{job.immigration_path}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>
        )}

        <Section title="🛠️ 建议补强技能">
          <ul style={{ paddingLeft: "1.25rem", color: "var(--slate-700)" }}>
            <li>SQL 查询与索引优化（LeetCode Database 50 题）</li>
            <li>PostgreSQL / MySQL 管理、备份、权限配置</li>
            <li>AWS RDS / Azure SQL 云端数据库实践经验</li>
            <li>英文简历与面试表达（突出 ERP/SAP/Oracle + Python 数据经验）</li>
            <li>NZQA IQA 学历评估（绿名单直申前置）</li>
          </ul>
        </Section>

        <Section title="⚙️ 自动化说明">
          <p style={{ color: "var(--slate-600)", lineHeight: 1.7 }}>
            本页面由本地 Python Agent 驱动，每日从 QQ Mail 拉取 SEEK 推送邮件，解析 HTML 提取岗位，并按绿名单
            Tier1 ICT 标准评分。匹配岗位会自动写入该 JSON feed，Next.js 客户端渲染展示。
            这是一个可写进 CV/申博作品集的开源数据工程与自动化情报项目。
          </p>
        </Section>
      </div>
    </div>
  );
}

function StatCard({ label, value, highlight }: { label: string; value: string | number; highlight?: boolean }) {
  return (
    <div
      style={{
        padding: "1.25rem",
        borderRadius: "var(--rounded-lg)",
        background: highlight ? "var(--blue-50)" : "var(--slate-50)",
        border: `1px solid ${highlight ? "var(--blue-200)" : "var(--slate-200)"}`,
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: "1.75rem", fontWeight: 800, color: highlight ? "var(--blue-700)" : "var(--slate-800)" }}>{value}</div>
      <div style={{ fontSize: "0.875rem", color: "var(--slate-500)", marginTop: "0.25rem" }}>{label}</div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section
      style={{
        marginBottom: "2.5rem",
        padding: "1.5rem",
        background: "var(--white)",
        borderRadius: "var(--rounded-lg)",
        border: "1px solid var(--slate-200)",
        boxShadow: "var(--shadow)",
      }}
    >
      <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--slate-800)", marginBottom: "1rem" }}>{title}</h2>
      {children}
    </section>
  );
}

const th: React.CSSProperties = { padding: "0.75rem", fontWeight: 600, color: "var(--slate-700)" };
const td: React.CSSProperties = { padding: "0.75rem", color: "var(--slate-700)", verticalAlign: "top" };
