"use client";

import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

// ─── Types ───────────────────────────────────────────
interface PatentData {
  total: number;
  patents: { title: string; authors: string; type: string; year: string; pubno: string; abstract: string }[];
  keywords: { word: string; count: number }[];
  network: { nodes: { id: string; count: number }[]; links: { source: string; target: string; weight: number }[] };
  techDistribution: { name: string; count: number }[];
  typeStats: { name: string; count: number }[];
  yearStats: { year: number; count: number }[];
}

const COLORS = ["#E63946", "#457B9D", "#2A9D8F", "#E9C46A", "#F4A261", "#264653"];
const LIGHT_COLORS = ["#FFE5E5", "#E5EDF5", "#E5F5F3", "#FDF5E5", "#FDF0E8", "#E5EAF0"];

// ─── Word Cloud ──────────────────────────────────────
function WordCloud({ data, width }: { data: PatentData["keywords"]; width: number }) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; word: string; count: number } | null>(null);

  useEffect(() => {
    if (!data.length) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // 足够大的画布，每个词给足呼吸空间
    const height = Math.max(500, data.length * 24);
    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const fScale = d3.scaleLinear()
      .domain([d3.min(data, d => d.count)!, d3.max(data, d => d.count)!])
      .range([16, 52]);

    const group = svg.append("g").attr("transform", `translate(${width / 2},${height / 2})`);

    const nodes = data.map((d) => ({
      text: d.word,
      size: fScale(d.count),
      count: d.count,
      x: (Math.random() - 0.5) * width * 0.6,
      y: (Math.random() - 0.5) * height * 0.6,
    }));

    const simulation = d3.forceSimulation(nodes as any)
      .force("center", d3.forceCenter(0, 0))
      // 碰撞半径 = 词宽的一半（中文字符宽度≈字号*0.85）+ 边距
      .force("collide", d3.forceCollide().radius((d: any) => d.text.length * d.size * 0.43 + 4))
      .force("x", d3.forceX(0).strength(0.01))
      .force("y", d3.forceY(0).strength(0.01))
      .stop();

    for (let i = 0; i < 400; i++) simulation.tick();

    group.selectAll("text").data(nodes).enter().append("text")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("x", (d: any) => d.x)
      .attr("y", (d: any) => d.y)
      .attr("font-size", (d: any) => `${d.size}px`)
      .attr("font-weight", (d: any) => d.size > 36 ? "700" : "400")
      .attr("fill", (_, i) => COLORS[i % COLORS.length])
      .attr("opacity", 0.85)
      .attr("cursor", "pointer")
      .text((d: any) => d.text)
      .on("mouseenter", function (event: any, d: any) {
        const rect = svgRef.current!.getBoundingClientRect();
        setTooltip({ x: event.clientX - rect.left, y: event.clientY - rect.top - 30, word: d.text, count: d.count });
        d3.select(this).attr("opacity", 1).attr("font-weight", "800");
      })
      .on("mouseleave", function (_, d: any) {
        setTooltip(null);
        d3.select(this).attr("opacity", 0.85).attr("font-weight", d.size > 36 ? "700" : "400");
      });
  }, [data, width]);

  return (
    <div style={{ position: "relative" }}>
      <svg ref={svgRef} style={{ width: "100%", height: "auto" }} />
      {tooltip && (
        <div style={{
          position: "absolute", left: tooltip.x, top: tooltip.y,
          background: "#1a237e", color: "#fff", padding: "4px 10px",
          borderRadius: 6, fontSize: 13, pointerEvents: "none", whiteSpace: "nowrap",
          transform: "translate(-50%, -100%)",
        }}>
          {tooltip.word}: {tooltip.count}次
        </div>
      )}
    </div>
  );
}

// ─── Network Graph ───────────────────────────────────
function NetworkGraph({ data, width }: { data: PatentData["network"]; width: number }) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data.nodes.length) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const height = 480;
    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const linkEl = svg.append("g");
    const nodeEl = svg.append("g");
    const labelEl = svg.append("g");

    const links = data.links.map(d => ({ ...d }));
    const nodes = data.nodes.map(d => ({ ...d }));

    const simulation = d3.forceSimulation(nodes as any)
      .force("link", d3.forceLink(links).id((d: any) => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius((d: any) => Math.sqrt(d.count) * 12 + 8));

    const sizeScale = d3.scaleSqrt()
      .domain([1, d3.max(nodes, d => d.count)!])
      .range([8, 40]);

    const link = linkEl.selectAll("line").data(links).enter().append("line")
      .attr("stroke", "#ccc").attr("stroke-opacity", 0.5)
      .attr("stroke-width", d => Math.sqrt(d.weight) * 1.2);

    const node = nodeEl.selectAll("circle").data(nodes).enter().append("circle")
      .attr("r", d => sizeScale(d.count))
      .attr("fill", (_, i) => COLORS[i % COLORS.length])
      .attr("stroke", "#fff").attr("stroke-width", 1.5)
      .call(d3.drag<SVGCircleElement, any>()
        .on("start", (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on("drag", (e, d) => { d.fx = e.x; d.fy = e.y; })
        .on("end", (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }) as any);

    node.append("title").text((d: any) => `${d.id}\n${d.count} 件专利`);

    const label = labelEl.selectAll("text").data(nodes).enter().append("text")
      .attr("text-anchor", "middle").attr("dy", -sizeScale(nodes[0].count) - 4)
      .attr("font-size", 11).attr("font-weight", "500")
      .attr("fill", "#333").text(d => d.id.length > 4 ? d.id.slice(0, 4) + ".." : d.id);

    simulation.on("tick", () => {
      link.attr("x1", (d: any) => d.source.x).attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x).attr("y2", (d: any) => d.target.y);
      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);
      label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
    });
  }, [data]);

  return <svg ref={svgRef} style={{ width: "100%", height: "auto" }} />;
}

// ─── Bar Chart ───────────────────────────────────────
function BarChart({ data, title, width, height }: { data: { name: string; count: number }[]; title: string; width: number; height: number }) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data.length) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const margin = { top: 40, right: 30, bottom: 60, left: 50 };
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand().domain(data.map(d => d.name)).range([0, innerW]).padding(0.3);
    const y = d3.scaleLinear().domain([0, d3.max(data, d => d.count)! * 1.15]).range([innerH, 0]);

    // Title
    g.append("text").attr("x", innerW / 2).attr("y", -15)
      .attr("text-anchor", "middle").attr("font-size", 15).attr("font-weight", "bold").text(title);

    // Bars
    g.selectAll("rect").data(data).enter().append("rect")
      .attr("x", d => x(d.name)!).attr("y", d => y(d.count))
      .attr("width", x.bandwidth()).attr("height", d => innerH - y(d.count))
      .attr("fill", (_, i) => COLORS[i % COLORS.length])
      .attr("rx", 4)
      .on("mouseenter", function () { d3.select(this).attr("opacity", 0.8); })
      .on("mouseleave", function () { d3.select(this).attr("opacity", 1); });

    // Labels
    g.selectAll(".label").data(data).enter().append("text")
      .attr("class", "label").attr("x", d => x(d.name)! + x.bandwidth() / 2)
      .attr("y", d => y(d.count) - 6).attr("text-anchor", "middle")
      .attr("font-size", 14).attr("font-weight", "bold").attr("fill", "#333")
      .text(d => d.count);

    // X axis
    g.append("g").attr("transform", `translate(0,${innerH})`).call(d3.axisBottom(x))
      .selectAll("text").attr("font-size", 12).attr("transform", "rotate(-15)")
      .style("text-anchor", "end");

    // Y axis
    g.append("g").call(d3.axisLeft(y).ticks(5)).selectAll("text").attr("font-size", 12);
  }, [data, title, width, height]);

  return <svg ref={svgRef} style={{ width: "100%", height: "auto" }} />;
}

// ─── Timeline ────────────────────────────────────────
function Timeline({ data, width, height }: { data: PatentData["yearStats"]; width: number; height: number }) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data.length) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const margin = { top: 30, right: 40, bottom: 50, left: 50 };
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear()
      .domain([d3.min(data, d => d.year)! - 1, d3.max(data, d => d.year)! + 1])
      .range([0, innerW]);
    const y = d3.scaleLinear().domain([0, d3.max(data, d => d.count)! * 1.3]).range([innerH, 0]);

    // Area fill
    const area = d3.area<{ year: number; count: number }>()
      .x(d => x(d.year)).y0(innerH).y1(d => y(d.count)).curve(d3.curveMonotoneX);
    g.append("path").datum(data).attr("fill", "url(#grad)").attr("d", area);

    // Gradient
    const grad = svg.append("defs").append("linearGradient").attr("id", "grad").attr("x1", "0").attr("x2", "0").attr("y1", "0").attr("y2", "1");
    grad.append("stop").attr("offset", "0%").attr("stop-color", "#457B9D").attr("stop-opacity", 0.6);
    grad.append("stop").attr("offset", "100%").attr("stop-color", "#457B9D").attr("stop-opacity", 0.05);

    // Line
    const line = d3.line<{ year: number; count: number }>()
      .x(d => x(d.year)).y(d => y(d.count)).curve(d3.curveMonotoneX);
    g.append("path").datum(data).attr("fill", "none").attr("stroke", "#457B9D")
      .attr("stroke-width", 3).attr("d", line);

    // Dots + labels
    g.selectAll(".dot").data(data).enter().append("circle")
      .attr("cx", d => x(d.year)).attr("cy", d => y(d.count))
      .attr("r", 6).attr("fill", "#457B9D").attr("stroke", "#fff").attr("stroke-width", 2);

    g.selectAll(".dot-label").data(data).enter().append("text")
      .attr("x", d => x(d.year)).attr("y", d => y(d.count) - 14)
      .attr("text-anchor", "middle").attr("font-size", 13).attr("font-weight", "bold")
      .attr("fill", "#1a237e").text(d => d.count);

    // Axes
    g.append("g").attr("transform", `translate(0,${innerH})`)
      .call(d3.axisBottom(x).ticks(data.length).tickFormat(d3.format("d")));
    g.append("g").call(d3.axisLeft(y).ticks(4));
  }, [data, width, height]);

  return <svg ref={svgRef} style={{ width: "100%", height: "auto" }} />;
}

// ─── Patent Table ────────────────────────────────────
function PatentTable({ data, t }: { data: PatentData; t: any }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table className="patent-table">
        <thead>
          <tr>
            <th>#</th><th>{t.title}</th><th>{t.inventors}</th>
            <th>{t.type}</th><th>{t.year}</th><th>{t.pubno}</th>
          </tr>
        </thead>
        <tbody>
          {data.patents.map((p, i) => (
            <tr key={i}>
              <td>{i + 1}</td>
              <td style={{ maxWidth: 300 }}>{p.title}</td>
              <td>{p.authors}</td>
              <td>{p.type}</td>
              <td>{p.year}</td>
              <td style={{ fontFamily: "Consolas, monospace", fontSize: 13 }}>{p.pubno}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── Certificate Gallery ─────────────────────────────
interface CertItem {
  id: string;
  src: string;       // base64 or original path
  label: string;
  type: "invention" | "utility" | "";
  isCustom: boolean; // true if user-uploaded (base64)
}

const DEFAULT_CERTS: CertItem[] = [
  { id: "c01", src: "/certs/patent-cert-01.png", label: "油井用方形护套电缆装置", type: "utility", isCustom: false },
  { id: "c02", src: "/certs/patent-cert-02.png", label: "电缆护套铅锭上料万向调节装置", type: "utility", isCustom: false },
  { id: "c03", src: "/certs/patent-cert-03.png", label: "磁悬浮列车电缆导线定位装置", type: "utility", isCustom: false },
  { id: "c04", src: "/certs/patent-cert-04.png", label: "磁悬浮列车长定子绕组电缆导线绞合装置", type: "invention", isCustom: false },
  { id: "c05", src: "/certs/patent-cert-05.png", label: "潜油电泵电缆与动力电缆联接结构", type: "utility", isCustom: false },
];

const CERT_STORAGE_KEY = "kos_cert_config";
const CERT_PASSWORD_KEY = "kos_cert_password";
const DEFAULT_PASSWORD = "kos2026";

function loadCerts(): CertItem[] {
  try {
    const raw = localStorage.getItem(CERT_STORAGE_KEY);
    if (raw) {
      const saved = JSON.parse(raw) as CertItem[];
      if (Array.isArray(saved) && saved.length > 0) return saved;
    }
  } catch { /* ignore */ }
  return [...DEFAULT_CERTS];
}

function saveCerts(certs: CertItem[]) {
  localStorage.setItem(CERT_STORAGE_KEY, JSON.stringify(certs));
}

function CertGallery({ t }: { t: any }) {
  const [certs, setCerts] = useState<CertItem[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [managing, setManaging] = useState(false);
  const [password, setPassword] = useState("");
  const [pwError, setPwError] = useState(false);
  const [showPw, setShowPw] = useState(false);
  const fileInputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Load certs on mount
  useEffect(() => {
    setCerts(loadCerts());
  }, []);

  function open(idx: number) { if (!managing) setSelected(idx); }
  function close() { setSelected(null); }
  function prev() { setSelected((s) => (s! - 1 + certs.length) % certs.length); }
  function next() { setSelected((s) => (s! + 1) % certs.length); }

  useEffect(() => {
    if (selected === null) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") prev();
      if (e.key === "ArrowRight") next();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selected, certs.length]);

  // ─── Password gate ───
  function tryUnlock() {
    if (password === DEFAULT_PASSWORD) {
      setManaging(true);
      setShowPw(false);
      setPwError(false);
      setPassword("");
    } else {
      setPwError(true);
    }
  }

  function exitManage() {
    setManaging(false);
    setCerts(loadCerts()); // reload from storage
  }

  // ─── Management actions ───
  function handleFileSelect(idx: number, e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      setCerts(prev => {
        const next = [...prev];
        next[idx] = {
          ...next[idx],
          src: reader.result as string,
          isCustom: true,
        };
        return next;
      });
    };
    reader.readAsDataURL(file);
  }

  function setCertType(idx: number, type: "invention" | "utility" | "") {
    setCerts(prev => {
      const next = [...prev];
      next[idx] = { ...next[idx], type };
      return next;
    });
  }

  function setCertLabel(idx: number, label: string) {
    setCerts(prev => {
      const next = [...prev];
      next[idx] = { ...next[idx], label };
      return next;
    });
  }

  function removeCert(idx: number) {
    setCerts(prev => prev.filter((_, i) => i !== idx));
  }

  function resetCert(idx: number) {
    setCerts(prev => {
      const next = [...prev];
      next[idx] = { ...DEFAULT_CERTS[idx], id: next[idx].id };
      return next;
    });
  }

  function resetAll() {
    setCerts([...DEFAULT_CERTS]);
  }

  function doSave() {
    saveCerts(certs);
    setManaging(false);
  }

  // Move cert up/down
  function moveUp(idx: number) {
    if (idx === 0) return;
    setCerts(prev => {
      const next = [...prev];
      [next[idx - 1], next[idx]] = [next[idx], next[idx - 1]];
      return next;
    });
  }

  function moveDown(idx: number) {
    if (idx === certs.length - 1) return;
    setCerts(prev => {
      const next = [...prev];
      [next[idx], next[idx + 1]] = [next[idx + 1], next[idx]];
      return next;
    });
  }

  return (
    <>
      {/* Management trigger */}
      {!managing && (
        <div className="cert-manage-trigger">
          <button
            className="cert-manage-btn"
            onClick={() => setShowPw(true)}
            title={t.manageCerts}
          >
            &#9881; {t.manageCerts}
          </button>
        </div>
      )}

      {/* Password Modal */}
      {showPw && !managing && (
        <div className="cert-modal-overlay" onClick={() => { setShowPw(false); setPwError(false); setPassword(""); }}>
          <div className="cert-modal" onClick={e => e.stopPropagation()}>
            <h3>{t.manageUnlock}</h3>
            <p style={{ fontSize: "0.85rem", color: "var(--slate-500)", marginBottom: "0.75rem" }}>{t.managePassword}</p>
            <input
              type="password"
              className="cert-pw-input"
              value={password}
              onChange={e => { setPassword(e.target.value); setPwError(false); }}
              onKeyDown={e => { if (e.key === "Enter") tryUnlock(); }}
              autoFocus
            />
            {pwError && <p className="cert-pw-error">{t.manageWrongPassword}</p>}
            <div className="cert-modal-actions">
              <button className="cert-modal-btn cert-modal-btn-cancel" onClick={() => { setShowPw(false); setPwError(false); setPassword(""); }}>{t.certClose}</button>
              <button className="cert-modal-btn cert-modal-btn-primary" onClick={tryUnlock}>{t.manageEnter}</button>
            </div>
          </div>
        </div>
      )}

      {/* Management Panel */}
      {managing && (
        <div className="cert-manager">
          <div className="cert-manager-header">
            <h3>{t.manageTitle}</h3>
            <p className="cert-manager-help">{t.manageHelp}</p>
          </div>
          <div className="cert-manager-grid">
            {certs.map((cert, idx) => (
              <div key={cert.id} className="cert-manager-item">
                {/* Upload area */}
                <div className="cert-manager-upload" onClick={() => fileInputRefs.current[idx]?.click()}>
                  <img src={cert.src} alt={`cert-${idx}`} />
                  <div className="cert-manager-upload-overlay">
                    <span>{cert.isCustom ? t.manageUpload : t.manageUpload}</span>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    ref={el => { fileInputRefs.current[idx] = el; }}
                    style={{ display: "none" }}
                    onChange={(e) => handleFileSelect(idx, e)}
                  />
                </div>
                {/* Type selector */}
                <select
                  className="cert-manager-select"
                  value={cert.type}
                  onChange={e => setCertType(idx, e.target.value as any)}
                >
                  <option value="">{t.manageLabel}...</option>
                  <option value="invention">{t.invention}</option>
                  <option value="utility">{t.utility}</option>
                </select>
                {/* Label input */}
                <input
                  className="cert-manager-label"
                  value={cert.label}
                  onChange={e => setCertLabel(idx, e.target.value)}
                  placeholder="标签文本..."
                />
                {/* Controls */}
                <div className="cert-manager-controls">
                  <button onClick={() => moveUp(idx)} disabled={idx === 0} title={t.manageDrag}>&#9650;</button>
                  <button onClick={() => moveDown(idx)} disabled={idx === certs.length - 1} title={t.manageDrag}>&#9660;</button>
                  <button onClick={() => resetCert(idx)} title={t.manageReset}>&#8634;</button>
                  {certs.length > 1 && (
                    <button onClick={() => removeCert(idx)} title={t.manageRemove} className="cert-manager-remove">&#10005;</button>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div className="cert-manager-footer">
            <button className="cert-modal-btn cert-modal-btn-cancel" onClick={resetAll}>{t.manageReset}</button>
            <button className="cert-modal-btn cert-modal-btn-cancel" onClick={exitManage}>{t.certClose}</button>
            <button className="cert-modal-btn cert-modal-btn-primary" onClick={doSave}>{t.manageSave}</button>
          </div>
        </div>
      )}

      {/* Normal view: grouped by patent type */}
      {!managing && (() => {
        const inventionCerts = certs.map((c, i) => ({ ...c, globalIdx: i })).filter(c => c.type === "invention");
        const utilityCerts = certs.map((c, i) => ({ ...c, globalIdx: i })).filter(c => c.type === "utility");
        const unlabeledCerts = certs.map((c, i) => ({ ...c, globalIdx: i })).filter(c => c.type !== "invention" && c.type !== "utility");

        const renderCertThumb = (cert: CertItem & { globalIdx: number }) => (
          <div key={cert.id} className="cert-thumb" onClick={() => open(cert.globalIdx)} title={cert.label}>
            <span className={`cert-badge ${cert.type === "invention" ? "cert-badge-invention" : "cert-badge-utility"}`}>
              {cert.type === "invention" ? t.invention : t.utility}
            </span>
            <img src={cert.src} alt={cert.label} loading="lazy" />
            <div className="cert-thumb-overlay">
              <span className="cert-thumb-btn">{t.certView}</span>
            </div>
          </div>
        );

        return (
          <>
            {/* Invention Patents Row */}
            {inventionCerts.length > 0 && (
              <div className="cert-group-section">
                <h3 className="cert-group-title">{t.inventionPatents}</h3>
                <div className="cert-gallery cert-gallery-invention">
                  {inventionCerts.map(renderCertThumb)}
                </div>
              </div>
            )}

            {/* Utility Models Row */}
            {utilityCerts.length > 0 && (
              <div className="cert-group-section">
                <h3 className="cert-group-title">{t.utilityModels}</h3>
                <div className="cert-gallery">
                  {utilityCerts.map(renderCertThumb)}
                </div>
              </div>
            )}

            {/* Unlabeled fallback */}
            {unlabeledCerts.length > 0 && (
              <div className="cert-gallery">
                {unlabeledCerts.map(renderCertThumb)}
              </div>
            )}
          </>
        );
      })()}

      {/* Lightbox */}
      {selected !== null && !managing && (
        <div className="cert-lightbox" onClick={close}>
          <div className="cert-lightbox-content" onClick={(e) => e.stopPropagation()}>
            <button className="cert-lightbox-close" onClick={close} title={t.certClose}>&times;</button>
            <button className="cert-lightbox-nav cert-lightbox-prev" onClick={prev}>&#8249;</button>
            <img src={certs[selected].src} alt={certs[selected].label} />
            <button className="cert-lightbox-nav cert-lightbox-next" onClick={next}>&#8250;</button>
            <div className="cert-lightbox-watermark">
              <div className="cert-lightbox-watermark-text">
                {Array.from({ length: 60 }, (_, i) => (
                  <span key={i}>KOS | WANG JIRUI | 学术展示</span>
                ))}
              </div>
            </div>
            <div className="cert-lightbox-caption">
              <span>{certs[selected].label}</span>
              <span className="cert-lightbox-counter">{selected + 1}{t.certOf}{certs.length}</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

// ─── Main Component ──────────────────────────────────
interface Props { lang: "zh" | "en"; t: any; }
export default function PatentVisualization({ lang, t }: Props) {
  const [data, setData] = useState<PatentData | null>(null);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(800);
  const scrolledRef = useRef(false);

  useEffect(() => {
    function resize() { if (containerRef.current) setWidth(containerRef.current.clientWidth); }
    resize();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, []);

  useEffect(() => {
    fetch("/data/patents.json").then(r => r.json()).then(d => { setData(d); setLoading(false); });
  }, []);

  // 用 URL 查询参数 ?anchor=wordcloud 替代 hash 锚点
  // 直接读 window.location.search，避免 SSR/static export 下的问题
  useEffect(() => {
    if (loading || !data || scrolledRef.current) return;
    const params = new URLSearchParams(window.location.search);
    const anchor = params.get("anchor");
    if (!anchor) return;

    scrolledRef.current = true;

    const timer = setTimeout(() => {
      const el = document.getElementById(anchor);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }, 600);

    return () => clearTimeout(timer);
  }, [loading, data]);

  if (loading) return <div className="page-section"><p style={{ textAlign: "center", padding: 50, color: "#888" }}>{t.loading}</p></div>;
  if (!data) return <div className="page-section"><p style={{ textAlign: "center", padding: 50, color: "#e74c3c" }}>{t.error}</p></div>;

  return (
    <div ref={containerRef}>
      {/* Stats Row */}
      <div id="stats" className="stats-row">
        <div className="stat-card"><div className="stat-num">{data.total}</div><div className="stat-label">{t.totalPatents}</div></div>
        <div className="stat-card"><div className="stat-num">{data.network.nodes.length}</div><div className="stat-label">{t.totalInventors}</div></div>
        <div className="stat-card"><div className="stat-num">{data.network.links.length}</div><div className="stat-label">{t.collaborations}</div></div>
        <div className="stat-card"><div className="stat-num">{data.techDistribution.length}</div><div className="stat-label">{t.techAreas}</div></div>
      </div>

      {/* Word Cloud */}
      <div id="wordcloud" className="page-section">
        <h2>{t.wordCloud}</h2>
        <WordCloud data={data.keywords} width={width} />
      </div>

      {/* Charts Row */}
      <div className="two-col">
        <div className="page-section">
          <BarChart data={data.techDistribution} title={t.techDist} width={Math.min(width, 500)} height={320} />
        </div>
        <div className="page-section">
          <BarChart data={data.typeStats} title={t.patentType} width={Math.min(width, 500)} height={320} />
        </div>
      </div>

      {/* Timeline */}
      <div className="page-section">
        <h2>{t.yearTrend}</h2>
        <Timeline data={data.yearStats} width={width} height={300} />
      </div>

      {/* Network */}
      <div id="network" className="page-section">
        <h2>{t.networkTitle}</h2>
        <NetworkGraph data={data.network} width={width} />
      </div>

      {/* Certificate Images */}
      <div className="page-section">
        <h2>{t.certs}</h2>
        <CertGallery t={t} />
      </div>

      {/* Table */}
      <div className="page-section">
        <h2>{t.patentList}</h2>
        <PatentTable data={data} t={t} />
      </div>
    </div>
  );
}
