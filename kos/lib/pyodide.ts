// Pyodide Python runtime loader — CDN-based, no bundling
// Pyodide is ~10MB, too large for static export; loaded on demand

const PYODIDE_VERSION = "0.26.2";
const PYODIDE_CDN = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

declare global {
  interface Window {
    loadPyodide: (opts?: { indexURL?: string }) => Promise<PyodideInstance>;
  }
}

interface PyodideInstance {
  runPython: (code: string) => unknown;
  runPythonAsync: (code: string) => Promise<unknown>;
  loadPackage: (names: string | string[]) => Promise<void>;
}

export type { PyodideInstance };

let pyodidePromise: Promise<PyodideInstance> | null = null;

export function loadPyodide(): Promise<PyodideInstance> {
  if (pyodidePromise) return pyodidePromise;

  pyodidePromise = new Promise((resolve, reject) => {
    if (typeof window === "undefined") {
      reject(new Error("Pyodide requires browser environment"));
      return;
    }

    const existingScript = document.querySelector(
      `script[src*="pyodide.js"]`
    );
    if (existingScript) {
      // Already loading, wait for it
      const checkInterval = setInterval(() => {
        if (window.loadPyodide) {
          clearInterval(checkInterval);
          resolve(window.loadPyodide({ indexURL: PYODIDE_CDN }));
        }
      }, 200);
      setTimeout(() => {
        clearInterval(checkInterval);
        reject(new Error("Pyodide load timeout"));
      }, 30000);
      return;
    }

    const script = document.createElement("script");
    script.src = `${PYODIDE_CDN}pyodide.js`;
    script.async = true;

    script.onload = async () => {
      try {
        const pyodide = await window.loadPyodide({
          indexURL: PYODIDE_CDN,
        });
        resolve(pyodide);
      } catch (e) {
        reject(e);
      }
    };

    script.onerror = () => {
      reject(new Error("Failed to load Pyodide script"));
    };

    document.head.appendChild(script);
  });

  return pyodidePromise;
}

export async function runPython(
  pyodide: PyodideInstance,
  code: string
): Promise<string> {
  // Redirect stdout to capture print() output
  pyodide.runPython(`
import sys
import io as _pyio
__stdout_capture = _pyio.StringIO()
sys.stdout = __stdout_capture
  `);

  await pyodide.runPythonAsync(code);

  const output = pyodide.runPython("__stdout_capture.getvalue()") as string;

  // Restore stdout
  pyodide.runPython("sys.stdout = sys.__stdout__");

  return output;
}
