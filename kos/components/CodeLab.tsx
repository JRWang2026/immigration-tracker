"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import type { Translation } from "@/lib/i18n";
import { DEMO_SCRIPTS } from "@/lib/demo-scripts";
import { loadPyodide, runPython } from "@/lib/pyodide";
import type { PyodideInstance } from "@/lib/pyodide";

export default function CodeLab({ t }: { t: Translation }) {
  const [activeFile, setActiveFile] = useState("api_fetch.py");
  const [customCode, setCustomCode] = useState("");
  const [output, setOutput] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [pyodide, setPyodide] = useState<PyodideInstance | null>(null);
  const [loadStatus, setLoadStatus] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [editorContent, setEditorContent] = useState("");
  const outputRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lineNumRef = useRef<HTMLDivElement>(null);

  const isCustom = activeFile === "custom";

  // Load Pyodide eagerly on mount
  useEffect(() => {
    if (loadStatus !== "idle") return;
    setLoadStatus("loading");

    loadPyodide()
      .then((py) => {
        setPyodide(py);
        setLoadStatus("ready");
      })
      .catch((err) => {
        console.error("Pyodide load failed:", err);
        setLoadStatus("error");
      });
  }, [loadStatus]);

  // Init editor content on mount and when tab changes
  useEffect(() => {
    if (isCustom) {
      if (!editorContent) {
        setEditorContent(customCode || t.codeLab.codePlaceholder);
      }
    } else {
      const script = DEMO_SCRIPTS[activeFile];
      if (script) {
        setEditorContent(script.code);
      }
    }
    // Reset custom code state when switching tabs
  }, [activeFile, isCustom]);

  // Auto-scroll output
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  // Sync line numbers scroll with textarea
  const syncScroll = useCallback(() => {
    if (textareaRef.current && lineNumRef.current) {
      lineNumRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  }, []);

  // Update line numbers when content changes
  const lineCount = editorContent.split("\n").length;

  // Update editor content handler
  const handleEditorChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const val = e.target.value;
      setEditorContent(val);
      if (isCustom) {
        setCustomCode(val);
      }
    },
    [isCustom]
  );

  // Handle tab key in textarea (insert spaces)
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Tab") {
        e.preventDefault();
        const textarea = e.currentTarget;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const val = textarea.value;
        const newVal = val.substring(0, start) + "    " + val.substring(end);
        setEditorContent(newVal);
        if (isCustom) setCustomCode(newVal);
        // Restore cursor position after React re-render
        requestAnimationFrame(() => {
          textarea.selectionStart = textarea.selectionEnd = start + 4;
        });
      }
    },
    [isCustom]
  );

  // Run code
  const handleRun = useCallback(async () => {
    if (!pyodide) return;

    setIsRunning(true);
    setOutput("");

    try {
      const codeToRun = editorContent;
      if (!codeToRun.trim()) {
        setOutput("Error: no code to execute");
        return;
      }

      const result = await runPython(pyodide, codeToRun);
      setOutput(result || "(no output)");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setOutput("Error:\n" + msg);
    } finally {
      setIsRunning(false);
    }
  }, [pyodide, editorContent]);

  // File upload handler
  const handleFileUpload = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      // Validate file type
      if (!file.name.endsWith(".py")) {
        setOutput("Error: only .py files are supported");
        return;
      }

      const reader = new FileReader();
      reader.onload = (ev) => {
        const content = ev.target?.result as string;
        setEditorContent(content);
        if (isCustom) setCustomCode(content);
        setActiveFile("custom");
        setOutput("");
      };
      reader.onerror = () => {
        setOutput("Error: failed to read file");
      };
      reader.readAsText(file, "UTF-8");

      // Reset file input so same file can be re-uploaded
      e.target.value = "";
    },
    [isCustom]
  );

  // Clear output
  const clearOutput = useCallback(() => setOutput(""), []);

  return (
    <div className="codelab-container">
      {/* Header */}
      <div className="codelab-header">
        <h1 className="section-title">{t.codeLab.title}</h1>
        <p className="section-subtitle">{t.codeLab.subtitle}</p>
      </div>

      {/* Tabs */}
      <div className="codelab-tabs">
        {t.codeLab.demos.map((demo) => (
          <button
            key={demo.name}
            className={`codelab-tab ${activeFile === demo.name ? "active" : ""}`}
            onClick={() => {
              setActiveFile(demo.name);
              setOutput("");
            }}
          >
            <span className="codelab-tab-dot" />
            {demo.label}
            <span className="codelab-tab-file">.py</span>
          </button>
        ))}
        <button
          className={`codelab-tab ${isCustom ? "active" : ""}`}
          onClick={() => {
            setActiveFile("custom");
            setOutput("");
          }}
        >
          <span className="codelab-tab-dot custom-dot" />
          {t.codeLab.custom}
        </button>
      </div>

      {/* Main layout: Editor | Output */}
      <div className="codelab-main">
        {/* Editor Panel */}
        <div className="codelab-editor-panel">
          <div className="codelab-editor-header">
            <span className="codelab-filename">
              {isCustom ? "custom.py" : activeFile}
            </span>
            <div className="codelab-editor-actions">
              {/* File upload button */}
              <button
                className="codelab-upload-btn"
                onClick={() => fileInputRef.current?.click()}
                title={t.codeLab.uploadPy}
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M7 1v8M3.5 5L7 1.5 10.5 5M1 10v2a1 1 0 001 1h10a1 1 0 001-1v-2" stroke="currentColor" strokeWidth="1.3" fill="none" />
                </svg>
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".py"
                onChange={handleFileUpload}
                style={{ display: "none" }}
              />
              <span className="codelab-lang-badge">Python 3</span>
            </div>
          </div>

          {/* Interactive Editor */}
          <div className="codelab-editor-body interactive">
            <div className="codelab-line-numbers" ref={lineNumRef}>
              {Array.from({ length: Math.max(lineCount, 1) }, (_, i) => (
                <span key={i}>{i + 1}</span>
              ))}
            </div>
            <textarea
              ref={textareaRef}
              className="codelab-textarea"
              value={editorContent}
              onChange={handleEditorChange}
              onKeyDown={handleKeyDown}
              onScroll={syncScroll}
              spellCheck={false}
              wrap="off"
              placeholder={t.codeLab.codePlaceholder}
            />
          </div>
        </div>

        {/* Run + Output Panel */}
        <div className="codelab-output-panel">
          <div className="codelab-output-header">
            <span>{t.codeLab.output}</span>
            <div className="codelab-output-actions">
              {loadStatus === "loading" && (
                <span className="codelab-status loading">
                  <span className="codelab-spinner" />
                  {t.codeLab.loading}
                </span>
              )}
              {loadStatus === "ready" && (
                <span className="codelab-status ready">{t.codeLab.ready.substring(0, 20)}</span>
              )}
              {loadStatus === "error" && (
                <span className="codelab-status error">Load failed</span>
              )}
              {output && (
                <button
                  className="codelab-clear-btn"
                  onClick={clearOutput}
                  title={t.codeLab.clearOutput}
                >
                  {t.codeLab.clearOutput}
                </button>
              )}
              <button
                className="codelab-run-btn"
                onClick={handleRun}
                disabled={isRunning || !pyodide}
              >
                {isRunning ? (
                  <>
                    <span className="codelab-spinner" />
                    {t.codeLab.running}
                  </>
                ) : (
                  <>
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <path d="M3 1.5L12 7L3 12.5V1.5Z" fill="currentColor" />
                    </svg>
                    {t.codeLab.run}
                  </>
                )}
              </button>
            </div>
          </div>
          <div className="codelab-output-content" ref={outputRef}>
            {output ? (
              <pre className="codelab-output-text">{output}</pre>
            ) : (
              <div className="codelab-output-placeholder">
                {loadStatus === "loading" && <p>{t.codeLab.loading}</p>}
                {loadStatus === "ready" && (
                  <p>
                    <span className="codelab-icon">▶</span>{" "}
                    {t.codeLab.ready}
                  </p>
                )}
                {loadStatus === "error" && (
                  <p style={{ color: "var(--red-500)" }}>
                    Failed to load Python runtime. Please refresh the page.
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
