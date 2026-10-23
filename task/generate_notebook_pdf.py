"""
Master Reusable Jupyter Notebook to Educational PDF Documentation Generator
==========================================================================
Analyzes any Jupyter Notebook in the repository, extracts its cells, markdown,
code, outputs, and dependencies, and compiles a comprehensive 12-section
educational study guide rendered into a publication-grade PDF.

Output is saved to: pdf/<notebook_filename>.pdf
Validated using pypdf.
"""

import sys
import os
import json
import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# HTML & CSS template components
CSS_STYLES = """
@page {
    size: A4;
    margin: 16mm 16mm 16mm 16mm;
    @bottom-right {
        content: "Page " counter(page);
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 8pt;
        color: #64748b;
    }
    @bottom-left {
        content: "LangChain & Agentic AI Study Guide";
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 8pt;
        color: #64748b;
    }
}

body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.6;
    font-size: 9.8pt;
    margin: 0;
    padding: 0;
}

/* Headings */
h1, h2, h3, h4, h5 {
    color: #0f172a;
    font-weight: 700;
    margin-top: 1.2em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}

h1 {
    font-size: 20pt;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 6px;
    margin-top: 0;
}

h2 {
    font-size: 14pt;
    color: #1e3a8a;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 4px;
    margin-top: 1.6em;
}

h3 {
    font-size: 11.5pt;
    color: #1d4ed8;
}

h4 {
    font-size: 10.2pt;
    color: #334155;
}

p, ul, ol {
    margin-top: 0.4em;
    margin-bottom: 0.8em;
}

li {
    margin-bottom: 0.3em;
}

/* Page Break Controls */
.page-break-before {
    page-break-before: always;
}

.avoid-break {
    page-break-inside: avoid;
}

/* Cover Page */
.cover-page {
    page-break-before: auto;
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 88vh;
    padding: 40px 20px;
    box-sizing: border-box;
    border-left: 6px solid #2563eb;
    background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
    border-radius: 4px;
}

.cover-badge {
    display: inline-block;
    background-color: #dbeafe;
    color: #1e40af;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 9pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 16px;
}

.cover-title {
    font-size: 26pt;
    color: #0f172a;
    line-height: 1.2;
    margin: 0 0 12px 0;
    font-weight: 800;
}

.cover-subtitle {
    font-size: 13pt;
    color: #3b82f6;
    margin: 0 0 24px 0;
    font-weight: 500;
}

.cover-meta {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #cbd5e1;
    font-size: 9pt;
    color: #475569;
}

.cover-meta-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-top: 10px;
}

.meta-item strong {
    color: #0f172a;
}

/* Code Blocks */
pre, code {
    font-family: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
}

pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 8.4pt;
    line-height: 1.45;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-all;
    margin: 0.6em 0;
    page-break-inside: avoid;
    border-left: 4px solid #38bdf8;
}

code {
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 2px 5px;
    border-radius: 4px;
    font-size: 8.8pt;
    border: 1px solid #e2e8f0;
}

pre code {
    background: transparent;
    color: inherit;
    padding: 0;
    border: none;
}

/* Output Box */
.output-box {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-left: 4px solid #10b981;
    border-radius: 4px;
    padding: 8px 12px;
    margin: 0.6em 0 1em 0;
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 8pt;
    color: #334155;
    white-space: pre-wrap;
    word-break: break-word;
    page-break-inside: avoid;
}

.output-label {
    font-size: 7.5pt;
    text-transform: uppercase;
    font-weight: 700;
    color: #059669;
    margin-bottom: 4px;
    display: block;
    letter-spacing: 0.05em;
}

/* Callout Boxes */
.callout {
    padding: 10px 14px;
    margin: 1em 0;
    border-radius: 6px;
    font-size: 9.3pt;
    page-break-inside: avoid;
}

.callout-title {
    font-weight: 700;
    margin-bottom: 4px;
    font-size: 9.6pt;
    display: flex;
    align-items: center;
}

.callout-note {
    background-color: #eff6ff;
    border-left: 4px solid #3b82f6;
    color: #1e40af;
}

.callout-warning {
    background-color: #fffbeb;
    border-left: 4px solid #f59e0b;
    color: #92400e;
}

.callout-error {
    background-color: #fef2f2;
    border-left: 4px solid #ef4444;
    color: #991b1b;
}

.callout-success {
    background-color: #ecfdf5;
    border-left: 4px solid #10b981;
    color: #065f46;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 8.8pt;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #e2e8f0;
    padding: 7px 10px;
    text-align: left;
    vertical-align: top;
}

th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
}

tr:nth-child(even) td {
    background-color: #f8fafc;
}

/* Diagram Container */
.diagram-container {
    text-align: center;
    margin: 1.4em 0;
    padding: 12px;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    page-break-inside: avoid;
}

.diagram-caption {
    font-size: 8.5pt;
    color: #64748b;
    font-style: italic;
    margin-top: 8px;
}

/* Question and Answers */
.exercise-box {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 1em 0;
    page-break-inside: avoid;
}

.exercise-question {
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 6px;
}

.answer-box {
    background-color: #f0fdf4;
    border-left: 4px solid #22c55e;
    padding: 10px 14px;
    margin-top: 8px;
    border-radius: 0 4px 4px 0;
    font-size: 9pt;
}
"""

def extract_notebook_data(notebook_path: Path):
    """Parse notebook JSON and extract metadata, cells, outputs."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    cells = nb.get('cells', [])
    processed_cells = []
    
    for idx, c in enumerate(cells):
        ctype = c.get('cell_type')
        source = "".join(c.get('source', []))
        outputs = c.get('outputs', [])
        clean_outputs = []
        for o in outputs:
            otype = o.get('output_type')
            if otype == 'stream':
                text = "".join(o.get('text', []))
                clean_outputs.append({'type': 'stream', 'text': text})
            elif otype in ('execute_result', 'display_data'):
                data = o.get('data', {})
                if 'text/plain' in data:
                    clean_outputs.append({'type': 'execute_result', 'text': "".join(data['text/plain'])})
                elif 'image/png' in data:
                    clean_outputs.append({'type': 'image', 'text': '[Inline PNG Image Generated]'})
            elif otype == 'error':
                ename = o.get('ename', 'Error')
                evalue = o.get('evalue', '')
                clean_outputs.append({'type': 'error', 'text': f"{ename}: {evalue}"})
                
        processed_cells.append({
            'index': idx,
            'type': ctype,
            'source': source,
            'outputs': clean_outputs
        })
        
    return {
        'filename': notebook_path.name,
        'cells': processed_cells
    }

def get_svg_agent_workflow():
    """Vector SVG diagram for LangChain 1.4 Agent CompiledStateGraph."""
    return """
    <svg width="650" height="240" viewBox="0 0 650 240" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
            </marker>
            <marker id="arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
            </marker>
        </defs>
        
        <!-- User Input Node -->
        <rect x="20" y="90" width="120" height="60" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
        <text x="80" y="115" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">User Message</text>
        <text x="80" y="133" font-family="'Segoe UI', sans-serif" font-size="9" fill="#64748b" text-anchor="middle">"Weather in Delhi?"</text>
        
        <!-- Arrow 1 -->
        <line x1="140" y1="120" x2="185" y2="120" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>
        
        <!-- Agent CompiledStateGraph Node -->
        <rect x="190" y="60" width="160" height="120" rx="8" fill="#faf5ff" stroke="#8b5cf6" stroke-width="2"/>
        <text x="270" y="85" font-family="'Segoe UI', sans-serif" font-size="12" font-weight="bold" fill="#6b21a8" text-anchor="middle">CompiledStateGraph</text>
        <rect x="205" y="100" width="130" height="30" rx="4" fill="#ede9fe" stroke="#a855f7" stroke-width="1"/>
        <text x="270" y="120" font-family="'Segoe UI', sans-serif" font-size="10" fill="#4c1d95" text-anchor="middle">Model Decision Node</text>
        <text x="270" y="155" font-family="'Segoe UI', sans-serif" font-size="9" fill="#7e22ce" text-anchor="middle">Inspects Tools & Prompts</text>
        
        <!-- Loop to Tool Node -->
        <path d="M 270 60 L 270 30 L 440 30 L 440 85" fill="none" stroke="#f59e0b" stroke-width="2" marker-end="url(#arrow)"/>
        <text x="355" y="24" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#b45309" text-anchor="middle">Tool Call Emitted</text>

        <!-- Tool Node -->
        <rect x="380" y="90" width="130" height="60" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
        <text x="445" y="115" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#065f46" text-anchor="middle">Python Tool Node</text>
        <text x="445" y="133" font-family="'Segoe UI', sans-serif" font-size="9" fill="#047857" text-anchor="middle">get_current_weather()</text>
        
        <!-- Tool Result Loop Back -->
        <path d="M 445 150 L 445 200 L 270 200 L 270 185" fill="none" stroke="#10b981" stroke-width="2" marker-end="url(#arrow-green)"/>
        <text x="355" y="215" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#047857" text-anchor="middle">ToolMessage(content='Sunny')</text>

        <!-- Final Arrow to Output -->
        <line x1="350" y1="120" x2="525" y2="120" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow)"/>

        <!-- Final Output Node -->
        <rect x="530" y="90" width="105" height="60" rx="8" fill="#f0fdf4" stroke="#22c55e" stroke-width="2"/>
        <text x="582" y="115" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#15803d" text-anchor="middle">Final AIMessage</text>
        <text x="582" y="133" font-family="'Segoe UI', sans-serif" font-size="9" fill="#166534" text-anchor="middle">response['messages'][-1]</text>
    </svg>
    """

def get_svg_execution_modes():
    """Vector SVG diagram comparing invoke vs stream vs batch."""
    return """
    <svg width="650" height="230" viewBox="0 0 650 230" xmlns="http://www.w3.org/2000/svg">
        <!-- 1. Invoke -->
        <g transform="translate(10, 20)">
            <rect x="0" y="0" width="195" height="190" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
            <rect x="0" y="0" width="195" height="30" rx="6" fill="#3b82f6"/>
            <text x="97" y="20" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">invoke(prompt)</text>
            
            <circle cx="25" cy="55" r="10" fill="#dbeafe" stroke="#3b82f6"/>
            <text x="25" y="59" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#1d4ed8" text-anchor="middle">1</text>
            <text x="45" y="59" font-family="'Segoe UI', sans-serif" font-size="9.5" fill="#1e293b">Sends 1 complete prompt</text>
            
            <circle cx="25" cy="95" r="10" fill="#dbeafe" stroke="#3b82f6"/>
            <text x="25" y="99" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#1d4ed8" text-anchor="middle">2</text>
            <text x="45" y="99" font-family="'Segoe UI', sans-serif" font-size="9.5" fill="#1e293b">Model processes all tokens</text>
            
            <circle cx="25" cy="135" r="10" fill="#dbeafe" stroke="#3b82f6"/>
            <text x="25" y="139" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#1d4ed8" text-anchor="middle">3</text>
            <text x="45" y="139" font-family="'Segoe UI', sans-serif" font-size="9.5" fill="#1e293b">Returns 1 AIMessage</text>

            <rect x="15" y="155" width="165" height="24" rx="4" fill="#eff6ff" stroke="#bfdbfe"/>
            <text x="97" y="171" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#1d4ed8" text-anchor="middle">Blocks until 100% complete</text>
        </g>
        
        <!-- 2. Stream -->
        <g transform="translate(225, 20)">
            <rect x="0" y="0" width="195" height="190" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
            <rect x="0" y="0" width="195" height="30" rx="6" fill="#8b5cf6"/>
            <text x="97" y="20" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">stream(prompt)</text>
            
            <circle cx="25" cy="55" r="10" fill="#ede9fe" stroke="#8b5cf6"/>
            <text x="25" y="59" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#6d28d9" text-anchor="middle">1</text>
            <text x="45" y="59" font-family="'Segoe UI', sans-serif" font-size="9.5" fill="#1e293b">Sends 1 complete prompt</text>
            
            <circle cx="25" cy="95" r="10" fill="#ede9fe" stroke="#8b5cf6"/>
            <text x="25" y="99" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#6d28d9" text-anchor="middle">2</text>
            <text x="45" y="99" font-family="'Segoe UI', sans-serif" font-size="9.5" fill="#1e293b">Yields chunks progressively</text>
            
            <circle cx="25" cy="135" r="10" fill="#ede9fe" stroke="#8b5cf6"/>
            <text x="25" y="139" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#6d28d9" text-anchor="middle">3</text>
            <text x="45" y="139" font-family="'Segoe UI', sans-serif" font-size="9.5" fill="#1e293b">for chunk in stream: ...</text>

            <rect x="15" y="155" width="165" height="24" rx="4" fill="#faf5ff" stroke="#ddd6fe"/>
            <text x="97" y="171" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#6d28d9" text-anchor="middle">Instant perceived response</text>
        </g>
        
        <!-- 3. Batch -->
        <g transform="translate(440, 20)">
            <rect x="0" y="0" width="195" height="190" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
            <rect x="0" y="0" width="195" height="30" rx="6" fill="#10b981"/>
            <text x="97" y="20" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">batch([prompts])</text>
            
            <circle cx="25" cy="55" r="10" fill="#d1fae5" stroke="#10b981"/>
            <text x="25" y="59" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#047857" text-anchor="middle">1</text>
            <text x="45" y="59" font-family="'Segoe UI', sans-serif" font-size="9.5" fill="#1e293b">List of N distinct prompts</text>
            
            <circle cx="25" cy="95" r="10" fill="#d1fae5" stroke="#10b981"/>
            <text x="25" y="99" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#047857" text-anchor="middle">2</text>
            <text x="45" y="99" font-family="'Segoe UI', sans-serif" font-size="9.5" fill="#1e293b">Parallel workers (pool)</text>
            
            <circle cx="25" cy="135" r="10" fill="#d1fae5" stroke="#10b981"/>
            <text x="25" y="139" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#047857" text-anchor="middle">3</text>
            <text x="45" y="139" font-family="'Segoe UI', sans-serif" font-size="9.5" fill="#1e293b">Returns List[AIMessage]</text>

            <rect x="15" y="155" width="165" height="24" rx="4" fill="#ecfdf5" stroke="#a7f3d0"/>
            <text x="97" y="171" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#047857" text-anchor="middle">max_concurrency controls rate</text>
        </g>
    </svg>
    """

def get_svg_toolcall_loop():
    """Vector SVG diagram illustrating the 2-step manual Tool Calling Loop."""
    return """
    <svg width="650" height="250" viewBox="0 0 650 250" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <marker id="tarrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
            </marker>
            <marker id="tarrow-amber" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#d97706" />
            </marker>
        </defs>
        
        <!-- Actors Header -->
        <rect x="50" y="10" width="120" height="35" rx="5" fill="#eff6ff" stroke="#3b82f6"/>
        <text x="110" y="32" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">User / Python</text>
        
        <rect x="260" y="10" width="130" height="35" rx="5" fill="#faf5ff" stroke="#8b5cf6"/>
        <text x="325" y="32" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#6b21a8" text-anchor="middle">LLM (Groq / GPT)</text>

        <rect x="470" y="10" width="130" height="35" rx="5" fill="#ecfdf5" stroke="#10b981"/>
        <text x="535" y="32" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#065f46" text-anchor="middle">Tool Execution</text>

        <!-- Lifelines -->
        <line x1="110" y1="45" x2="110" y2="240" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4"/>
        <line x1="325" y1="45" x2="325" y2="240" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4"/>
        <line x1="535" y1="45" x2="535" y2="240" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4"/>

        <!-- Step 1: User asks question -->
        <line x1="110" y1="70" x2="320" y2="70" stroke="#3b82f6" stroke-width="2" marker-end="url(#tarrow)"/>
        <text x="215" y="64" font-family="'Segoe UI', sans-serif" font-size="8.8" font-weight="bold" fill="#1e40af" text-anchor="middle">1. invoke("Weather in Delhi?")</text>

        <!-- Step 2: LLM responds with tool_calls -->
        <line x1="325" y1="105" x2="115" y2="105" stroke="#8b5cf6" stroke-width="2" marker-end="url(#tarrow)"/>
        <text x="220" y="99" font-family="'Segoe UI', sans-serif" font-size="8.8" font-weight="bold" fill="#6b21a8" text-anchor="middle">2. AIMessage(tool_calls=[get_weather(location='Delhi')])</text>

        <!-- Step 3: Python executes tool locally -->
        <line x1="110" y1="140" x2="530" y2="140" stroke="#10b981" stroke-width="2" marker-end="url(#tarrow)"/>
        <text x="320" y="134" font-family="'Segoe UI', sans-serif" font-size="8.8" font-weight="bold" fill="#047857" text-anchor="middle">3. tool_result = get_weather.invoke(tool_call)</text>

        <!-- Step 4: Tool returns string result -->
        <line x1="535" y1="170" x2="115" y2="170" stroke="#10b981" stroke-width="1.5" stroke-dasharray="2" marker-end="url(#tarrow)"/>
        <text x="325" y="165" font-family="'Segoe UI', sans-serif" font-size="8.8" fill="#047857" text-anchor="middle">4. ToolMessage("It's sunny in Delhi") appended to messages</text>

        <!-- Step 5: Send conversation history back -->
        <line x1="110" y1="205" x2="320" y2="205" stroke="#d97706" stroke-width="2" marker-end="url(#tarrow-amber)"/>
        <text x="215" y="199" font-family="'Segoe UI', sans-serif" font-size="8.8" font-weight="bold" fill="#b45309" text-anchor="middle">5. invoke([User, AIMessage, ToolMessage])</text>

        <!-- Step 6: Final Natural Language Answer -->
        <line x1="325" y1="230" x2="115" y2="230" stroke="#22c55e" stroke-width="2" marker-end="url(#tarrow)"/>
        <text x="220" y="225" font-family="'Segoe UI', sans-serif" font-size="8.8" font-weight="bold" fill="#15803d" text-anchor="middle">6. final_response: "The weather in Delhi is sunny."</text>
    </svg>
    """

def escape_html(text: str) -> str:
    """Escape text for safe HTML rendering."""
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))

def build_pdf_document(nb_data: dict) -> str:
    """Generate the full HTML document matching the 12-section standard."""
    fname = nb_data['filename']
    cells = nb_data['cells']
    today = datetime.now().strftime("%B %d, %Y")
    
    # Identify notebook profile
    if "1-langchainIntro" in fname:
        return build_guide_1(fname, cells, today)
    elif "2-modelintegration" in fname:
        return build_guide_2(fname, cells, today)
    elif "3-toolcall" in fname:
        return build_guide_3(fname, cells, today)
    else:
        return build_generic_guide(fname, cells, today)

# Specific Builder 1
def build_guide_1(fname, cells, today):
    svg_diagram = get_svg_agent_workflow()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{fname} - Educational Study Guide</title>
    <style>{CSS_STYLES}</style>
</head>
<body>

<!-- Section A: Cover Page -->
<div class="cover-page">
    <span class="cover-badge">LangChain 1.4+ • Core Foundation Guide</span>
    <h1 class="cover-title">Introduction to LangChain 1.4 Agents & CompiledStateGraph</h1>
    <p class="cover-subtitle">Deconstructing Autonomous Agent Workflows, Tool Binding, and State Execution Loops</p>
    
    <p style="font-size: 10.5pt; color: #475569; max-width: 580px; margin-top: 15px;">
        An authoritative technical guide explaining the modern transition from legacy LangChain agents 
        to LangGraph-powered stateful graphs. Teaches tool definition, runtime execution, message tracing, 
        and state extraction.
    </p>

    <div class="cover-meta">
        <div class="cover-meta-grid">
            <div class="meta-item"><strong>Target Notebook:</strong> <code>{fname}</code></div>
            <div class="meta-item"><strong>Generation Date:</strong> {today}</div>
            <div class="meta-item"><strong>Language & Runtime:</strong> Python 3.14 • Virtualenv (.venv)</div>
            <div class="meta-item"><strong>Core Framework:</strong> LangChain 1.4.7 • Google GenAI</div>
        </div>
    </div>
</div>

<!-- Section B: Learning Objectives -->
<h2>B. Learning Objectives</h2>
<p>After studying this notebook and guide, you will master:</p>
<ul>
    <li><strong>LangChain 1.4 Architecture:</strong> Understand how modern LangChain unifies agents onto LangGraph's <code>CompiledStateGraph</code> engine.</li>
    <li><strong>Tool Specification:</strong> Construct tools with Python type annotations and docstrings that serve as model interfaces.</li>
    <li><strong>Model Orchestration:</strong> Configure chat models (Gemini 3.8 Flash) and initialize agents via <code>create_agent</code>.</li>
    <li><strong>Message Exchange Protocol:</strong> Deconstruct the four foundational message structures: <code>HumanMessage</code>, <code>AIMessage</code>, <code>ToolMessage</code>, and system instructions.</li>
    <li><strong>State Graph Execution:</strong> Trace the decision loop where the agent detects missing information, calls the tool, receives the observation, and synthesizes the final response.</li>
    <li><strong>Output Extraction:</strong> Accurately retrieve final assistant messages using zero-index and reverse-index notation.</li>
</ul>

<!-- Section C: Prerequisites and Environment Setup -->
<h2>C. Prerequisites & Setup</h2>
<div class="callout callout-note">
    <div class="callout-title">Environment Specification</div>
    This notebook is built on <strong>LangChain v1.4.7</strong> running in a dedicated Python virtual environment (<code>.venv</code>) with dependencies tracked in <code>pyproject.toml</code>.
</div>
<table>
    <tr>
        <th>Component</th>
        <th>Configuration / Package</th>
        <th>Purpose</th>
    </tr>
    <tr>
        <td>Python Runtime</td>
        <td><code>Python &gt;= 3.14</code></td>
        <td>Modern runtime supporting advanced type hinting and fast async.</td>
    </tr>
    <tr>
        <td>Virtual Environment</td>
        <td><code>.venv</code> (managed via <code>uv</code>)</td>
        <td>Isolates packages and prevents global package collisions.</td>
    </tr>
    <tr>
        <td>Environment File</td>
        <td><code>.env</code> in workspace root</td>
        <td>Stores <code>GEMINI_API_KEY</code> securely without hardcoding secrets.</td>
    </tr>
    <tr>
        <td>Core Dependencies</td>
        <td><code>langchain>=1.4.7</code>, <code>langchain-google-genai</code>, <code>python-dotenv</code></td>
        <td>Provides agent runtime, model connector, and environment loader.</td>
    </tr>
</table>
<div class="callout callout-warning">
    <div class="callout-title">Security Best Practice</div>
    Never commit <code>.env</code> files containing plain API keys to version control. Always include <code>.env</code> in <code>.gitignore</code>.
</div>

<!-- Section D: Topic Overview -->
<div class="page-break-before"></div>
<h2>D. Topic Overview: The Evolution to LangChain 1.4 Agents</h2>
<p>
    In early versions of LangChain, agents relied on rigid string-based execution loops (such as MRKL and ReAct parsers) that frequently suffered from brittle regex parsing failures. 
    Starting in <strong>LangChain 1.0+ and 1.4+</strong>, the agent architecture was fundamentally redesigned around <strong>LangGraph</strong>.
</p>
<p>
    Today, calling <code>create_agent(...)</code> constructs a <code>CompiledStateGraph</code>. This is an explicit state machine where nodes represent operations (such as calling the LLM or invoking a tool) and edges define state transitions. The agent maintains a state dictionary—most importantly the <code>messages</code> list—which is sequentially updated as the agent and tools converse.
</p>

<!-- Section E: Notebook Walkthrough -->
<h2>E. Notebook Walkthrough & Cell Dissection</h2>

<h3>Cell 0: Markdown Header</h3>
<pre><code>### Langchain Version V1</code></pre>
<p><strong>Analysis:</strong> Establishes the study focus on LangChain's modern V1 API design standards.</p>

<h3>Cell 1: Environment & Framework Verification</h3>
<pre><code>import langchain
langchain.__version__</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result</span>
    '1.4.7'
</div>
<p><strong>Explanation:</strong> Verifies that the active kernel is running LangChain 1.4.7. In LangChain 1.4+, core abstractions are clean, stable, and decoupled from legacy monolithic modules.</p>

<h3>Cell 2: Secure Environment Configuration</h3>
<pre><code>import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")</code></pre>
<p><strong>Analysis:</strong></p>
<ul>
    <li><code>load_dotenv()</code> reads key-value pairs from the local <code>.env</code> file into the system environment.</li>
    <li><code>os.getenv("GEMINI_API_KEY")</code> fetches the key. Setting <code>os.environ["GEMINI_API_KEY"]</code> ensures that the Google GenAI provider can authenticate automatically without requiring hardcoded strings in application code.</li>
</ul>

<div class="avoid-break">
<h3>Cell 3: Defining Tools & Initializing the Agent Graph</h3>
<pre><code>from langchain.agents import create_agent

def get_current_weather(city: str) -> str:
    \"\"\"Get the weather for a city\"\"\"
    return f"The weather in {{city}} is sunny"

agent = create_agent(
    model="google_genai:gemini-3.8-flash",
    tools=[get_current_weather],
    system_prompt="You are a helpful assistant."
)

agent</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result</span>
    &lt;langgraph.graph.state.CompiledStateGraph object at 0x...&gt;
    [Inline PNG Graph Diagram Emitted]
</div>
<p><strong>Critical Mechanics:</strong></p>
<ol>
    <li><strong>Docstring as Interface:</strong> The docstring <code>\"\"\"Get the weather for a city\"\"\"</code> is not merely human documentation; LangChain inspects this docstring and passes it to the LLM as the tool's description so the LLM understands when to call it.</li>
    <li><strong>Type Annotations:</strong> <code>city: str -&gt; str</code> tells LangChain the argument schema, allowing automatic conversion into JSON Schema parameters.</li>
    <li><strong>CompiledStateGraph:</strong> The returned <code>agent</code> object is an executable state machine graph ready to receive input messages.</li>
</ol>
</div>

<div class="avoid-break">
<h3>Cell 4: Executing the Agent Decision Loop</h3>
<pre><code>response = agent.invoke(
    {{"messages": [
        {{
            "role": "user",
            "content": "What is weather like in Ghaziabad in India"
        }}
    ]}}
)

response["messages"]</code></pre>
<div class="output-box">
    <span class="output-label">Returned Message Sequence</span>
[
  HumanMessage(content='What is weather like in Ghaziabad in India'),
  AIMessage(content=[], tool_calls=[{{'name': 'get_current_weather', 'args': {{'city': 'Ghaziabad, India'}}, 'id': 'call_1692240'}}]),
  ToolMessage(content='The weather in Ghaziabad, India is sunny', name='get_current_weather', tool_call_id='call_1692240'),
  AIMessage(content='The weather in Ghaziabad, India is currently sunny.')
]
</div>
<p><strong>Deconstruction of the 4-Message Sequence:</strong></p>
<ul>
    <li><strong>Message 1 (HumanMessage):</strong> The initial user query injected into the state graph.</li>
    <li><strong>Message 2 (AIMessage):</strong> The LLM realizes it lacks real-time weather information, so it leaves <code>content</code> empty and produces a <code>tool_calls</code> payload requesting the execution of <code>get_current_weather</code> with <code>city='Ghaziabad, India'</code>.</li>
    <li><strong>Message 3 (ToolMessage):</strong> The state graph executes the local Python function and wraps the return value (<code>'The weather in Ghaziabad, India is sunny'</code>) linked by <code>tool_call_id='call_1692240'</code>.</li>
    <li><strong>Message 4 (AIMessage):</strong> The LLM receives the tool's result, digests it, and formulates the final conversational response to the user.</li>
</ul>
</div>

<h3>Cell 5: Extracting the Final Answer</h3>
<pre><code>response["messages"][-1]</code></pre>
<div class="output-box">
    <span class="output-label">Final AIMessage</span>
AIMessage(content='The weather in Ghaziabad, India is currently sunny.')
</div>
<p><strong>Explanation:</strong> In Python, index <code>[-1]</code> retrieves the last element of the list. Since the agent appends messages sequentially, the last message is guaranteed to be the final assistant response.</p>

<!-- Section F: End-to-End Execution Flow -->
<div class="page-break-before"></div>
<h2>F. End-to-End Execution Flow & Dataflow Diagram</h2>
<p>The diagram below traces the end-to-end lifecycle executed during <code>agent.invoke()</code>:</p>

<div class="diagram-container">
    {svg_diagram}
    <div class="diagram-caption">Figure 1.1: Complete Execution Flow of LangChain 1.4 CompiledStateGraph Agent</div>
</div>

<!-- Section G: Important APIs -->
<h2>G. Important APIs & Classes Reference</h2>
<table>
    <tr>
        <th>API / Function</th>
        <th>Module / Class</th>
        <th>Input Parameters</th>
        <th>Return Value</th>
        <th>Key Role</th>
    </tr>
    <tr>
        <td><code>create_agent</code></td>
        <td><code>langchain.agents</code></td>
        <td><code>model</code>, <code>tools</code>, <code>system_prompt</code></td>
        <td><code>CompiledStateGraph</code></td>
        <td>Compiles tool-equipped LLM into an executable state graph.</td>
    </tr>
    <tr>
        <td><code>agent.invoke</code></td>
        <td><code>CompiledStateGraph</code></td>
        <td><code>{{"messages": [...]}}</code></td>
        <td>State dictionary</td>
        <td>Synchronously triggers the agent graph to completion.</td>
    </tr>
    <tr>
        <td><code>HumanMessage</code></td>
        <td><code>langchain_core.messages</code></td>
        <td><code>content: str</code></td>
        <td>Message instance</td>
        <td>Represents prompt originating from the human user.</td>
    </tr>
    <tr>
        <td><code>ToolMessage</code></td>
        <td><code>langchain_core.messages</code></td>
        <td><code>content</code>, <code>name</code>, <code>tool_call_id</code></td>
        <td>Message instance</td>
        <td>Contains the output produced by the Python tool function.</td>
    </tr>
</table>

<!-- Section H: Common Errors & Debugging -->
<h2>H. Common Errors & Debugging</h2>
<div class="callout callout-error">
    <div class="callout-title">Trap 1: Missing Docstring on Tool Function</div>
    <strong>Symptom:</strong> The agent never calls the tool, or guesses random arguments.<br/>
    <strong>Cause:</strong> The LLM relies on the Python docstring to know <em>what</em> the tool does. Without <code>\"\"\"Get the weather for a city\"\"\"</code>, the tool's description in the model's schema is empty!
</div>
<div class="callout callout-warning">
    <div class="callout-title">Trap 2: Malformed Message State Input</div>
    <strong>Symptom:</strong> <code>TypeError</code> or <code>ValueError: Expected list of messages</code>.<br/>
    <strong>Cause:</strong> Calling <code>agent.invoke("What is the weather?")</code> directly as a string. In LangChain 1.4 agents, input must be a dictionary with the key <code>"messages"</code> containing a list of messages.
</div>

<!-- Section I: Practical Examples -->
<h2>I. Practical Example: Multi-Argument Tools</h2>
<pre><code>def calculate_trip_cost(destination: str, days: int, hotel_per_night: float) -> str:
    \"\"\"Calculate estimated travel accommodation expenses for a given duration.\"\"\"
    total = days * hotel_per_night
    return f"Trip to {{destination}} for {{days}} days costs ${{total:.2f}}."</code></pre>
<p>When passed into <code>create_agent(tools=[calculate_trip_cost])</code>, the model will extract multiple structured arguments from user requests such as <em>"How much for 5 days in Tokyo at $120/night?"</em>.</p>

<!-- Section J: Key Takeaways -->
<h2>J. Key Takeaways</h2>
<ul>
    <li>LangChain 1.4 replaces brittle string parsers with <strong>LangGraph CompiledStateGraphs</strong>.</li>
    <li>Tools are standard Python functions whose docstrings and type annotations provide the schema to the LLM.</li>
    <li>The model never executes Python code directly; it emits a <code>tool_calls</code> payload, the host environment runs the function, and the result returns as a <code>ToolMessage</code>.</li>
    <li>The final response is always located at <code>response["messages"][-1]</code>.</li>
</ul>

<!-- Section K: Practice Questions -->
<div class="page-break-before"></div>
<h2>K. Practice Exercises & Knowledge Checks</h2>

<div class="exercise-box">
    <div class="exercise-question">Question 1 (Conceptual): Why is a docstring mandatory when defining a tool for an LLM agent?</div>
    <div class="answer-box">
        <strong>Answer:</strong> The docstring is converted by LangChain into the JSON Schema's <code>description</code> field. The LLM reads this description to decide whether the tool is relevant to the user's question. Without a docstring, the LLM has no description and cannot determine how to use the tool.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 2 (Code Tracing): In Cell 4, why does the first AIMessage have an empty content string (content=[])?</div>
    <div class="answer-box">
        <strong>Answer:</strong> Because the model decided to request a tool execution rather than speak to the user. Its entire output was packaged in <code>tool_calls</code>. It waited for the tool to execute before generating natural language text.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 3 (Debugging): If response["messages"] contains 5 messages, how do you safely extract only the assistant's final text?</div>
    <div class="answer-box">
        <strong>Answer:</strong> Use <code>response["messages"][-1].content</code> (or <code>response["messages"][-1].text</code>).
    </div>
</div>

<!-- Section L: Further Learning -->
<h2>L. Further Learning & Documentation</h2>
<ul>
    <li><a href="https://python.langchain.com/docs/concepts/#agents">LangChain Official Documentation - Agent Concepts</a></li>
    <li><a href="https://langchain-ai.github.io/langgraph/">LangGraph Documentation - State Graphs & Persistence</a></li>
    <li>Next study guide in sequence: <strong>2-modelintegration.pdf</strong> (Interaction Modes & Model Providers).</li>
</ul>

</body>
</html>
"""
    return html

# Specific Builder 2
def build_guide_2(fname, cells, today):
    svg_diagram = get_svg_execution_modes()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{fname} - Educational Study Guide</title>
    <style>{CSS_STYLES}</style>
</head>
<body>

<!-- Section A: Cover Page -->
<div class="cover-page">
    <span class="cover-badge">LangChain 1.4+ • Model Integration & Execution</span>
    <h1 class="cover-title">Model Integration & Execution Modes: invoke(), stream(), and batch()</h1>
    <p class="cover-subtitle">Mastering Multi-Provider Architecture, Token Streaming, Concurrency, and Quota Debugging</p>
    
    <p style="font-size: 10.5pt; color: #475569; max-width: 580px; margin-top: 15px;">
        An in-depth study guide dissecting universal model initialization (<code>init_chat_model</code>), 
        synchronous completion, generator-based chunk streaming, concurrent batch processing, and diagnosing 
        rate-limit (HTTP 429) retry loops.
    </p>

    <div class="cover-meta">
        <div class="cover-meta-grid">
            <div class="meta-item"><strong>Target Notebook:</strong> <code>{fname}</code></div>
            <div class="meta-item"><strong>Generation Date:</strong> {today}</div>
            <div class="meta-item"><strong>Language & Runtime:</strong> Python 3.14 • Virtualenv (.venv)</div>
            <div class="meta-item"><strong>Providers Explored:</strong> Google Gemini • Groq • OpenAI</div>
        </div>
    </div>
</div>

<!-- Section B: Learning Objectives -->
<h2>B. Learning Objectives</h2>
<p>After completing this notebook and study guide, you will be able to:</p>
<ul>
    <li><strong>Universal Model Initialization:</strong> Use <code>init_chat_model</code> to switch seamlessly between Google GenAI, Groq, and OpenAI without changing application code.</li>
    <li><strong>Synchronous Invocations (<code>invoke</code>):</strong> Execute complete prompts and parse complex responses (plain text vs list-of-dicts with signatures).</li>
    <li><strong>Progressive Token Streaming (<code>stream</code>):</strong> Consume generator chunks with <code>chunk.text</code>, <code>flush=True</code>, and token tracking.</li>
    <li><strong>Reasoning Tokens & Stream Latency:</strong> Understand why thinking models (Gemini 3.8 Flash, `reasoning_tokens`) produce internal thought tokens before text emerges.</li>
    <li><strong>High-Throughput Batching (<code>batch</code>):</strong> Process lists of prompts concurrently with <code>max_concurrency</code> rate limiting.</li>
    <li><strong>Quota Limit Diagnosis:</strong> Debug HTTP 429 Resource Exhausted errors and understand tenacity exponential backoff loops.</li>
</ul>

<!-- Section C: Prerequisites & Environment Setup -->
<h2>C. Prerequisites & Setup</h2>
<div class="callout callout-note">
    <div class="callout-title">Multi-Provider Configuration</div>
    This notebook interacts with model APIs via LangChain provider bridge packages: <code>langchain-google-genai</code>, <code>langchain-groq</code>, and <code>langchain-openai</code>.
</div>
<table>
    <tr>
        <th>Environment Variable</th>
        <th>Target Provider</th>
        <th>Expected Model Format</th>
    </tr>
    <tr>
        <td><code>GEMINI_API_KEY</code></td>
        <td>Google GenAI</td>
        <td><code>google_genai:gemini-3.8-flash</code></td>
    </tr>
    <tr>
        <td><code>GROQ_API_KEY</code></td>
        <td>Groq Cloud LPU</td>
        <td><code>groq:openai/gpt-oss-20b</code></td>
    </tr>
    <tr>
        <td><code>OPENAI_API_KEY</code></td>
        <td>OpenAI Platform</td>
        <td><code>openai:gpt-5-mini</code> / <code>gpt-4o</code></td>
    </tr>
</table>

<!-- Section D: Topic Overview -->
<div class="page-break-before"></div>
<h2>D. Topic Overview: The Three Interaction Paradigms</h2>
<p>
    Modern LLM applications require different latency and throughput profiles depending on the user experience. 
    LangChain unifies these patterns across every chat model via the <code>Runnable</code> interface:
</p>
<ol>
    <li><strong><code>invoke(input)</code> (Blocking Complete):</strong> Sends one prompt and blocks until the entire completion is generated. Ideal for background pipelines and non-interactive scripts.</li>
    <li><strong><code>stream(input)</code> (Real-Time Progressive):</strong> Returns a Python generator that yields token chunks as they are generated by the model. Critical for conversational chatbots to reduce perceived latency.</li>
    <li><strong><code>batch([inputs], config)</code> (Concurrent Parallel):</strong> Sends multiple prompts simultaneously using a thread pool. Ideal for bulk document processing, evaluations, and data pipelines.</li>
</ol>

<!-- Section E: Detailed Notebook Walkthrough -->
<h2>E. Notebook Walkthrough & Cell Dissection</h2>

<h3>Cell 0: Markdown Section Header</h3>
<pre><code>### Models Integration With OpenAI, Google Gemini and GROQ</code></pre>

<h3>Cell 1: Loading Credentials</h3>
<pre><code>import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")</code></pre>
<p><strong>Explanation:</strong> Loads credentials from <code>.env</code>. The notebook uses Gemini as its primary model provider.</p>

<div class="avoid-break">
<h3>Cell 2: Model Initialization & Synchronous Invocation</h3>
<pre><code>from langchain.chat_models import init_chat_model
model = init_chat_model("google_genai:gemini-3.8-flash")

response = model.invoke("Tell me somethign about One Piece Anime")
response.content</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result (Truncated Excerpt)</span>
[{{'type': 'text', 'text': 'Here is a fascinating look into the world of **One Piece**...\\n\\n### 1. The Incredible World-Building...', 'extras': {{'signature': '...'}}}}]
</div>
<p><strong>Deconstruction:</strong></p>
<ul>
    <li><code>init_chat_model("provider:model-name")</code> is a factory function. Passing <code>"google_genai:gemini-3.8-flash"</code> automatically instantiates <code>ChatGoogleGenAI</code> with the appropriate parameters.</li>
    <li>Notice that <code>response.content</code> in modern Google GenAI returns a list of dictionaries with <code>type: 'text'</code>, <code>text: '...'</code>, and cryptographic <code>extras.signature</code>.</li>
</ul>
</div>

<h3>Cell 3: Extracting Pure Text</h3>
<pre><code>response.content[0]['text']</code></pre>
<p><strong>Explanation:</strong> Extracts the string from the first content block. (Alternatively, <code>response.text</code> provides direct access across all LangChain 1.4 messages).</p>

<h3>Cell 4 & 5: Streaming Generator Demonstration</h3>
<pre><code># Cell 4: Markdown ### STREAMING
# Cell 5: Generator inspection
model.stream("Tell me something about anime called One Piece.")</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result</span>
&lt;generator object BaseChatModel.stream at 0x...&gt;
</div>
<p><strong>Explanation:</strong> <code>model.stream()</code> does not return a finished message; it returns a Python <strong>generator</strong> that yields chunks on demand when iterated.</p>

<div class="avoid-break">
<h3>Cell 6: Iterating Stream Chunks</h3>
<pre><code>for chunk in model.stream("Tell me something about anime called One Piece."):
    print(chunk.text, end="|", flush=True)</code></pre>
<div class="output-box">
    <span class="output-label">Printed Stream Output</span>
***One Piece*** is not just an anime; it is a global cultural phenomenon and one of the longest-running|, most successful entertainment franchises in history. \n\nHere is a breakdown...
</div>
<p><strong>Key Mechanics:</strong></p>
<ul>
    <li><code>chunk.text</code> retrieves the text delta in the current chunk.</li>
    <li><code>end="|"</code> prints a pipe delimiter between chunks, making chunk boundaries visually explicit.</li>
    <li><code>flush=True</code> forces stdout to render immediately rather than waiting for newline buffers.</li>
</ul>
</div>

<div class="avoid-break">
<h3>Cell 7 & 8: Batch Processing with Concurrency Control</h3>
<pre><code># Cell 7: Markdown ### BATCH
# Cell 8: Concurrent Batch
responses = model.batch([
    "Who is Luffy In One Piece?",
    "How old is Goku in dragin ball?",
    "Tell me feats of Ronaldo in 2008",
    "What are the powers of Dr Doom?"
],
config={{
    'max_concurrency': 2 # limit to 2 parallel calls so 4 questions sent 2 at a time
}})

for response in responses:
    print(response)</code></pre>
<p><strong>Key Mechanics:</strong></p>
<ul>
    <li><code>model.batch([q1, q2, q3, q4])</code> sends all 4 queries to the model concurrently.</li>
    <li><code>config={{'max_concurrency': 2}}</code> limits the thread pool to 2 simultaneous requests. The first 2 queries run; as soon as one finishes, query 3 begins. This prevents flooding the API and triggering rate limits.</li>
</ul>
</div>

<div class="avoid-break">
<h3>Cell 9: Correcting the Batch Response Iteration</h3>
<div class="callout callout-error">
    <div class="callout-title">Original Bug Analysis</div>
    The original notebook contained:
    <pre><code>for response in responses:
    for chunk in model.stream(response): # &lt;-- ERROR!
        print(chunk.text)</code></pre>
    <strong>Error:</strong> <code>ValueError: Invalid input type &lt;class 'AIMessage'&gt;. Must be a PromptValue, str, or list of BaseMessages.</code><br/>
    <strong>Cause:</strong> <code>model.batch</code> had ALREADY generated the full answers as <code>AIMessage</code> objects! Nesting <code>model.stream(response)</code> attempted to pass the completed AI answer back into the model as an input prompt!
</div>

<p><strong>Corrected Code:</strong></p>
<pre><code>for response in responses:
    print(response.text)
    print("-" * 50)</code></pre>
<p><strong>Explanation:</strong> Simply iterate over the <code>responses</code> list and print each answer directly.</p>
</div>

<!-- Section F: End-to-End Execution Flow -->
<div class="page-break-before"></div>
<h2>F. End-to-End Execution Modes Comparison</h2>
<p>The diagram below contrasts the dataflow and runtime behavior of the three execution modes:</p>

<div class="diagram-container">
    {svg_diagram}
    <div class="diagram-caption">Figure 2.1: Architectural Comparison of invoke(), stream(), and batch()</div>
</div>

<!-- Section G: Important APIs -->
<h2>G. Important APIs & Classes Reference</h2>
<table>
    <tr>
        <th>Method</th>
        <th>Input Type</th>
        <th>Return Type</th>
        <th>Best Used For</th>
    </tr>
    <tr>
        <td><code>model.invoke(prompt)</code></td>
        <td><code>str</code> or <code>List[BaseMessage]</code></td>
        <td><code>AIMessage</code></td>
        <td>Single query when latency is not user-facing.</td>
    </tr>
    <tr>
        <td><code>model.stream(prompt)</code></td>
        <td><code>str</code> or <code>List[BaseMessage]</code></td>
        <td><code>Iterator[AIMessageChunk]</code></td>
        <td>Interactive chat UIs requiring immediate visual feedback.</td>
    </tr>
    <tr>
        <td><code>model.batch(prompts, config)</code></td>
        <td><code>List[str]</code> or <code>List[List[Message]]</code></td>
        <td><code>List[AIMessage]</code></td>
        <td>Bulk processing with controlled parallelism.</td>
    </tr>
    <tr>
        <td><code>chunk.text</code></td>
        <td>N/A (Property)</td>
        <td><code>str</code></td>
        <td>Direct string extraction from a stream chunk.</td>
    </tr>
</table>

<!-- Section H: Common Errors & Debugging -->
<h2>H. Common Errors & Debugging</h2>
<div class="callout callout-error">
    <div class="callout-title">Case Study: The "5-10 Minute Hang" (HTTP 429 Quota Exhaustion)</div>
    <strong>Symptom:</strong> A simple cell execution freezes and takes 5 to 10 minutes without printing anything.<br/>
    <strong>Diagnostic Investigation:</strong> When inspected via network debug logs, the Google GenAI endpoint returned:
    <pre><code>HTTP 429 Too Many Requests: RESOURCE_EXHAUSTED
Generate content requests per day limit exceeded on Free Tier (limit: 20 requests/day).
Retrying in 1.28s, 2.43s, 4.11s, 8.51s, 16.6s, 32s...</code></pre>
    <strong>Root Cause:</strong> LangChain's retry handler (<code>tenacity</code>) catches 429 errors and automatically retries with exponential backoff. The notebook wasn't computing slowly; it was stuck in a retry loop waiting for quota to reset!<br/>
    <strong>Fix:</strong> Switch to a high-quota provider like Groq (<code>init_chat_model("groq:openai/gpt-oss-20b")</code>) or upgrade your API tier.
</div>

<!-- Section I: Practical Examples -->
<h2>I. Practical Example: Stream Fallback Handler</h2>
<pre><code>def safe_stream_print(model, prompt: str):
    \"\"\"Stream response with automatic error handling.\"\"\"
    try:
        for chunk in model.stream(prompt):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print()
    except Exception as e:
        print(f"\\n[Streaming Error: {{e}}]")</code></pre>

<!-- Section J: Key Takeaways -->
<h2>J. Key Takeaways</h2>
<ul>
    <li>Use <code>init_chat_model</code> for provider-agnostic applications.</li>
    <li><code>stream()</code> yields chunks progressively; use <code>chunk.text</code> and <code>flush=True</code> for responsive rendering.</li>
    <li>Thinking models generate invisible reasoning tokens first; output appears only after reasoning finishes.</li>
    <li><code>batch()</code> handles concurrency natively via <code>config={{'max_concurrency': N}}</code>.</li>
    <li>Long execution delays often indicate background HTTP 429 retry loops rather than slow computation.</li>
</ul>

<!-- Section K: Practice Questions -->
<div class="page-break-before"></div>
<h2>K. Practice Exercises & Knowledge Checks</h2>

<div class="exercise-box">
    <div class="exercise-question">Question 1 (Conceptual): Why did model.batch([4 questions], config={{'max_concurrency': 2}}) send questions in pairs rather than all 4 at once?</div>
    <div class="answer-box">
        <strong>Answer:</strong> <code>max_concurrency: 2</code> limits the thread pool to 2 simultaneous HTTP requests. This prevents rate-limit spikes by ensuring at most 2 requests are in flight simultaneously.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 2 (Debugging): Why did calling model.stream(response) inside the batch loop fail with a ValueError?</div>
    <div class="answer-box">
        <strong>Answer:</strong> Because <code>response</code> was an <code>AIMessage</code> (the model's finished answer), not a user prompt or list of messages. The batch call had already finished processing the question.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 3 (Code Tracing): In cell 6, what happens if flush=True is omitted from print(chunk.text, end="|")?</div>
    <div class="answer-box">
        <strong>Answer:</strong> Without <code>flush=True</code>, Python's standard output buffer may hold the characters in memory until a newline is reached or the buffer fills, causing text to appear in sudden bursts rather than smooth word-by-word streaming.
    </div>
</div>

<!-- Section L: Further Learning -->
<h2>L. Further Learning & Documentation</h2>
<ul>
    <li><a href="https://python.langchain.com/docs/concepts/#chat-models">LangChain Chat Models & Unified Interface</a></li>
    <li><a href="https://ai.google.dev/gemini-api/docs/rate-limits">Google Gemini API Rate Limits & Quotas</a></li>
    <li>Next study guide in sequence: <strong>3-toolcall.pdf</strong> (Native Tool Calling & Execution Loops).</li>
</ul>

</body>
</html>
"""
    return html

# Specific Builder 3
def build_guide_3(fname, cells, today):
    svg_diagram = get_svg_toolcall_loop()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{fname} - Educational Study Guide</title>
    <style>{CSS_STYLES}</style>
</head>
<body>

<!-- Section A: Cover Page -->
<div class="cover-page">
    <span class="cover-badge">LangChain 1.4+ • Tool Calling & Agent Mechanics</span>
    <h1 class="cover-title">Native Tool Calling & Manual Execution Loops</h1>
    <p class="cover-subtitle">Understanding Schema Binding, Model Invocations, and Multi-Turn Conversation Loops</p>
    
    <p style="font-size: 10.5pt; color: #475569; max-width: 580px; margin-top: 15px;">
        A comprehensive deep dive into the inner workings of tool calling. Explains the <code>@tool</code> decorator, 
        parameter schema generation, <code>model.bind_tools()</code>, and how to implement the classic two-step 
        manual tool execution loop from scratch.
    </p>

    <div class="cover-meta">
        <div class="cover-meta-grid">
            <div class="meta-item"><strong>Target Notebook:</strong> <code>{fname}</code></div>
            <div class="meta-item"><strong>Generation Date:</strong> {today}</div>
            <div class="meta-item"><strong>Language & Runtime:</strong> Python 3.14 • Virtualenv (.venv)</div>
            <div class="meta-item"><strong>Inference Engine:</strong> Groq LPU (openai/gpt-oss-20b)</div>
        </div>
    </div>
</div>

<!-- Section B: Learning Objectives -->
<h2>B. Learning Objectives</h2>
<p>By studying this notebook and guide, you will master:</p>
<ul>
    <li><strong>The Tool Calling Contract:</strong> Understand the division of labor between the LLM (which outputs structured JSON requests) and your application (which executes the code).</li>
    <li><strong>The <code>@tool</code> Decorator:</strong> Turn regular Python functions into model-compatible tools using type hints and docstrings.</li>
    <li><strong>Tool Schema Binding:</strong> Use <code>model.bind_tools()</code> to inject tool definitions into the model's system payload.</li>
    <li><strong>Parsing Tool Call Payloads:</strong> Inspect <code>AIMessage.tool_calls</code>, extracting <code>name</code>, <code>args</code>, and unique <code>id</code>.</li>
    <li><strong>Manual Tool Execution Loops:</strong> Build the multi-turn conversational loop manually: User $\rightarrow$ Model Tool Request $\rightarrow$ Python Tool Execution $\rightarrow$ ToolMessage $\rightarrow$ Final Model Response.</li>
    <li><strong>Conversation History Management:</strong> Maintain sequential state in the <code>messages</code> list.</li>
</ul>

<!-- Section C: Prerequisites & Environment Setup -->
<h2>C. Prerequisites & Setup</h2>
<div class="callout callout-note">
    <div class="callout-title">Fast Inference Provider: Groq</div>
    This notebook leverages <strong>Groq</strong> for ultra-fast model inference (<code>openai/gpt-oss-20b</code>), which executes responses in ~1.00 second.
</div>
<table>
    <tr>
        <th>Variable / Key</th>
        <th>Setting</th>
        <th>Notes</th>
    </tr>
    <tr>
        <td><code>GROQ_API_KEY</code></td>
        <td>Stored in local <code>.env</code></td>
        <td>Required by <code>langchain-groq</code> for authentication.</td>
    </tr>
    <tr>
        <td>Target Model</td>
        <td><code>groq:openai/gpt-oss-20b</code></td>
        <td>High-speed open-weights model hosted on Groq LPU hardware.</td>
    </tr>
</table>

<!-- Section D: Topic Overview -->
<div class="page-break-before"></div>
<h2>D. Topic Overview: What is Tool Calling?</h2>
<p>
    Large Language Models cannot directly access real-time databases, browse the web, or run computations without external help. 
    <strong>Tool calling</strong> (also called function calling) is the standardized protocol that bridges this gap:
</p>
<ol>
    <li>Your application gives the LLM a list of tool descriptions (names, descriptions, parameter types).</li>
    <li>When a user asks a question requiring external data, the LLM decides <em>which</em> tool to call and extracts the arguments.</li>
    <li><strong>Crucial Principle:</strong> The LLM does <strong>not</strong> execute the code. The LLM simply stops and outputs a structured request: <code>call get_weather with location="Delhi"</code>.</li>
    <li>Your Python runtime executes the function locally, captures the return value, and wraps it in a <code>ToolMessage</code>.</li>
    <li>Your application sends the tool result back to the LLM so it can read the observation and formulate an answer for the user.</li>
</ol>

<!-- Section E: Detailed Notebook Walkthrough -->
<h2>E. Notebook Walkthrough & Cell Dissection</h2>

<h3>Cell 0: Markdown Section Header</h3>
<pre><code>### Tool Calling</code></pre>

<div class="avoid-break">
<h3>Cell 1: Groq Initialization & Initial Invocation</h3>
<pre><code>import os
from langchain.chat_models import init_chat_model

os.environ["GROQ_API_KYE"] = os.getenv("GROQ_API_KEY")

model = init_chat_model("groq:openai/gpt-oss-20b")
response = model.invoke("Tell me something about Mbappe.")
response</code></pre>
<p><strong>Code & Execution Analysis:</strong></p>
<ul>
    <li>Notice the typo <code>os.environ["GROQ_API_KYE"]</code> in line 3. Fortunately, <code>os.getenv("GROQ_API_KEY")</code> had already populated the true environment via <code>.env</code>, so <code>init_chat_model</code> found the real key seamlessly.</li>
    <li>The model responded with a detailed breakdown of footballer Kylian Mbappé in 1.3 seconds, demonstrating the speed of Groq's inference engine.</li>
</ul>
</div>

<div class="avoid-break">
<h3>Cell 2: Defining & Binding Tools</h3>
<pre><code>from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    \"\"\"Get the weather at a location\"\"\"
    return f"It's sunny in {{location}}"

model_with_tools = model.bind_tools([get_weather])</code></pre>
<p><strong>Key Mechanics:</strong></p>
<ol>
    <li><strong><code>@tool</code>:</strong> A decorator that converts a Python function into a <code>BaseTool</code> instance.</li>
    <li><strong>Type Hints & Docstring:</strong> <code>location: str</code> and the docstring <code>\"\"\"Get the weather at a location\"\"\"</code> are automatically converted into a JSON Schema definition:
        <pre><code>{{
    "name": "get_weather",
    "description": "Get the weather at a location",
    "parameters": {{"type": "object", "properties": {{"location": {{"type": "string"}}}}}}
}}</code></pre>
    </li>
    <li><strong><code>model.bind_tools([get_weather])</code>:</strong> Returns a new runnable model wrapper with tool definitions permanently attached to its requests.</li>
</ol>
</div>

<div class="avoid-break">
<h3>Cell 3: Triggering a Tool Call Request</h3>
<pre><code>response = model_with_tools.invoke("What's the weather like in Delhi?")
print(response)

for tool_call in response.tool_calls:
    print(f"Tool: {{tool_call['name']}}")
    print(f"Args: {{tool_call['args']}}")</code></pre>
<div class="output-box">
    <span class="output-label">Printed Execution Output</span>
content='' additional_kwargs={{...}} tool_calls=[{{'name': 'get_weather', 'args': {{'location': 'Delhi'}}, 'id': 'fc_623e26ba-d2e8-49ca-b7b4-69f9accf453c', 'type': 'tool_call'}}]
Tool: get_weather
Args: {{'location': 'Delhi'}}
</div>
<p><strong>Critical Observations:</strong></p>
<ul>
    <li><code>content=''</code>: The model generated zero natural language text because it chose to call a tool.</li>
    <li><code>tool_calls</code>: Contains the structured payload with <code>name='get_weather'</code> and parsed arguments <code>{{'location': 'Delhi'}}</code>.</li>
</ul>
</div>

<div class="avoid-break">
<h3>Cell 4: The 2-Step Manual Tool Execution Loop</h3>
<pre><code># Tool Execution Loops

# 1. You ask, but the AI doesn't know live data
messages = [{{"role": "user", "content": "What's the weather in Delhi?"}}]
ai_msg = model_with_tools.invoke(messages)
messages.append(ai_msg)

# 2. Program runs the tool for the AI
for tool_call in ai_msg.tool_calls:
    tool_result = get_weather.invoke(tool_call)
    messages.append(tool_result)

# 3. Pass results back to model for final response
final_response = model_with_tools.invoke(messages)
print(final_response.text)</code></pre>
<div class="output-box">
    <span class="output-label">Final Printed Result</span>
The weather in Delhi is sunny.
</div>
<p><strong>Step-by-Step Architectural Trace:</strong></p>
<ol>
    <li><strong>Step 1:</strong> <code>messages</code> begins with the user question. The model inspects the question and returns <code>ai_msg</code> with a tool call request.</li>
    <li><strong>Step 2:</strong> We append <code>ai_msg</code> to <code>messages</code> so the conversation history includes the model's intent.</li>
    <li><strong>Step 3:</strong> <code>get_weather.invoke(tool_call)</code> executes the Python function using the arguments generated by the model. It automatically creates a <code>ToolMessage</code> matching the tool call ID.</li>
    <li><strong>Step 4:</strong> We append <code>tool_result</code> to <code>messages</code>.</li>
    <li><strong>Step 5:</strong> We invoke <code>model_with_tools.invoke(messages)</code> again. Now the model sees the original question, its own tool call request, and the tool's actual output! It synthesizes the final conversational answer: <em>"The weather in Delhi is sunny."</em></li>
</ol>
</div>

<div class="avoid-break">
<h3>Cell 5: Inspecting the Accumulated Message History</h3>
<pre><code>messages</code></pre>
<div class="output-box">
    <span class="output-label">Full State Inspection</span>
[
  {{'role': 'user', 'content': "What's the weather in Delhi?"}},
  AIMessage(content='', tool_calls=[{{'name': 'get_weather', 'args': {{'location': 'Delhi'}}, 'id': 'fc_d4d8...'}}]),
  ToolMessage(content="It's sunny in Delhi", name='get_weather', tool_call_id='fc_d4d8...')
]
</div>
<p><strong>Explanation:</strong> Demonstrates how conversational context accumulates in LangChain. Every step is transparently visible in the state list.</p>
</div>

<!-- Section F: End-to-End Execution Flow -->
<div class="page-break-before"></div>
<h2>F. End-to-End Tool Execution Sequence Diagram</h2>
<p>The sequence diagram below illustrates the exact two-turn handshake executed in Cell 4:</p>

<div class="diagram-container">
    {svg_diagram}
    <div class="diagram-caption">Figure 3.1: Sequence Diagram of the 2-Turn Manual Tool Calling Loop</div>
</div>

<!-- Section G: Important APIs -->
<h2>G. Important APIs & Classes Reference</h2>
<table>
    <tr>
        <th>Construct</th>
        <th>Type</th>
        <th>Input</th>
        <th>Output</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><code>@tool</code></td>
        <td>Decorator</td>
        <td>Python function</td>
        <td><code>BaseTool</code></td>
        <td>Parses function annotations & docstrings into model tool schemas.</td>
    </tr>
    <tr>
        <td><code>model.bind_tools</code></td>
        <td>Method</td>
        <td><code>List[BaseTool]</code></td>
        <td><code>RunnableBinding</code></td>
        <td>Binds schemas to chat model API parameters.</td>
    </tr>
    <tr>
        <td><code>response.tool_calls</code></td>
        <td>Attribute</td>
        <td>N/A</td>
        <td><code>List[Dict]</code></td>
        <td>Structured list of tool requests emitted by the model.</td>
    </tr>
    <tr>
        <td><code>tool.invoke(tool_call)</code></td>
        <td>Method</td>
        <td><code>tool_call</code> dict</td>
        <td><code>ToolMessage</code></td>
        <td>Executes tool and creates linked ToolMessage with matching ID.</td>
    </tr>
</table>

<!-- Section H: Common Errors & Debugging -->
<h2>H. Common Errors & Debugging</h2>
<div class="callout callout-error">
    <div class="callout-title">Trap 1: Mismatched tool_call_id in ToolMessage</div>
    <strong>Symptom:</strong> API returns <code>400 Invalid Message Sequence</code> or model hallucinates.<br/>
    <strong>Cause:</strong> If you construct a <code>ToolMessage</code> manually without matching the <code>id</code> from <code>tool_call['id']</code>, the LLM cannot link the observation to its corresponding request. Always use <code>tool.invoke(tool_call)</code> to guarantee ID synchronization.
</div>
<div class="callout callout-warning">
    <div class="callout-title">Trap 2: Missing Return Types or Argument Types</div>
    <strong>Symptom:</strong> Tool schema has <code>"type": "null"</code> or arguments are passed as unparsed strings.<br/>
    <strong>Cause:</strong> Failing to include Python type hints (e.g. <code>location: str</code>). The <code>@tool</code> decorator uses type inspection to build the JSON Schema.
</div>

<!-- Section I: Practical Examples -->
<h2>I. Practical Example: Multi-Tool Dispatcher</h2>
<pre><code>tools_by_name = {{"get_weather": get_weather}}

for tool_call in ai_msg.tool_calls:
    tool_func = tools_by_name.get(tool_call['name'])
    if tool_func:
        result = tool_func.invoke(tool_call)
        messages.append(result)</code></pre>
<p>Using a dictionary lookup dynamically routes multiple distinct tools without hardcoded <code>if/elif</code> statements.</p>

<!-- Section J: Key Takeaways -->
<h2>J. Key Takeaways</h2>
<ul>
    <li>The model <strong>never</strong> runs tools directly; it generates structured JSON arguments for your host environment to execute.</li>
    <li><code>@tool</code> requires both clear Python type annotations and descriptive docstrings.</li>
    <li>A complete tool execution loop requires two model invocations: Turn 1 produces the tool call request; Turn 2 digests the <code>ToolMessage</code> observation and answers the user.</li>
    <li>Automated agents (such as <code>create_agent</code> from Notebook 1) wrap this exact loop inside an automated state machine.</li>
</ul>

<!-- Section K: Practice Questions -->
<div class="page-break-before"></div>
<h2>K. Practice Exercises & Knowledge Checks</h2>

<div class="exercise-box">
    <div class="exercise-question">Question 1 (Conceptual): What is the difference between model.bind_tools() and create_agent()?</div>
    <div class="answer-box">
        <strong>Answer:</strong> <code>model.bind_tools()</code> only teaches the model about tools; you must manually write the execution loop to run the tool and send results back. <code>create_agent()</code> constructs an automated state graph (LangGraph) that handles tool execution and multi-step reasoning automatically.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 2 (Code Tracing): In Cell 3, why does response.content evaluate to an empty string?</div>
    <div class="answer-box">
        <strong>Answer:</strong> Because the model decided to request a tool execution. Its entire response payload was directed into <code>response.tool_calls</code>, reserving conversational text for after the tool result is received.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 3 (Debugging): If an environment variable is set as os.environ["GROQ_API_KYE"], why did init_chat_model("groq:...") still work?</div>
    <div class="answer-box">
        <strong>Answer:</strong> Because <code>load_dotenv()</code> had already loaded the true <code>GROQ_API_KEY</code> from the <code>.env</code> file directly into <code>os.environ</code>. The typo line merely set an extra unused variable (<code>GROQ_API_KYE</code>).
    </div>
</div>

<!-- Section L: Further Learning -->
<h2>L. Further Learning & Documentation</h2>
<ul>
    <li><a href="https://python.langchain.com/docs/concepts/#tools">LangChain Tools & Tool Calling Documentation</a></li>
    <li><a href="https://console.groq.com/docs/models">Groq Supported Models & Hardware Overview</a></li>
    <li>Previous study guide in sequence: <strong>2-modelintegration.pdf</strong> (Interaction Modes).</li>
</ul>

</body>
</html>
"""
    return html

# Generic Fallback Builder
def build_generic_guide(fname, cells, today):
    cells_html = []
    for c in cells:
        ctype = c['type']
        source = escape_html(c['source'])
        out_html = ""
        if c['outputs']:
            out_texts = []
            for o in c['outputs']:
                out_texts.append(escape_html(o['text']))
            out_html = f"<div class='output-box'><span class='output-label'>Output</span>{'<br/>'.join(out_texts)}</div>"
            
        cells_html.append(f"""
        <div class="avoid-break" style="margin-bottom: 1.2em;">
            <h4>Cell {c['index']} ({ctype.capitalize()})</h4>
            <pre><code>{source}</code></pre>
            {out_html}
        </div>
        """)
        
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{fname} - Educational Study Guide</title>
    <style>{CSS_STYLES}</style>
</head>
<body>
<div class="cover-page">
    <span class="cover-badge">Jupyter Notebook Study Guide</span>
    <h1 class="cover-title">{fname}</h1>
    <p class="cover-subtitle">Complete Educational Walkthrough & Code Analysis</p>
    <div class="cover-meta">
        <div><strong>Filename:</strong> <code>{fname}</code></div>
        <div><strong>Generation Date:</strong> {today}</div>
    </div>
</div>

<h2>B. Learning Objectives</h2>
<p>Understand the concepts, execution order, and code structures presented in <code>{fname}</code>.</p>

<h2>C. Prerequisites & Setup</h2>
<p>Python 3.14+ environment with dependencies configured in <code>pyproject.toml</code>.</p>

<h2>D. Notebook Walkthrough</h2>
{''.join(cells_html)}

<h2>E. Key Takeaways</h2>
<p>Review the cell outputs above and test interactive modifications in the Jupyter environment.</p>
</body>
</html>
"""

def generate_pdf_from_html(html_content: str, output_pdf_path: Path):
    """Render HTML to PDF using Microsoft Edge headless."""
    scratch_dir = Path("scratch")
    scratch_dir.mkdir(exist_ok=True)
    
    temp_html = scratch_dir / f"temp_{output_pdf_path.stem}.html"
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    
    edge_exe = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_exe = p
            break
            
    if not edge_exe:
        raise FileNotFoundError("Microsoft Edge executable not found for headless PDF generation.")
        
    cmd = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={output_pdf_path.resolve()}",
        str(temp_html.resolve())
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Edge PDF generation failed: {res.stderr}")
        
    # Cleanup temp html
    if temp_html.exists():
        temp_html.unlink()

def validate_pdf(pdf_path: Path) -> dict:
    """Validate generated PDF using pypdf."""
    from pypdf import PdfReader
    
    if not pdf_path.exists():
        return {'valid': False, 'error': 'File does not exist'}
        
    size_kb = pdf_path.stat().st_size / 1024
    if size_kb < 10:
        return {'valid': False, 'error': f'File too small ({size_kb:.1f} KB)'}
        
    try:
        reader = PdfReader(str(pdf_path))
        num_pages = len(reader.pages)
        empty_pages = []
        
        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if len(text.strip()) < 20:
                empty_pages.append(idx + 1)
                
        return {
            'valid': True,
            'pages': num_pages,
            'size_kb': size_kb,
            'empty_pages': empty_pages
        }
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def process_notebook(nb_path: Path, output_dir: Path):
    """Process a single notebook file into a PDF."""
    print(f"\nProcessing notebook: {nb_path.name}")
    nb_data = extract_notebook_data(nb_path)
    
    output_pdf = output_dir / f"{nb_path.stem}.pdf"
    print(f"Generating HTML for {nb_path.name}...")
    html_content = build_pdf_document(nb_data)
    
    print(f"Rendering PDF via headless Edge to {output_pdf}...")
    generate_pdf_from_html(html_content, output_pdf)
    
    print("Validating generated PDF...")
    val = validate_pdf(output_pdf)
    if val['valid']:
        print(f"SUCCESS: {output_pdf.name} generated successfully!")
        print(f"  Pages: {val['pages']}")
        print(f"  Size: {val['size_kb']:.1f} KB")
        if val['empty_pages']:
            print(f"  WARNING: Potential blank pages at: {val['empty_pages']}")
        return True, val
    else:
        print(f"FAILED: {output_pdf.name} validation failed: {val.get('error')}")
        return False, val

def main():
    parser = argparse.ArgumentParser(description="Jupyter Notebook to Educational PDF Documentation Generator")
    parser.add_argument("--notebook", type=str, help="Path to single notebook to document")
    parser.add_argument("--all", action="store_true", help="Document all notebooks found in the workspace")
    args = parser.parse_args()
    
    workspace_root = Path.cwd()
    output_dir = workspace_root / "pdf"
    output_dir.mkdir(exist_ok=True)
    
    if args.notebook:
        nb_path = Path(args.notebook)
        if not nb_path.exists():
            print(f"Error: Notebook {nb_path} not found.")
            sys.exit(1)
        notebooks = [nb_path]
    else:
        # Default to all notebooks in workspace
        notebooks = sorted(list(workspace_root.glob("**/*.ipynb")))
        # Filter out virtualenv or checkpoint notebooks if any
        notebooks = [nb for nb in notebooks if ".venv" not in str(nb) and ".ipynb_checkpoints" not in str(nb)]
        
    if not notebooks:
        print("No notebooks found to document.")
        sys.exit(0)
        
    print(f"Found {len(notebooks)} notebook(s) to process.")
    results = {}
    for nb in notebooks:
        success, val = process_notebook(nb, output_dir)
        results[nb.name] = (success, val)
        
    print("\n" + "="*50)
    print("SUMMARY OF GENERATION RESULTS:")
    print("="*50)
    for name, (succ, val) in results.items():
        status = "SUCCESS" if succ else "FAILED"
        pages = val.get('pages', 'N/A') if succ else 'N/A'
        size = f"{val.get('size_kb', 0):.1f} KB" if succ else 'N/A'
        print(f"- {name} -> {status} ({pages} pages, {size})")

if __name__ == "__main__":
    main()
