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

def get_svg_messages_hierarchy():
    """Vector SVG diagram for LangChain Core Message Hierarchy and Handshake."""
    return """
    <svg width="650" height="260" viewBox="0 0 650 260" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <marker id="marrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
            </marker>
            <marker id="marrow-amber" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#d97706" />
            </marker>
            <marker id="marrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
            </marker>
        </defs>
        
        <!-- Base Message Box -->
        <rect x="235" y="10" width="180" height="38" rx="6" fill="#1e293b" stroke="#0f172a" stroke-width="1.5"/>
        <text x="325" y="27" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">BaseMessage</text>
        <text x="325" y="41" font-family="'Segoe UI', sans-serif" font-size="8" fill="#94a3b8" text-anchor="middle">content, id, name, additional_kwargs</text>

        <!-- Connecting Lines to 4 subclasses -->
        <line x1="325" y1="48" x2="325" y2="62" stroke="#64748b" stroke-width="1.5"/>
        <line x1="80" y1="62" x2="570" y2="62" stroke="#64748b" stroke-width="1.5"/>
        <line x1="80" y1="62" x2="80" y2="75" stroke="#64748b" stroke-width="1.5" marker-end="url(#marrow)"/>
        <line x1="240" y1="62" x2="240" y2="75" stroke="#64748b" stroke-width="1.5" marker-end="url(#marrow)"/>
        <line x1="410" y1="62" x2="410" y2="75" stroke="#64748b" stroke-width="1.5" marker-end="url(#marrow)"/>
        <line x1="570" y1="62" x2="570" y2="75" stroke="#64748b" stroke-width="1.5" marker-end="url(#marrow)"/>

        <!-- 4 Subclasses -->
        <!-- 1. SystemMessage -->
        <rect x="15" y="75" width="130" height="52" rx="5" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
        <text x="80" y="93" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#92400e" text-anchor="middle">SystemMessage</text>
        <text x="80" y="108" font-family="'Segoe UI', sans-serif" font-size="8" fill="#b45309" text-anchor="middle">Role / Persona Guidance</text>
        <text x="80" y="120" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#78350f" text-anchor="middle">Steers Model Tone</text>

        <!-- 2. HumanMessage -->
        <rect x="175" y="75" width="130" height="52" rx="5" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
        <text x="240" y="93" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#1e40af" text-anchor="middle">HumanMessage</text>
        <text x="240" y="108" font-family="'Segoe UI', sans-serif" font-size="8" fill="#2563eb" text-anchor="middle">User Queries & Inputs</text>
        <text x="240" y="120" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#1d4ed8" text-anchor="middle">name="alice", id="msg_1"</text>

        <!-- 3. AIMessage -->
        <rect x="345" y="75" width="130" height="52" rx="5" fill="#faf5ff" stroke="#8b5cf6" stroke-width="1.5"/>
        <text x="410" y="93" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#6b21a8" text-anchor="middle">AIMessage</text>
        <text x="410" y="108" font-family="'Segoe UI', sans-serif" font-size="8" fill="#7c3aed" text-anchor="middle">Model Responses</text>
        <text x="410" y="120" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#581c87" text-anchor="middle">tool_calls=[{id, args}]</text>

        <!-- 4. ToolMessage -->
        <rect x="505" y="75" width="130" height="52" rx="5" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
        <text x="570" y="93" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#065f46" text-anchor="middle">ToolMessage</text>
        <text x="570" y="108" font-family="'Segoe UI', sans-serif" font-size="8" fill="#059669" text-anchor="middle">Tool Execution Result</text>
        <text x="570" y="120" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#047857" text-anchor="middle">tool_call_id="call_123"</text>

        <!-- Multi-Turn Sequence Diagram at Bottom -->
        <rect x="15" y="145" width="620" height="105" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>
        <text x="325" y="162" font-family="'Segoe UI', sans-serif" font-size="9.5" font-weight="bold" fill="#334155" text-anchor="middle">Multi-Turn Tool Execution Handshake in Message State</text>

        <!-- Turn 1 -->
        <rect x="30" y="174" width="130" height="64" rx="4" fill="#eff6ff" stroke="#bfdbfe"/>
        <text x="95" y="190" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#1e40af" text-anchor="middle">1. Initial Input</text>
        <text x="95" y="205" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155" text-anchor="middle">[SystemMessage,</text>
        <text x="95" y="218" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155" text-anchor="middle"> HumanMessage]</text>
        <text x="95" y="231" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#2563eb" text-anchor="middle">-> Sent to LLM</text>

        <line x1="162" y1="206" x2="182" y2="206" stroke="#3b82f6" stroke-width="1.8" marker-end="url(#marrow)"/>

        <!-- Turn 2 -->
        <rect x="185" y="174" width="135" height="64" rx="4" fill="#faf5ff" stroke="#ddd6fe"/>
        <text x="252" y="190" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#6b21a8" text-anchor="middle">2. Tool Call Request</text>
        <text x="252" y="205" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155" text-anchor="middle">AIMessage(content='',</text>
        <text x="252" y="218" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155" text-anchor="middle"> tool_calls=[{id:'call_1'}])</text>
        <text x="252" y="231" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#7c3aed" text-anchor="middle">-> Appended to State</text>

        <line x1="322" y1="206" x2="342" y2="206" stroke="#8b5cf6" stroke-width="1.8" marker-end="url(#marrow)"/>

        <!-- Turn 3 -->
        <rect x="345" y="174" width="135" height="64" rx="4" fill="#ecfdf5" stroke="#a7f3d0"/>
        <text x="412" y="190" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#065f46" text-anchor="middle">3. Tool Observation</text>
        <text x="412" y="205" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155" text-anchor="middle">ToolMessage(content='..',</text>
        <text x="412" y="218" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155" text-anchor="middle"> tool_call_id='call_1')</text>
        <text x="412" y="231" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#059669" text-anchor="middle">-> Python Executes</text>

        <line x1="482" y1="206" x2="502" y2="206" stroke="#10b981" stroke-width="1.8" marker-end="url(#marrow-green)"/>

        <!-- Turn 4 -->
        <rect x="505" y="174" width="120" height="64" rx="4" fill="#f0fdf4" stroke="#86efac"/>
        <text x="565" y="190" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#15803d" text-anchor="middle">4. Final Answer</text>
        <text x="565" y="205" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155" text-anchor="middle">Final AIMessage</text>
        <text x="565" y="218" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155" text-anchor="middle">Natural Language</text>
        <text x="565" y="231" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#166534" text-anchor="middle">-> User Receives</text>
    </svg>
    """

def get_svg_structured_output_pipeline():
    """Vector SVG diagram for Structured Output compilation and validation pipeline."""
    return """
    <svg width="650" height="240" viewBox="0 0 650 240" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <marker id="sarrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
            </marker>
            <marker id="sarrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
            </marker>
        </defs>

        <!-- Step 1: Schema Definition -->
        <rect x="15" y="30" width="135" height="175" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
        <rect x="15" y="30" width="135" height="28" rx="6" fill="#3b82f6"/>
        <text x="82" y="49" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#ffffff" text-anchor="middle">1. Schema Definition</text>
        <text x="82" y="78" font-family="'Segoe UI', sans-serif" font-size="8.8" font-weight="bold" fill="#1e40af" text-anchor="middle">Python Schemas</text>
        <rect x="25" y="92" width="115" height="22" rx="3" fill="#dbeafe"/>
        <text x="82" y="106" font-family="'Segoe UI', sans-serif" font-size="8" fill="#1e40af" text-anchor="middle">Pydantic BaseModel</text>
        <rect x="25" y="120" width="115" height="22" rx="3" fill="#dbeafe"/>
        <text x="82" y="134" font-family="'Segoe UI', sans-serif" font-size="8" fill="#1e40af" text-anchor="middle">TypedDict + Annotated</text>
        <rect x="25" y="148" width="115" height="22" rx="3" fill="#dbeafe"/>
        <text x="82" y="162" font-family="'Segoe UI', sans-serif" font-size="8" fill="#1e40af" text-anchor="middle">@dataclass Model</text>
        <text x="82" y="192" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#475569" text-anchor="middle">Field(description="...")</text>

        <!-- Arrow 1 to 2 -->
        <line x1="152" y1="117" x2="175" y2="117" stroke="#3b82f6" stroke-width="2" marker-end="url(#sarrow)"/>

        <!-- Step 2: LangChain Binding Compiler -->
        <rect x="178" y="30" width="135" height="175" rx="6" fill="#faf5ff" stroke="#8b5cf6" stroke-width="1.5"/>
        <rect x="178" y="30" width="135" height="28" rx="6" fill="#8b5cf6"/>
        <text x="245" y="49" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#ffffff" text-anchor="middle">2. Schema Binding</text>
        <text x="245" y="78" font-family="'Segoe UI', sans-serif" font-size="8.8" font-weight="bold" fill="#6b21a8" text-anchor="middle">Compiler Layer</text>
        <rect x="188" y="92" width="115" height="32" rx="3" fill="#ede9fe"/>
        <text x="245" y="105" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#581c87" text-anchor="middle">with_structured_</text>
        <text x="245" y="117" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#581c87" text-anchor="middle">output(Schema)</text>
        <text x="245" y="142" font-family="'Segoe UI', sans-serif" font-size="8" fill="#6b21a8" text-anchor="middle">Translates to:</text>
        <text x="245" y="157" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#4c1d95" text-anchor="middle">JSON Schema Tool</text>
        <text x="245" y="172" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#7e22ce" text-anchor="middle">Strict Type Checking</text>
        <text x="245" y="192" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#475569" text-anchor="middle">include_raw=True/False</text>

        <!-- Arrow 2 to 3 -->
        <line x1="315" y1="117" x2="338" y2="117" stroke="#8b5cf6" stroke-width="2" marker-end="url(#sarrow)"/>

        <!-- Step 3: Model Inference & Tool Call Emission -->
        <rect x="340" y="30" width="135" height="175" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
        <rect x="340" y="30" width="135" height="28" rx="6" fill="#f59e0b"/>
        <text x="407" y="49" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#ffffff" text-anchor="middle">3. Model Execution</text>
        <text x="407" y="78" font-family="'Segoe UI', sans-serif" font-size="8.8" font-weight="bold" fill="#92400e" text-anchor="middle">Groq LPU Engine</text>
        <rect x="350" y="92" width="115" height="32" rx="3" fill="#fde68a"/>
        <text x="407" y="105" font-family="'Segoe UI', sans-serif" font-size="8" fill="#78350f" text-anchor="middle">Forces Function Call</text>
        <text x="407" y="117" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#78350f" text-anchor="middle">tool_choice="auto"</text>
        <text x="407" y="145" font-family="'Segoe UI', sans-serif" font-size="8" fill="#92400e" text-anchor="middle">Model generates:</text>
        <rect x="350" y="152" width="115" height="36" rx="3" fill="#ffffff" stroke="#fbbf24"/>
        <text x="407" y="166" font-family="'Courier New', monospace" font-size="7.5" fill="#1e293b" text-anchor="middle">{"title":"Avengers",</text>
        <text x="407" y="179" font-family="'Courier New', monospace" font-size="7.5" fill="#1e293b" text-anchor="middle"> "year": 2019, ...}</text>

        <!-- Arrow 3 to 4 -->
        <line x1="477" y1="117" x2="500" y2="117" stroke="#f59e0b" stroke-width="2" marker-end="url(#sarrow)"/>

        <!-- Step 4: Validation & Python Object Return -->
        <rect x="502" y="30" width="135" height="175" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
        <rect x="502" y="30" width="135" height="28" rx="6" fill="#10b981"/>
        <text x="569" y="49" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#ffffff" text-anchor="middle">4. Validated Output</text>
        <text x="569" y="78" font-family="'Segoe UI', sans-serif" font-size="8.8" font-weight="bold" fill="#065f46" text-anchor="middle">Parser & Instantiator</text>
        <rect x="512" y="92" width="115" height="32" rx="3" fill="#d1fae5"/>
        <text x="569" y="105" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#047857" text-anchor="middle">Movie(title=...,</text>
        <text x="569" y="117" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#047857" text-anchor="middle"> year=2019, ...)</text>
        <text x="569" y="145" font-family="'Segoe UI', sans-serif" font-size="8" fill="#065f46" text-anchor="middle">Zero regex needed</text>
        <text x="569" y="160" font-family="'Segoe UI', sans-serif" font-size="8" fill="#065f46" text-anchor="middle">Type Safe Objects</text>
        <rect x="512" y="172" width="115" height="20" rx="3" fill="#a7f3d0"/>
        <text x="569" y="186" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#065f46" text-anchor="middle">IDE Auto-Complete</text>
    </svg>
    """

def get_svg_middleware_interceptor_architecture():
    """Vector SVG diagram illustrating LangChain 1.4 Agent Middleware Interceptor Architecture."""
    return """
    <svg width="650" height="260" viewBox="0 0 650 260" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <marker id="mw-arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
            </marker>
            <marker id="mw-arrow-purple" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#8b5cf6" />
            </marker>
            <marker id="mw-arrow-amber" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b" />
            </marker>
            <marker id="mw-arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
            </marker>
            <marker id="mw-arrow-red" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
            </marker>
        </defs>

        <!-- Outer Boundary: CompiledStateGraph with Middleware Pipeline -->
        <rect x="150" y="15" width="485" height="230" rx="8" fill="#f8fafc" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4"/>
        <text x="165" y="34" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#475569">LangChain 1.4 CompiledStateGraph (Agent Lifecycle)</text>

        <!-- 1. User Input & Config -->
        <rect x="15" y="80" width="115" height="75" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
        <text x="72" y="100" font-family="'Segoe UI', sans-serif" font-size="10.5" font-weight="bold" fill="#1e40af" text-anchor="middle">User Invocation</text>
        <text x="72" y="116" font-family="'Segoe UI', sans-serif" font-size="8.5" fill="#334155" text-anchor="middle">HumanMessage</text>
        <rect x="25" y="126" width="95" height="20" rx="3" fill="#dbeafe"/>
        <text x="72" y="139" font-family="'Consolas', monospace" font-size="7.5" fill="#1d4ed8" text-anchor="middle">thread_id: "test-1"</text>

        <!-- Arrow to Checkpointer -->
        <line x1="130" y1="117" x2="165" y2="117" stroke="#3b82f6" stroke-width="1.8" marker-end="url(#mw-arrow)"/>

        <!-- 2. Checkpointer -->
        <rect x="170" y="80" width="105" height="75" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
        <text x="222" y="100" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#92400e" text-anchor="middle">Checkpointer</text>
        <text x="222" y="115" font-family="'Consolas', monospace" font-size="8" fill="#b45309" text-anchor="middle">InMemorySaver</text>
        <text x="222" y="132" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#78350f" text-anchor="middle">Loads state for</text>
        <text x="222" y="143" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#78350f" text-anchor="middle">active thread_id</text>

        <!-- Arrow to Pre-Model Middleware -->
        <line x1="275" y1="117" x2="295" y2="117" stroke="#f59e0b" stroke-width="1.8" marker-end="url(#mw-arrow-amber)"/>

        <!-- 3. Summarization Middleware Hook -->
        <rect x="300" y="65" width="105" height="105" rx="6" fill="#ecfeff" stroke="#06b6d4" stroke-width="1.5"/>
        <text x="352" y="84" font-family="'Segoe UI', sans-serif" font-size="9.5" font-weight="bold" fill="#0e7490" text-anchor="middle">Summarization</text>
        <text x="352" y="96" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#0e7490" text-anchor="middle">Middleware</text>
        <rect x="308" y="106" width="89" height="34" rx="3" fill="#cffafe"/>
        <text x="352" y="119" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#155e75" text-anchor="middle">Trigger Check:</text>
        <text x="352" y="131" font-family="'Consolas', monospace" font-size="7.5" font-weight="bold" fill="#164e63" text-anchor="middle">N&gt;=10 or T&gt;=550</text>
        <text x="352" y="154" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#0e7490" text-anchor="middle">Compresses State</text>

        <!-- Arrow to Model -->
        <line x1="405" y1="117" x2="425" y2="117" stroke="#06b6d4" stroke-width="1.8" marker-end="url(#mw-arrow)"/>

        <!-- 4. Chat Model Decision -->
        <rect x="430" y="55" width="95" height="125" rx="6" fill="#faf5ff" stroke="#8b5cf6" stroke-width="1.5"/>
        <text x="477" y="74" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#6b21a8" text-anchor="middle">Chat Model</text>
        <text x="477" y="88" font-family="'Consolas', monospace" font-size="7.5" fill="#7c3aed" text-anchor="middle">gpt-oss-20b</text>
        
        <rect x="438" y="98" width="79" height="30" rx="3" fill="#ede9fe"/>
        <text x="477" y="111" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#581c87" text-anchor="middle">Evaluates Prompt</text>
        <text x="477" y="121" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#4c1d95" text-anchor="middle">&amp; Decides Action</text>

        <rect x="438" y="136" width="79" height="34" rx="3" fill="#ffffff" stroke="#c4b5fd"/>
        <text x="477" y="149" font-family="'Segoe UI', sans-serif" font-size="7" fill="#6b21a8" text-anchor="middle">Path A: Text Output</text>
        <text x="477" y="161" font-family="'Segoe UI', sans-serif" font-size="7" font-weight="bold" fill="#7c3aed" text-anchor="middle">Path B: Tool Call</text>

        <!-- Arrow to HITL Middleware -->
        <line x1="525" y1="117" x2="545" y2="117" stroke="#8b5cf6" stroke-width="1.8" marker-end="url(#mw-arrow-purple)"/>

        <!-- 5. HITL Interceptor -->
        <rect x="550" y="65" width="75" height="105" rx="6" fill="#fff1f2" stroke="#f43f5e" stroke-width="1.5"/>
        <text x="587" y="84" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#be123c" text-anchor="middle">HITL</text>
        <text x="587" y="96" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#be123c" text-anchor="middle">Middleware</text>
        <rect x="556" y="106" width="63" height="36" rx="3" fill="#ffe4e6"/>
        <text x="587" y="118" font-family="'Segoe UI', sans-serif" font-size="7" font-weight="bold" fill="#9f1239" text-anchor="middle">interrupt_on</text>
        <text x="587" y="129" font-family="'Segoe UI', sans-serif" font-size="7" fill="#881337" text-anchor="middle">Pauses Tool</text>
        <text x="587" y="138" font-family="'Segoe UI', sans-serif" font-size="7" fill="#881337" text-anchor="middle">Execution</text>
        <text x="587" y="158" font-family="'Segoe UI', sans-serif" font-size="7" font-weight="bold" fill="#e11d48" text-anchor="middle">__interrupt__</text>

        <!-- Bottom Feedback Loops -->
        <!-- Interrupt signal back to user -->
        <path d="M 587 170 L 587 215 L 72 215 L 72 160" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="3" marker-end="url(#mw-arrow-red)"/>
        <text x="325" y="210" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#b91c1c" text-anchor="middle">Pause &amp; Emit __interrupt__ (Human reviews: Approve, Edit, Reject via Command)</text>

        <!-- Tool execution loop -->
        <path d="M 625 105 L 640 105 L 640 45 L 222 45 L 222 75" fill="none" stroke="#10b981" stroke-width="1.5" marker-end="url(#mw-arrow-green)"/>
        <text x="430" y="40" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#047857" text-anchor="middle">Approved Tool Execution -&gt; ToolMessage -&gt; Checkpoint Update</text>
    </svg>
    """

def get_svg_summarization_middleware_dataflow():
    """Vector SVG diagram illustrating SummarizationMiddleware Compaction Data Flow."""
    return """
    <svg width="650" height="260" viewBox="0 0 650 260" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <marker id="sm-arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#0284c7" />
            </marker>
            <marker id="sm-arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
            </marker>
        </defs>

        <!-- Left Container: Before Summarization (State Explosion) -->
        <rect x="15" y="20" width="230" height="225" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
        <rect x="15" y="20" width="230" height="28" rx="6" fill="#64748b"/>
        <text x="130" y="39" font-family="'Segoe UI', sans-serif" font-size="10.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Unmanaged State (10 Messages)</text>

        <rect x="25" y="58" width="210" height="20" rx="3" fill="#fee2e2" stroke="#fca5a5"/>
        <text x="35" y="72" font-family="'Consolas', monospace" font-size="8" fill="#991b1b">Msg 1: Human("What is 2+2?")</text>

        <rect x="25" y="82" width="210" height="20" rx="3" fill="#fee2e2" stroke="#fca5a5"/>
        <text x="35" y="96" font-family="'Consolas', monospace" font-size="8" fill="#991b1b">Msg 2: AI("2 + 2 = 4")</text>

        <rect x="25" y="106" width="210" height="20" rx="3" fill="#fee2e2" stroke="#fca5a5"/>
        <text x="35" y="120" font-family="'Consolas', monospace" font-size="8" fill="#991b1b">Msg 3: Human("What is 10*5?")</text>

        <rect x="25" y="130" width="210" height="20" rx="3" fill="#fee2e2" stroke="#fca5a5"/>
        <text x="35" y="144" font-family="'Consolas', monospace" font-size="8" fill="#991b1b">Msg 4: AI("10 * 5 = 50")</text>

        <rect x="25" y="154" width="210" height="20" rx="3" fill="#fee2e2" stroke="#fca5a5"/>
        <text x="35" y="168" font-family="'Consolas', monospace" font-size="8" fill="#991b1b">Msg 5: Human("What is 100/4?")</text>

        <rect x="25" y="178" width="210" height="20" rx="3" fill="#fee2e2" stroke="#fca5a5"/>
        <text x="35" y="192" font-family="'Consolas', monospace" font-size="8" fill="#991b1b">Msg 6: AI("100 / 4 = 25")</text>

        <rect x="25" y="202" width="210" height="35" rx="3" fill="#fef3c7" stroke="#fcd34d"/>
        <text x="130" y="216" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#92400e" text-anchor="middle">Msgs 7–10: 15-7 &amp; 3*3 Q&amp;A</text>
        <text x="130" y="228" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#b45309" text-anchor="middle">Threshold Met: trigger=("messages", 10)</text>

        <!-- Center: Summarization Compactor Engine -->
        <g transform="translate(260, 60)">
            <rect x="0" y="0" width="125" height="145" rx="6" fill="#ecfeff" stroke="#0284c7" stroke-width="1.5"/>
            <text x="62" y="22" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#0369a1" text-anchor="middle">Summarizer LLM</text>
            <text x="62" y="36" font-family="'Segoe UI', sans-serif" font-size="8" fill="#0284c7" text-anchor="middle">Compaction Engine</text>
            
            <line x1="-12" y1="72" x2="-2" y2="72" stroke="#0284c7" stroke-width="2" marker-end="url(#sm-arrow)"/>
            
            <rect x="8" y="48" width="109" height="85" rx="4" fill="#ffffff" stroke="#bae6fd"/>
            <text x="62" y="63" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#0c4a6e" text-anchor="middle">Extracts Key State:</text>
            <text x="14" y="77" font-family="'Consolas', monospace" font-size="7" fill="#0369a1">• SESSION INTENT</text>
            <text x="14" y="90" font-family="'Consolas', monospace" font-size="7" fill="#0369a1">• SUMMARY (Q&amp;A)</text>
            <text x="14" y="103" font-family="'Consolas', monospace" font-size="7" fill="#0369a1">• ARTIFACTS</text>
            <text x="14" y="116" font-family="'Consolas', monospace" font-size="7" fill="#0369a1">• NEXT STEPS</text>
            <text x="62" y="127" font-family="'Segoe UI', sans-serif" font-size="6.5" font-weight="bold" fill="#0284c7" text-anchor="middle">keep=("messages", 4)</text>

            <line x1="126" y1="72" x2="138" y2="72" stroke="#10b981" stroke-width="2" marker-end="url(#sm-arrow-green)"/>
        </g>

        <!-- Right Container: After Summarization (Compressed Clean State) -->
        <rect x="405" y="20" width="230" height="225" rx="6" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5"/>
        <rect x="405" y="20" width="230" height="28" rx="6" fill="#16a34a"/>
        <text x="520" y="39" font-family="'Segoe UI', sans-serif" font-size="10.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Compacted State (6 Messages)</text>

        <!-- 1. Synthetic Summary Message -->
        <rect x="415" y="58" width="210" height="52" rx="4" fill="#dcfce7" stroke="#4ade80" stroke-width="1.2"/>
        <text x="425" y="73" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#166534">1. Injected Summary Message</text>
        <text x="425" y="86" font-family="'Consolas', monospace" font-size="7.5" fill="#15803d">HumanMessage(content="## SUMMARY...")</text>
        <text x="425" y="98" font-family="'Consolas', monospace" font-size="7.5" fill="#166534">additional_kwargs={'lc_source': 'summarization'}</text>

        <!-- 2. Retained Recent Messages (keep=4) -->
        <rect x="415" y="116" width="210" height="22" rx="3" fill="#ffffff" stroke="#bbf7d0"/>
        <text x="425" y="131" font-family="'Consolas', monospace" font-size="7.5" fill="#334155">2. AIMessage("15 - 7 = 8")</text>

        <rect x="415" y="142" width="210" height="22" rx="3" fill="#ffffff" stroke="#bbf7d0"/>
        <text x="425" y="157" font-family="'Consolas', monospace" font-size="7.5" fill="#334155">3. HumanMessage("What is 3*3?")</text>

        <rect x="415" y="168" width="210" height="22" rx="3" fill="#ffffff" stroke="#bbf7d0"/>
        <text x="425" y="183" font-family="'Consolas', monospace" font-size="7.5" fill="#334155">4. AIMessage("3 * 3 = 9")</text>

        <!-- 3. New Turn Messages -->
        <rect x="415" y="194" width="210" height="22" rx="3" fill="#eff6ff" stroke="#93c5fd"/>
        <text x="425" y="209" font-family="'Consolas', monospace" font-size="7.5" fill="#1e40af">5. HumanMessage("What is 4*4?")</text>

        <rect x="415" y="220" width="210" height="20" rx="3" fill="#eff6ff" stroke="#93c5fd"/>
        <text x="425" y="234" font-family="'Consolas', monospace" font-size="7.5" fill="#1e40af">6. AIMessage("4 * 4 = 16")</text>
    </svg>
    """

def get_svg_hitl_middleware_dataflow():
    """Vector SVG diagram illustrating HumanInTheLoopMiddleware 3-Way Decision Data Flow."""
    return """
    <svg width="650" height="300" viewBox="0 0 650 300" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <marker id="hitl-arrow-blue" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
            </marker>
            <marker id="hitl-arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
            </marker>
            <marker id="hitl-arrow-red" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
            </marker>
            <marker id="hitl-arrow-amber" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b" />
            </marker>
        </defs>

        <!-- Top Box: Phase 1 - Tool Interception & Graph Suspension -->
        <rect x="15" y="10" width="620" height="100" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
        <rect x="15" y="10" width="620" height="24" rx="6" fill="#1e293b"/>
        <text x="325" y="27" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#ffffff" text-anchor="middle">Phase 1: Tool Call Interception &amp; State Checkpointing</text>

        <!-- Step 1: LLM Tool Call Request -->
        <rect x="25" y="42" width="175" height="58" rx="4" fill="#faf5ff" stroke="#c084fc"/>
        <text x="112" y="58" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#6b21a8" text-anchor="middle">1. Model Emits Tool Call</text>
        <text x="112" y="72" font-family="'Consolas', monospace" font-size="7.5" fill="#581c87" text-anchor="middle">send_email_tool(recipient=...,</text>
        <text x="112" y="83" font-family="'Consolas', monospace" font-size="7.5" fill="#581c87" text-anchor="middle">subject=..., body=...)</text>

        <line x1="200" y1="71" x2="225" y2="71" stroke="#8b5cf6" stroke-width="1.8" marker-end="url(#hitl-arrow-blue)"/>

        <!-- Step 2: HITL Middleware Intercepts -->
        <rect x="230" y="42" width="180" height="58" rx="4" fill="#fff1f2" stroke="#f43f5e"/>
        <text x="320" y="58" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#be123c" text-anchor="middle">2. HITL Middleware Intercepts</text>
        <text x="320" y="72" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#9f1239" text-anchor="middle">Matches interrupt_on["send_email_tool"]</text>
        <text x="320" y="85" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#e11d48" text-anchor="middle">HALTS execution before tool runs</text>

        <line x1="410" y1="71" x2="435" y2="71" stroke="#f43f5e" stroke-width="1.8" marker-end="url(#hitl-arrow-red)"/>

        <!-- Step 3: Checkpoint & Yield Interrupt -->
        <rect x="440" y="42" width="185" height="58" rx="4" fill="#fef3c7" stroke="#fcd34d"/>
        <text x="532" y="58" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#92400e" text-anchor="middle">3. Yields __interrupt__</text>
        <text x="532" y="72" font-family="'Consolas', monospace" font-size="7.5" fill="#78350f" text-anchor="middle">Saved in checkpointer (thread_id)</text>
        <text x="532" y="85" font-family="'Consolas', monospace" font-size="7" fill="#b45309" text-anchor="middle">allowed_decisions: [approve, edit, reject]</text>

        <!-- Downward connecting lines to Phase 2 branches -->
        <line x1="532" y1="100" x2="532" y2="120" stroke="#64748b" stroke-width="1.5"/>
        <line x1="115" y1="120" x2="532" y2="120" stroke="#64748b" stroke-width="1.5"/>
        <line x1="115" y1="120" x2="115" y2="135" stroke="#10b981" stroke-width="1.5" marker-end="url(#hitl-arrow-green)"/>
        <line x1="325" y1="120" x2="325" y2="135" stroke="#ef4444" stroke-width="1.5" marker-end="url(#hitl-arrow-red)"/>
        <line x1="532" y1="120" x2="532" y2="135" stroke="#f59e0b" stroke-width="1.5" marker-end="url(#hitl-arrow-amber)"/>

        <!-- Bottom Box: Phase 2 - 3-Way Resume Protocol -->
        <!-- Branch A: APPROVE -->
        <rect x="15" y="140" width="195" height="150" rx="6" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5"/>
        <rect x="15" y="140" width="195" height="24" rx="6" fill="#16a34a"/>
        <text x="112" y="156" font-family="'Segoe UI', sans-serif" font-size="9.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Branch A: Approve (Cell 8)</text>
        <rect x="25" y="172" width="175" height="32" rx="3" fill="#dcfce7"/>
        <text x="112" y="185" font-family="'Consolas', monospace" font-size="7.5" font-weight="bold" fill="#14532d" text-anchor="middle">Command(resume={</text>
        <text x="112" y="196" font-family="'Consolas', monospace" font-size="7.5" font-weight="bold" fill="#14532d" text-anchor="middle">"decisions": [{"type":"approve"}]})</text>
        <text x="112" y="220" font-family="'Segoe UI', sans-serif" font-size="8" fill="#166534" text-anchor="middle">1. Tool executes with original args</text>
        <text x="112" y="234" font-family="'Segoe UI', sans-serif" font-size="8" fill="#166534" text-anchor="middle">2. Real email dispatched</text>
        <rect x="25" y="248" width="175" height="32" rx="3" fill="#ffffff" stroke="#86efac"/>
        <text x="112" y="261" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#15803d" text-anchor="middle">Final Model Output:</text>
        <text x="112" y="273" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#166534" text-anchor="middle">"✅ Email has been sent to..."</text>

        <!-- Branch B: REJECT -->
        <rect x="225" y="140" width="200" height="150" rx="6" fill="#fef2f2" stroke="#fca5a5" stroke-width="1.5"/>
        <rect x="225" y="140" width="200" height="24" rx="6" fill="#dc2626"/>
        <text x="325" y="156" font-family="'Segoe UI', sans-serif" font-size="9.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Branch B: Reject (Cell 9)</text>
        <rect x="235" y="172" width="180" height="32" rx="3" fill="#fee2e2"/>
        <text x="325" y="185" font-family="'Consolas', monospace" font-size="7.5" fill="#7f1d1d" text-anchor="middle">Command(resume={</text>
        <text x="325" y="196" font-family="'Consolas', monospace" font-size="7.5" fill="#7f1d1d" text-anchor="middle">"decisions": [{"type":"reject"}]})</text>
        <text x="325" y="220" font-family="'Segoe UI', sans-serif" font-size="8" fill="#991b1b" text-anchor="middle">1. Tool execution bypassed completely</text>
        <text x="325" y="234" font-family="'Segoe UI', sans-serif" font-size="8" fill="#991b1b" text-anchor="middle">2. Model receives rejection notice</text>
        <rect x="235" y="248" width="180" height="32" rx="3" fill="#ffffff" stroke="#fca5a5"/>
        <text x="325" y="261" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#b91c1c" text-anchor="middle">Polite Fallback Output:</text>
        <text x="325" y="273" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#991b1b" text-anchor="middle">"I'm sorry, I can't send it now..."</text>

        <!-- Branch C: EDIT -->
        <rect x="440" y="140" width="195" height="150" rx="6" fill="#fffbeb" stroke="#fde68a" stroke-width="1.5"/>
        <rect x="440" y="140" width="195" height="24" rx="6" fill="#d97706"/>
        <text x="537" y="156" font-family="'Segoe UI', sans-serif" font-size="9.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Branch C: Edit (Cell 10)</text>
        <rect x="448" y="172" width="179" height="32" rx="3" fill="#fef3c7"/>
        <text x="537" y="184" font-family="'Consolas', monospace" font-size="7" font-weight="bold" fill="#78350f" text-anchor="middle">Command(resume={"decisions": [{</text>
        <text x="537" y="195" font-family="'Consolas', monospace" font-size="7" font-weight="bold" fill="#78350f" text-anchor="middle">"type":"edit", "edited_action":..}]})</text>
        <text x="537" y="220" font-family="'Segoe UI', sans-serif" font-size="7.8" fill="#92400e" text-anchor="middle">1. Human fixes typo in recipient</text>
        <text x="537" y="234" font-family="'Segoe UI', sans-serif" font-size="7.8" fill="#92400e" text-anchor="middle">2. Tool runs with corrected args</text>
        <rect x="448" y="248" width="179" height="32" rx="3" fill="#ffffff" stroke="#fde68a"/>
        <text x="537" y="261" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#b45309" text-anchor="middle">Corrected Execution:</text>
        <text x="537" y="273" font-family="'Segoe UI', sans-serif" font-size="7.5" fill="#92400e" text-anchor="middle">"✅ Email sent to varad0404@..."</text>
    </svg>
    """

def get_svg_langgraph_state_machine():
    """Vector SVG diagram illustrating LangGraph State Machine, State TypedDict, and add_messages reducer."""
    return """
    <svg width="680" height="230" viewBox="0 0 680 230" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <marker id="sm-arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
            </marker>
            <marker id="sm-arrow-purple" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#7c3aed" />
            </marker>
            <marker id="sm-arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#059669" />
            </marker>
        </defs>

        <!-- 1. State Definition & Reducer Box -->
        <rect x="10" y="15" width="200" height="200" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
        <rect x="10" y="15" width="200" height="30" rx="8" fill="#3b82f6"/>
        <text x="110" y="35" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">1. State Definition &amp; Reducer</text>
        
        <rect x="22" y="55" width="176" height="38" rx="4" fill="#ffffff" stroke="#bfdbfe"/>
        <text x="30" y="70" font-family="'Courier New', monospace" font-size="8" font-weight="bold" fill="#1e3a8a">class State(TypedDict):</text>
        <text x="42" y="83" font-family="'Courier New', monospace" font-size="7.5" fill="#2563eb">messages: Annotated[list,</text>
        <text x="105" y="83" font-family="'Courier New', monospace" font-size="7.5" font-weight="bold" fill="#dc2626">add_messages]</text>

        <text x="110" y="110" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#1e40af" text-anchor="middle">add_messages Reducer Role:</text>
        <text x="25" y="128" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155">• Appends new incoming messages</text>
        <text x="25" y="143" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155">• Overwrites by matching message ID</text>
        <text x="25" y="158" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155">• Converts strings/dicts to BaseMessage</text>
        <rect x="22" y="172" width="176" height="30" rx="4" fill="#dbeafe"/>
        <text x="110" y="186" font-family="'Segoe UI', sans-serif" font-size="7.8" font-weight="bold" fill="#1e40af" text-anchor="middle">Prevents State Key Overwrites!</text>
        <text x="110" y="196" font-family="'Segoe UI', sans-serif" font-size="7.2" fill="#1e3a8a" text-anchor="middle">(Accumulates turn history)</text>

        <!-- Arrow 1 to 2 -->
        <line x1="210" y1="115" x2="235" y2="115" stroke="#3b82f6" stroke-width="2" marker-end="url(#sm-arrow)"/>

        <!-- 2. Node Function Box -->
        <rect x="240" y="15" width="200" height="200" rx="8" fill="#faf5ff" stroke="#8b5cf6" stroke-width="1.5"/>
        <rect x="240" y="15" width="200" height="30" rx="8" fill="#8b5cf6"/>
        <text x="340" y="35" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">2. Node Function (Brain)</text>

        <rect x="252" y="55" width="176" height="48" rx="4" fill="#ffffff" stroke="#e9d5ff"/>
        <text x="260" y="70" font-family="'Courier New', monospace" font-size="8" font-weight="bold" fill="#581c87">def chatbot(state: State):</text>
        <text x="272" y="83" font-family="'Courier New', monospace" font-size="7.5" fill="#6b21a8">return {"messages": [</text>
        <text x="284" y="95" font-family="'Courier New', monospace" font-size="7.5" fill="#6b21a8">llm.invoke(state["messages"])]}</text>

        <text x="340" y="120" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#6b21a8" text-anchor="middle">Execution Principles:</text>
        <text x="255" y="138" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155">• Receives full state dict snapshot</text>
        <text x="255" y="153" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155">• Returns partial delta update dict</text>
        <text x="255" y="168" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155">• Never mutates state in-place</text>
        <rect x="252" y="176" width="176" height="26" rx="4" fill="#f3e8ff"/>
        <text x="340" y="193" font-family="'Segoe UI', sans-serif" font-size="7.8" font-weight="bold" fill="#6b21a8" text-anchor="middle">Pure Functional State Transformation</text>

        <!-- Arrow 2 to 3 -->
        <line x1="440" y1="115" x2="465" y2="115" stroke="#8b5cf6" stroke-width="2" marker-end="url(#sm-arrow-purple)"/>

        <!-- 3. Compiled Graph Engine Box -->
        <rect x="470" y="15" width="200" height="200" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
        <rect x="470" y="15" width="200" height="30" rx="8" fill="#10b981"/>
        <text x="570" y="35" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="bold" fill="#ffffff" text-anchor="middle">3. Compiled StateGraph</text>

        <g transform="translate(485, 55)">
            <circle cx="20" cy="25" r="16" fill="#64748b"/>
            <text x="20" y="28" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#ffffff" text-anchor="middle">START</text>

            <line x1="36" y1="25" x2="60" y2="25" stroke="#64748b" stroke-width="2" marker-end="url(#sm-arrow)"/>

            <rect x="62" y="10" width="56" height="30" rx="5" fill="#8b5cf6"/>
            <text x="90" y="28" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#ffffff" text-anchor="middle">chatbot</text>

            <line x1="118" y1="25" x2="140" y2="25" stroke="#64748b" stroke-width="2" marker-end="url(#sm-arrow)"/>

            <circle cx="156" cy="25" r="16" fill="#0f172a"/>
            <text x="156" y="28" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#ffffff" text-anchor="middle">END</text>
        </g>

        <text x="570" y="118" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#065f46" text-anchor="middle">Compilation Lifecycle:</text>
        <text x="485" y="136" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155">• Validates node connectivity &amp; edges</text>
        <text x="485" y="151" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155">• Binds optional state checkpointer</text>
        <text x="485" y="166" font-family="'Segoe UI', sans-serif" font-size="8" fill="#334155">• Exposes .invoke(), .stream(), .astream()</text>
        <rect x="482" y="176" width="176" height="26" rx="4" fill="#d1fae5"/>
        <text x="570" y="193" font-family="'Segoe UI', sans-serif" font-size="7.8" font-weight="bold" fill="#065f46" text-anchor="middle">CompiledStateGraph Executable</text>
    </svg>
    """

def get_svg_langgraph_react_cycle():
    """Vector SVG comparing Static Linear Tool Graph (Cell 8) vs ReAct Dynamic Cyclic Graph (Cell 10)."""
    return """
    <svg width="680" height="280" viewBox="0 0 680 280" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <marker id="rc-arrow-blue" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
            </marker>
            <marker id="rc-arrow-purple" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#7c3aed" />
            </marker>
            <marker id="rc-arrow-amber" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#d97706" />
            </marker>
            <marker id="rc-arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#059669" />
            </marker>
            <marker id="rc-arrow-red" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626" />
            </marker>
        </defs>

        <!-- TOP PANEL: Cell 8 Static Tool Graph (Terminal Dead End) -->
        <rect x="10" y="10" width="660" height="115" rx="8" fill="#fef2f2" stroke="#fca5a5" stroke-width="1.5"/>
        <rect x="10" y="10" width="660" height="24" rx="8" fill="#ef4444"/>
        <text x="25" y="26" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#ffffff">A. Cell 8 Static Tool Execution Graph (Premature Termination / Broken Feedback Loop)</text>

        <!-- Nodes in Row 1 -->
        <!-- START -->
        <circle cx="45" cy="72" r="15" fill="#64748b"/>
        <text x="45" y="75" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#ffffff" text-anchor="middle">START</text>

        <line x1="60" y1="72" x2="85" y2="72" stroke="#64748b" stroke-width="2" marker-end="url(#rc-arrow-blue)"/>

        <!-- tool_calling_llm -->
        <rect x="90" y="52" width="115" height="40" rx="6" fill="#8b5cf6"/>
        <text x="147" y="68" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">tool_calling_llm</text>
        <text x="147" y="82" font-family="'Courier New', monospace" font-size="7" fill="#ede9fe" text-anchor="middle">llm.bind_tools()</text>

        <!-- Conditional Diamond: tools_condition -->
        <line x1="205" y1="72" x2="235" y2="72" stroke="#8b5cf6" stroke-width="2" marker-end="url(#rc-arrow-purple)"/>

        <polygon points="270,50 305,72 270,94 235,72" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
        <text x="270" y="70" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#92400e" text-anchor="middle">tools_</text>
        <text x="270" y="80" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#92400e" text-anchor="middle">condition</text>

        <!-- Path to tools -->
        <line x1="305" y1="72" x2="340" y2="72" stroke="#d97706" stroke-width="2" marker-end="url(#rc-arrow-amber)"/>
        <text x="322" y="64" font-family="'Segoe UI', sans-serif" font-size="7" font-weight="bold" fill="#b45309">tools</text>

        <!-- tools Node -->
        <rect x="345" y="52" width="100" height="40" rx="6" fill="#10b981"/>
        <text x="395" y="68" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">tools (ToolNode)</text>
        <text x="395" y="82" font-family="'Segoe UI', sans-serif" font-size="7" fill="#d1fae5" text-anchor="middle">Tavily / Multiply</text>

        <!-- Dead end edge to END -->
        <line x1="445" y1="72" x2="480" y2="72" stroke="#dc2626" stroke-width="2.5" marker-end="url(#rc-arrow-red)"/>

        <!-- END -->
        <circle cx="500" cy="72" r="15" fill="#dc2626"/>
        <text x="500" y="75" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#ffffff" text-anchor="middle">END</text>

        <!-- Warning Callout Box on Right -->
        <rect x="530" y="44" width="130" height="56" rx="4" fill="#fee2e2" stroke="#f87171"/>
        <text x="595" y="58" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#991b1b" text-anchor="middle">Flaw: No Feedback Loop!</text>
        <text x="536" y="72" font-family="'Segoe UI', sans-serif" font-size="6.8" fill="#7f1d1d">• ToolMessage is stored</text>
        <text x="536" y="83" font-family="'Segoe UI', sans-serif" font-size="6.8" fill="#7f1d1d">• LLM never sees tool output</text>
        <text x="536" y="94" font-family="'Segoe UI', sans-serif" font-size="6.8" fill="#7f1d1d">• No final answer generated</text>


        <!-- BOTTOM PANEL: Cell 10 ReAct Dynamic Cyclic Execution Loop -->
        <rect x="10" y="135" width="660" height="135" rx="8" fill="#f0fdf4" stroke="#86efac" stroke-width="1.5"/>
        <rect x="10" y="135" width="660" height="24" rx="8" fill="#16a34a"/>
        <text x="25" y="151" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#ffffff">B. Cell 10 ReAct Cyclic Execution Graph (Closed-Loop Reasoning &amp; Acting Agent)</text>

        <!-- START -->
        <circle cx="45" cy="195" r="15" fill="#64748b"/>
        <text x="45" y="198" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#ffffff" text-anchor="middle">START</text>

        <line x1="60" y1="195" x2="85" y2="195" stroke="#64748b" stroke-width="2" marker-end="url(#rc-arrow-blue)"/>

        <!-- tool_calling_llm -->
        <rect x="90" y="175" width="115" height="40" rx="6" fill="#8b5cf6"/>
        <text x="147" y="191" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">tool_calling_llm</text>
        <text x="147" y="205" font-family="'Courier New', monospace" font-size="7" fill="#ede9fe" text-anchor="middle">llm_with_tool</text>

        <line x1="205" y1="195" x2="235" y2="195" stroke="#8b5cf6" stroke-width="2" marker-end="url(#rc-arrow-purple)"/>

        <!-- tools_condition diamond -->
        <polygon points="270,173 305,195 270,217 235,195" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
        <text x="270" y="193" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#92400e" text-anchor="middle">tools_</text>
        <text x="270" y="203" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#92400e" text-anchor="middle">condition</text>

        <!-- Branch 1: If tool calls exist -> tools -->
        <line x1="305" y1="195" x2="340" y2="195" stroke="#d97706" stroke-width="2" marker-end="url(#rc-arrow-amber)"/>
        <text x="322" y="187" font-family="'Segoe UI', sans-serif" font-size="7" font-weight="bold" fill="#b45309">tools</text>

        <!-- tools Node -->
        <rect x="345" y="175" width="100" height="40" rx="6" fill="#10b981"/>
        <text x="395" y="191" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">tools (ToolNode)</text>
        <text x="395" y="205" font-family="'Segoe UI', sans-serif" font-size="7" fill="#d1fae5" text-anchor="middle">Executes Python Tools</text>

        <!-- CYCLIC EDGE: tools back to tool_calling_llm -->
        <path d="M 395 215 L 395 250 L 147 250 L 147 220" fill="none" stroke="#059669" stroke-width="2.5" stroke-dasharray="4" marker-end="url(#rc-arrow-green)"/>
        <text x="270" y="244" font-family="'Segoe UI', sans-serif" font-size="7.8" font-weight="bold" fill="#047857" text-anchor="middle">Cyclic Feedback Edge: builder.add_edge("tools", "tool_calling_llm")</text>

        <!-- Branch 2: tools_condition -> END (when no tool calls exist) -->
        <path d="M 270 173 L 270 152 L 480 152 L 480 185" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#rc-arrow-blue)"/>
        <text x="375" y="148" font-family="'Segoe UI', sans-serif" font-size="7" font-weight="bold" fill="#475569">END (Final Answer Synthesized)</text>

        <!-- END Node -->
        <circle cx="480" cy="195" r="15" fill="#0f172a"/>
        <text x="480" y="198" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#ffffff" text-anchor="middle">END</text>

        <!-- Success Callout Box on Right -->
        <rect x="520" y="168" width="140" height="70" rx="4" fill="#dcfce7" stroke="#4ade80"/>
        <text x="590" y="182" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#14532d" text-anchor="middle">True ReAct Convergence</text>
        <text x="526" y="196" font-family="'Segoe UI', sans-serif" font-size="6.8" fill="#166534">• Observation returned</text>
        <text x="526" y="208" font-family="'Segoe UI', sans-serif" font-size="6.8" fill="#166534">• LLM synthesizes answer</text>
        <text x="526" y="220" font-family="'Segoe UI', sans-serif" font-size="6.8" fill="#166534">• Multi-hop chaining enabled</text>
        <text x="526" y="232" font-family="'Segoe UI', sans-serif" font-size="6.8" fill="#166534">• Terminates when done</text>
    </svg>
    """

def get_svg_langgraph_memory_saver():
    """Vector SVG illustrating MemorySaver checkpointer, thread_id session isolation, and multi-turn persistence."""
    return """
    <svg width="680" height="245" viewBox="0 0 680 245" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <marker id="ms-arrow-blue" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
            </marker>
            <marker id="ms-arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#059669" />
            </marker>
            <marker id="ms-arrow-purple" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#7c3aed" />
            </marker>
        </defs>

        <!-- Outer Framework Boundary -->
        <rect x="10" y="10" width="660" height="225" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
        <text x="25" y="28" font-family="'Segoe UI', sans-serif" font-size="10.5" font-weight="bold" fill="#1e293b">LangGraph State Checkpointing Architecture (MemorySaver &amp; thread_id Isolation)</text>

        <!-- TURN 1 COLUMN -->
        <rect x="25" y="42" width="200" height="180" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="1"/>
        <rect x="25" y="42" width="200" height="22" rx="6" fill="#3b82f6"/>
        <text x="125" y="57" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Turn 1 (thread_id: "1")</text>

        <rect x="35" y="72" width="180" height="34" rx="4" fill="#ffffff" stroke="#bfdbfe"/>
        <text x="42" y="84" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#1e40af">Client Invocation 1:</text>
        <text x="42" y="96" font-family="'Courier New', monospace" font-size="7" fill="#1e293b">{"messages": "Hi my name is Varad"}</text>

        <line x1="125" y1="108" x2="125" y2="122" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#ms-arrow-blue)"/>

        <rect x="35" y="125" width="180" height="32" rx="4" fill="#dbeafe"/>
        <text x="125" y="138" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#1e3a8a" text-anchor="middle">Agent Processing &amp; Output</text>
        <text x="125" y="149" font-family="'Courier New', monospace" font-size="7" fill="#1e40af" text-anchor="middle">"Hello Varad! How can I help?"</text>

        <line x1="125" y1="160" x2="125" y2="174" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#ms-arrow-blue)"/>

        <rect x="35" y="177" width="180" height="36" rx="4" fill="#bfdbfe"/>
        <text x="125" y="189" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#1e3a8a" text-anchor="middle">Checkpoint Snapshot Saved</text>
        <text x="125" y="201" font-family="'Segoe UI', sans-serif" font-size="6.8" fill="#1e40af" text-anchor="middle">Key: thread_id="1", state=[H1, A1]</text>

        <!-- TURN 2 COLUMN -->
        <rect x="240" y="42" width="200" height="180" rx="6" fill="#f0fdf4" stroke="#86efac" stroke-width="1"/>
        <rect x="240" y="42" width="200" height="22" rx="6" fill="#16a34a"/>
        <text x="340" y="57" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Turn 2 (thread_id: "1")</text>

        <rect x="250" y="72" width="180" height="34" rx="4" fill="#ffffff" stroke="#bbf7d0"/>
        <text x="257" y="84" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#166534">Client Invocation 2 (No History!):</text>
        <text x="257" y="96" font-family="'Courier New', monospace" font-size="7" fill="#1e293b">{"messages": "what is my name"}</text>

        <line x1="340" y1="108" x2="340" y2="122" stroke="#16a34a" stroke-width="1.5" marker-end="url(#ms-arrow-green)"/>

        <rect x="250" y="125" width="180" height="32" rx="4" fill="#dcfce7"/>
        <text x="340" y="137" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#14532d" text-anchor="middle">Checkpointer Restores [H1, A1]</text>
        <text x="340" y="148" font-family="'Segoe UI', sans-serif" font-size="7" fill="#166534" text-anchor="middle">add_messages merges new query H2</text>

        <line x1="340" y1="160" x2="340" y2="174" stroke="#16a34a" stroke-width="1.5" marker-end="url(#ms-arrow-green)"/>

        <rect x="250" y="177" width="180" height="36" rx="4" fill="#bbf7d0"/>
        <text x="340" y="189" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#14532d" text-anchor="middle">Accurate Contextual Recall!</text>
        <text x="340" y="201" font-family="'Courier New', monospace" font-size="7" font-weight="bold" fill="#047857" text-anchor="middle">'Your name is Varad.'</text>

        <!-- THREAD ISOLATION COLUMN -->
        <rect x="455" y="42" width="200" height="180" rx="6" fill="#faf5ff" stroke="#d8b4fe" stroke-width="1"/>
        <rect x="455" y="42" width="200" height="22" rx="6" fill="#9333ea"/>
        <text x="555" y="57" font-family="'Segoe UI', sans-serif" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Thread Isolation (thread_id: "2")</text>

        <rect x="465" y="72" width="180" height="34" rx="4" fill="#ffffff" stroke="#e9d5ff"/>
        <text x="472" y="84" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#6b21a8">New Conversation Branch:</text>
        <text x="472" y="96" font-family="'Courier New', monospace" font-size="7" fill="#1e293b">config={"thread_id": "2"}</text>

        <line x1="555" y1="108" x2="555" y2="122" stroke="#9333ea" stroke-width="1.5" marker-end="url(#ms-arrow-purple)"/>

        <rect x="465" y="125" width="180" height="32" rx="4" fill="#f3e8ff"/>
        <text x="555" y="137" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#581c87" text-anchor="middle">Zero Cross-Session Leakage</text>
        <text x="555" y="148" font-family="'Segoe UI', sans-serif" font-size="7" fill="#6b21a8" text-anchor="middle">Fresh isolated checkpoint partition</text>

        <line x1="555" y1="160" x2="555" y2="174" stroke="#9333ea" stroke-width="1.5" marker-end="url(#ms-arrow-purple)"/>

        <rect x="465" y="177" width="180" height="36" rx="4" fill="#e9d5ff"/>
        <text x="555" y="189" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#581c87" text-anchor="middle">Enterprise Multi-Tenancy</text>
        <text x="555" y="201" font-family="'Segoe UI', sans-serif" font-size="6.8" fill="#581c87" text-anchor="middle">Supports thousands of user sessions</text>
    </svg>
    """

def get_svg_langgraph_streaming_modes():
    """Vector SVG illustrating comparison of updates vs values vs astream_events v2."""
    return """
    <svg width="680" height="235" viewBox="0 0 680 235" xmlns="http://www.w3.org/2000/svg">
        <!-- 1. Stream Mode Updates -->
        <rect x="10" y="10" width="210" height="215" rx="8" fill="#f8fafc" stroke="#3b82f6" stroke-width="1.5"/>
        <rect x="10" y="10" width="210" height="28" rx="8" fill="#3b82f6"/>
        <text x="115" y="28" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#ffffff" text-anchor="middle">1. stream_mode="updates"</text>

        <rect x="20" y="48" width="190" height="30" rx="4" fill="#eff6ff"/>
        <text x="115" y="62" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#1e40af" text-anchor="middle">Granularity: Node Mutation Delta</text>
        <text x="115" y="73" font-family="'Segoe UI', sans-serif" font-size="7" fill="#3b82f6" text-anchor="middle">Yields ONLY what the node returned</text>

        <rect x="20" y="85" width="190" height="80" rx="4" fill="#ffffff" stroke="#cbd5e1"/>
        <text x="26" y="99" font-family="'Courier New', monospace" font-size="7.2" font-weight="bold" fill="#0f172a"># Emitted Chunk Structure:</text>
        <text x="26" y="113" font-family="'Courier New', monospace" font-size="7" fill="#2563eb">{</text>
        <text x="34" y="125" font-family="'Courier New', monospace" font-size="7" fill="#1d4ed8">'SuperBot': {</text>
        <text x="44" y="137" font-family="'Courier New', monospace" font-size="7" fill="#059669">'messages': [AIMessage(...)]</text>
        <text x="34" y="149" font-family="'Courier New', monospace" font-size="7" fill="#1d4ed8">}</text>
        <text x="26" y="161" font-family="'Courier New', monospace" font-size="7" fill="#2563eb">}</text>

        <rect x="20" y="172" width="190" height="42" rx="4" fill="#dbeafe"/>
        <text x="115" y="186" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#1e40af" text-anchor="middle">Best Used For:</text>
        <text x="115" y="198" font-family="'Segoe UI', sans-serif" font-size="7" fill="#1e3a8a" text-anchor="middle">• Targeted state diffing</text>
        <text x="115" y="208" font-family="'Segoe UI', sans-serif" font-size="7" fill="#1e3a8a" text-anchor="middle">• Node execution monitoring &amp; audit</text>

        <!-- 2. Stream Mode Values -->
        <rect x="235" y="10" width="210" height="215" rx="8" fill="#f8fafc" stroke="#10b981" stroke-width="1.5"/>
        <rect x="235" y="10" width="210" height="28" rx="8" fill="#10b981"/>
        <text x="340" y="28" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#ffffff" text-anchor="middle">2. stream_mode="values"</text>

        <rect x="245" y="48" width="190" height="30" rx="4" fill="#ecfdf5"/>
        <text x="340" y="62" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#065f46" text-anchor="middle">Granularity: Full Graph Snapshot</text>
        <text x="340" y="73" font-family="'Segoe UI', sans-serif" font-size="7" fill="#059669" text-anchor="middle">Yields complete state after each node</text>

        <rect x="245" y="85" width="190" height="80" rx="4" fill="#ffffff" stroke="#cbd5e1"/>
        <text x="251" y="99" font-family="'Courier New', monospace" font-size="7.2" font-weight="bold" fill="#0f172a"># Emitted Chunk Structure:</text>
        <text x="251" y="113" font-family="'Courier New', monospace" font-size="7" fill="#059669">{</text>
        <text x="259" y="125" font-family="'Courier New', monospace" font-size="7" fill="#047857">'messages': [</text>
        <text x="269" y="137" font-family="'Courier New', monospace" font-size="7" fill="#1e293b">HumanMessage(...),</text>
        <text x="269" y="149" font-family="'Courier New', monospace" font-size="7" fill="#1e293b">AIMessage(...)</text>
        <text x="259" y="161" font-family="'Courier New', monospace" font-size="7" fill="#047857">]</text>
        <text x="251" y="173" font-family="'Courier New', monospace" font-size="7" fill="#059669">}</text>

        <rect x="245" y="172" width="190" height="42" rx="4" fill="#d1fae5"/>
        <text x="340" y="186" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#065f46" text-anchor="middle">Best Used For:</text>
        <text x="340" y="198" font-family="'Segoe UI', sans-serif" font-size="7" fill="#065f46" text-anchor="middle">• Real-time UI conversation feeds</text>
        <text x="340" y="208" font-family="'Segoe UI', sans-serif" font-size="7" fill="#065f46" text-anchor="middle">• Rendering cumulative message history</text>

        <!-- 3. astream_events v2 -->
        <rect x="460" y="10" width="210" height="215" rx="8" fill="#f8fafc" stroke="#8b5cf6" stroke-width="1.5"/>
        <rect x="460" y="10" width="210" height="28" rx="8" fill="#8b5cf6"/>
        <text x="565" y="28" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#ffffff" text-anchor="middle">3. astream_events(..., version="v2")</text>

        <rect x="470" y="48" width="190" height="30" rx="4" fill="#f5f3ff"/>
        <text x="565" y="62" font-family="'Segoe UI', sans-serif" font-size="8" font-weight="bold" fill="#581c87" text-anchor="middle">Granularity: Token &amp; Lifecycle Events</text>
        <text x="565" y="73" font-family="'Segoe UI', sans-serif" font-size="7" fill="#7c3aed" text-anchor="middle">Yields fine-grained execution events</text>

        <rect x="470" y="85" width="190" height="80" rx="4" fill="#ffffff" stroke="#cbd5e1"/>
        <text x="476" y="99" font-family="'Courier New', monospace" font-size="7.2" font-weight="bold" fill="#0f172a"># Emitted Event Timeline:</text>
        <text x="476" y="113" font-family="'Courier New', monospace" font-size="7" fill="#6b21a8">• on_chain_start</text>
        <text x="476" y="125" font-family="'Courier New', monospace" font-size="7" fill="#6b21a8">• on_chat_model_start</text>
        <text x="476" y="137" font-family="'Courier New', monospace" font-size="7" font-weight="bold" fill="#dc2626">• on_chat_model_stream (tokens)</text>
        <text x="476" y="149" font-family="'Courier New', monospace" font-size="7" fill="#6b21a8">• on_chat_model_end</text>
        <text x="476" y="161" font-family="'Courier New', monospace" font-size="7" fill="#6b21a8">• on_chain_end</text>

        <rect x="470" y="172" width="190" height="42" rx="4" fill="#ede9fe"/>
        <text x="565" y="186" font-family="'Segoe UI', sans-serif" font-size="7.5" font-weight="bold" fill="#581c87" text-anchor="middle">Best Used For:</text>
        <text x="565" y="198" font-family="'Segoe UI', sans-serif" font-size="7" fill="#581c87" text-anchor="middle">• Typewriter token streaming in UI</text>
        <text x="565" y="208" font-family="'Segoe UI', sans-serif" font-size="7" fill="#581c87" text-anchor="middle">• Reasoning tokens &amp; latency profiling</text>
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
    elif "4-messages" in fname:
        return build_guide_4(fname, cells, today)
    elif "5-structure" in fname:
        return build_guide_5(fname, cells, today)
    elif "6-middleware" in fname:
        return build_guide_6(fname, cells, today)
    elif "1-BasicChatBot" in fname:
        return build_guide_langgraph_1(fname, cells, today)
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

def build_guide_4(fname, cells, today):
    """Build canonical 12-section educational guide for 4-messages.ipynb."""
    svg_diagram = get_svg_messages_hierarchy()
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>__FNAME__ - Educational Study Guide</title>
    <style>__CSS_STYLES__</style>
</head>
<body>

<!-- Section A: Cover Page -->
<div class="cover-page">
    <span class="cover-badge">LangChain 1.4+ • Core Foundation Guide</span>
    <h1 class="cover-title">LangChain Core Message Architecture</h1>
    <p class="cover-subtitle">Mastering SystemMessage, HumanMessage, AIMessage, and ToolMessage in Conversational Agents</p>
    
    <p style="font-size: 10.5pt; color: #475569; max-width: 580px; margin-top: 15px;">
        An authoritative technical deep dive into LangChain's message polymorphism. Deconstructs role-based
        conversational state, persona steering, metadata tracing (<code>name</code>, <code>id</code>), historical message
        injection, and the multi-turn tool calling handshake.
    </p>

    <div class="cover-meta">
        <div class="cover-meta-grid">
            <div class="meta-item"><strong>Target Notebook:</strong> <code>__FNAME__</code></div>
            <div class="meta-item"><strong>Generation Date:</strong> __TODAY__</div>
            <div class="meta-item"><strong>Language & Runtime:</strong> Python 3.14 • Virtualenv (.venv)</div>
            <div class="meta-item"><strong>Core Framework:</strong> LangChain 1.4.7 • Groq (openai/gpt-oss-20b)</div>
        </div>
    </div>
</div>

<!-- Section B: Learning Objectives -->
<h2>B. Learning Objectives</h2>
<p>After studying this notebook and study guide, you will master:</p>
<ul>
    <li><strong>Core Message Class Polymorphism:</strong> Understand how <code>BaseMessage</code> serves as the parent abstraction for <code>SystemMessage</code>, <code>HumanMessage</code>, <code>AIMessage</code>, and <code>ToolMessage</code>.</li>
    <li><strong>Persona Steering via System Prompts:</strong> Direct the model's domain expertise, tone, formatting constraints, and reasoning protocols using <code>SystemMessage</code>.</li>
    <li><strong>Speaker Identification & Observability:</strong> Use optional message metadata attributes (<code>name</code> for multi-agent disambiguation and <code>id</code> for distributed execution tracing).</li>
    <li><strong>Context Seeding & Conversation History:</strong> Manually reconstruct multi-turn dialogue histories using synthetic <code>AIMessage</code> exemplars.</li>
    <li><strong>The Two-Turn Tool Handshake:</strong> Deconstruct the exact protocol linking <code>AIMessage.tool_calls</code> to <code>ToolMessage(tool_call_id=...)</code> for autonomous tool execution.</li>
    <li><strong>Provider-Agnostic Message Normalization:</strong> Recognize how LangChain bridges native provider message formats across Groq, OpenAI, Anthropic, and Google GenAI.</li>
</ul>

<!-- Section C: Prerequisites & Setup -->
<h2>C. Prerequisites & Setup</h2>
<div class="callout callout-note">
    <div class="callout-title">Environment Specification</div>
    This notebook runs against the high-throughput <strong>Groq LPU Inference Cloud</strong> executing the <code>openai/gpt-oss-20b</code> open-weights reasoning model.
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
        <td>Modern runtime supporting advanced type hinting and fast async execution.</td>
    </tr>
    <tr>
        <td>Virtual Environment</td>
        <td><code>.venv</code> (managed via <code>uv</code>)</td>
        <td>Strictly isolates dependencies defined in <code>pyproject.toml</code>.</td>
    </tr>
    <tr>
        <td>Environment File</td>
        <td><code>.env</code> in workspace root</td>
        <td>Securely provides <code>GROQ_API_KEY</code> without hardcoding credentials.</td>
    </tr>
    <tr>
        <td>Core Dependencies</td>
        <td><code>langchain>=1.4.7</code>, <code>langchain-groq</code>, <code>python-dotenv</code></td>
        <td>Supplies universal chat model interfaces and provider bridge drivers.</td>
    </tr>
</table>
<div class="callout callout-warning">
    <div class="callout-title">Security Best Practice</div>
    Never commit real API keys to version control. Always verify that <code>.env</code> is tracked in <code>.gitignore</code> and use <code>.env.example</code> for team onboarding.
</div>

<!-- Section D: Topic Overview -->
<div class="page-break-before"></div>
<h2>D. Topic Overview: The Architecture of Structured Messages</h2>
<p>
    In simplistic LLM interactions, prompts are passed as plain strings: <code>model.invoke("Who are you?")</code>. However, production agentic architectures and conversational applications cannot rely on unstructured strings. Real-world LLM APIs (including OpenAI ChatML, Anthropic Messages API, and Groq) expect a chronological array of distinct message objects, each representing an explicit role and semantic purpose.
</p>
<p>
    LangChain models this reality through a polymorphic hierarchy rooted in <code>BaseMessage</code> (located in <code>langchain_core.messages</code>). Each message subclass encapsulates:
</p>
<ol>
    <li><strong>Role Semantics:</strong> Identifies whether the content originates from the system administrator (<code>SystemMessage</code>), the end user (<code>HumanMessage</code>), the generative assistant (<code>AIMessage</code>), or external code execution (<code>ToolMessage</code>).</li>
    <li><strong>Structured Payloads:</strong> Allows messages to carry structured metadata beyond plain strings, such as <code>tool_calls</code> dictionaries, token usage records, and cryptographic signatures.</li>
    <li><strong>Observability Attributes:</strong> Provides native properties including <code>id</code> (for LangSmith distributed tracing) and <code>name</code> (for differentiating distinct speakers in multi-agent collaboration).</li>
</ol>

<!-- Section E: Detailed Notebook Walkthrough -->
<h2>E. Detailed Notebook Walkthrough & Cell Dissection</h2>

<h3>Cell 0: Markdown Section Header</h3>
<pre><code>### Message</code></pre>
<p><strong>Analysis:</strong> Establishes the study module exploring LangChain's message system.</p>

<h3>Cell 1: Baseline Invocation & Chat Model Initialization</h3>
<pre><code>import os
from langchain.chat_models import init_chat_model

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

model = init_chat_model("groq:openai/gpt-oss-20b")

model.invoke("HI")</code></pre>
<div class="output-box">
    <span class="output-label">Execution Output (AIMessage)</span>
AIMessage(content='Hello! How can I help you today?', additional_kwargs={'reasoning_content': 'User says "HI". We should respond politely.'}, response_metadata={'token_usage': {'completion_tokens': 29, 'prompt_tokens': 72, 'total_tokens': 101, 'completion_time': 0.030370052, 'model_name': 'openai/gpt-oss-20b', 'model_provider': 'groq'}})
</div>
<p><strong>Deconstruction & Key Mechanics:</strong></p>
<ul>
    <li><code>init_chat_model("groq:openai/gpt-oss-20b")</code>: Instantiates a standardized <code>ChatGroq</code> model wrapper under LangChain's unified factory interface.</li>
    <li><strong>Automatic String Coercion:</strong> Passing the raw string <code>"HI"</code> causes LangChain to automatically wrap the string into a single <code>HumanMessage(content="HI")</code> before transmitting it to the Groq API.</li>
    <li><strong>Reasoning Metadata:</strong> In <code>additional_kwargs['reasoning_content']</code>, we observe the open-weights model's internal thought deliberation (<code>User says "HI". We should respond politely.</code>) generated prior to the user-facing output.</li>
</ul>

<div class="avoid-break">
<h3>Cell 2: Persona Steering via SystemMessage</h3>
<pre><code>from langchain.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage("You are a professional football coach"),
    HumanMessage("Give detailed analysis of Kylian Mbappe Playstyle")
]

response = model.invoke(messages)
response.content</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result (Excerpts)</span>
## Kylian Mbappé – Play-style Analysis  
*(Perspective of a professional football coach – tactical, technical, and developmental insights)*  

### 1. Core Physical & Technical Profile  
| Attribute | Typical Rating (0–10) | Key Observations |
| Pace & Acceleration | 10/10 | Exceptional burst over 5–15 meters; unmatched top speed... |
| Finishing & Ball Striking | 9.0/10 | Lethal across the goalkeeper; curler into far corner... |
...
</div>
<p><strong>Architectural Rationale:</strong></p>
<ul>
    <li><code>SystemMessage</code> instructs the LLM before any user input is processed. It anchors the model's tone, terminology, and evaluation criteria into those of a professional sports coach.</li>
    <li>Notice how the response immediately adopts tactical jargon (e.g., "half-spaces", "low defensive block", "counter-press transition"). Without the <code>SystemMessage</code>, the model would produce a generic biographical summary.</li>
</ul>
</div>

<div class="avoid-break">
<h3>Cell 3: Strict Behavioral Guidelines & Comparative Prompting</h3>
<pre><code>system_msg = SystemMessage(\"\"\"You are an expert in football tactics.
Always provide examples and explain your reasoning.
Be concise but thorough in you explanations.
\"\"\")

human_msg = HumanMessage("who is better in attacking and defence lamine yamal vs kyliam mbappe")

messages = [
    system_msg,
    human_msg
]

response = model.invoke(messages)
print(response.content)</code></pre>
<div class="output-box">
    <span class="output-label">Printed Stream Output</span>
**Short answer:**  
- **Attacking:** Kylian Mbappé is far superior.  
- **Defensive contribution:** Mbappé also edges out Yamal, but Yamal’s defensive stats are limited and come from youth-level play.

## 1. Attacking comparison
| Metric | Mbappé (2023-24) | Yamal (2023-24) |
| Goals / 90 min | 0.95 | 0.28 |
...
</div>
<p><strong>Key Mechanics:</strong> Demonstrates multi-line system prompts enforcing constraints: providing concrete examples, structured tables, and concise reasoning.</p>
</div>

<div class="page-break-before"></div>
<h3>Cell 4: Message Metadata Attributes (Speaker Disambiguation & Tracing)</h3>
<pre><code>human_msg = HumanMessage(
    content="Hello",
    name="alice",   # Optional: Identifies the speaker in multi-user/multi-agent chats
    id="msg_123"    # Optional: Unique identifier for application telemetry/tracing
)</code></pre>
<p><strong>Deep-Dive on Optional Parameters:</strong></p>
<table>
    <tr>
        <th>Attribute</th>
        <th>Type</th>
        <th>Primary Purpose in Production</th>
    </tr>
    <tr>
        <td><code>name</code></td>
        <td><code>str | None</code></td>
        <td>Crucial for multi-party conversations (e.g., Group Chats, Multi-Agent Debates). Allows the model to distinguish between inputs from "alice", "bob", or specialized agent nodes ("researcher", "critic").</td>
    </tr>
    <tr>
        <td><code>id</code></td>
        <td><code>str | None</code></td>
        <td>Used for distributed tracing (LangSmith, OpenTelemetry) and database synchronization. Allows updating, rating, or referencing specific messages in persistent storage.</td>
    </tr>
</table>

<div class="avoid-break">
<h3>Cell 5: Simulating Prior Conversation History</h3>
<pre><code># Manual example AI message to seed conversation context
ai_msg = AIMessage("I would be happy to help you with that question")

system_msg = SystemMessage("You are a professional cook, always give detailed ingredients list, and exact step wise instructions")

human_msg = HumanMessage("tell me how to cook chicken changezi")

messages = [
    system_msg,
    human_msg,
    ai_msg
]

response = model.invoke(messages)
print(response.content)</code></pre>
<div class="output-box">
    <span class="output-label">Printed Output</span>
## Chicken Changzi (Changezi Chicken)  
*A classic, savory-spicy Mughlai-style chicken dish that showcases the deep umami of rich tomato gravy and aromatic spices...*

### 1. Ingredients
| Category | Ingredient | Quantity | Notes |
...
</div>
<p><strong>Pedagogical Insight:</strong> Demonstrates how conversational memory is maintained in stateless HTTP APIs. By passing a list of alternating <code>HumanMessage</code> and <code>AIMessage</code> objects, the application reconstructs the illusion of memory for the LLM.</p>
</div>

<div class="avoid-break">
<h3>Cell 6: The Synthetic Tool Calling Handshake</h3>
<pre><code># 1. Model emits a structured tool call request
ai_message = AIMessage(
    content=[],
    tool_calls=[{
        "name": "get_weather",
        "args": {
            "location": "Delhi"
        },
        "id": "call_123"
    }]
)

# 2. Host Python runtime executes tool and obtains result
weather_result = "Sunny, 32 C"

from langchain.messages import ToolMessage

# 3. Wrap tool execution result linked by ID
tool_message = ToolMessage(
    content=weather_result,
    tool_call_id="call_123"  # Must match the call id exactly!
)

# 4. Continue conversation with full context
messages = [
    HumanMessage("What's the weather in Delhi right now?"),
    ai_message,
    tool_message
]

response = model.invoke(messages)
print(response.content)</code></pre>
<div class="output-box">
    <span class="output-label">Final Synthesized Output</span>
The weather in Delhi right now is sunny with a temperature of 32°C.
</div>
<p><strong>The 4-Step Tool Handshake Protocol:</strong></p>
<ol>
    <li>The user submits a prompt requiring external live data (<code>"What's the weather in Delhi?"</code>).</li>
    <li>The model determines it needs a tool, producing an <code>AIMessage</code> where <code>content</code> is empty or minimal, and <code>tool_calls</code> contains the function name, arguments, and a unique <code>id="call_123"</code>.</li>
    <li>The Python runtime runs the code and returns the observation wrapped in a <code>ToolMessage</code> explicitly referencing <code>tool_call_id="call_123"</code>.</li>
    <li>The entire sequence <code>[HumanMessage, AIMessage, ToolMessage]</code> is passed back to the model, allowing it to synthesize a final natural-language response.</li>
</ol>
</div>

<!-- Section F: End-to-End Diagram -->
<div class="page-break-before"></div>
<h2>F. End-to-End Message Architecture & Handshake Diagram</h2>
<p>The diagram below visualizes the class inheritance hierarchy and the exact 4-turn state handshake executed during tool orchestration:</p>

<div class="diagram-container">
    __SVG_DIAGRAM__
    <div class="diagram-caption">Figure 4.1: LangChain BaseMessage Architecture and Multi-Turn Tool Execution Handshake</div>
</div>

<!-- Section G: Important APIs & Classes Reference -->
<h2>G. Important APIs & Classes Reference</h2>
<table>
    <tr>
        <th>Class / Function</th>
        <th>Import Path</th>
        <th>Key Attributes / Parameters</th>
        <th>Description & Role</th>
    </tr>
    <tr>
        <td><code>BaseMessage</code></td>
        <td><code>langchain_core.messages</code></td>
        <td><code>content</code>, <code>id</code>, <code>name</code>, <code>additional_kwargs</code></td>
        <td>Root polymorphic message abstraction across all LangChain components.</td>
    </tr>
    <tr>
        <td><code>SystemMessage</code></td>
        <td><code>langchain.messages</code></td>
        <td><code>content</code> (instructions / persona)</td>
        <td>Sets system-level prompt guidelines, role behaviors, and constraints.</td>
    </tr>
    <tr>
        <td><code>HumanMessage</code></td>
        <td><code>langchain.messages</code></td>
        <td><code>content</code>, <code>name</code>, <code>id</code></td>
        <td>Represents inputs and queries originating from human users.</td>
    </tr>
    <tr>
        <td><code>AIMessage</code></td>
        <td><code>langchain.messages</code></td>
        <td><code>content</code>, <code>tool_calls</code>, <code>usage_metadata</code></td>
        <td>Represents assistant completions or structured tool call requests.</td>
    </tr>
    <tr>
        <td><code>ToolMessage</code></td>
        <td><code>langchain.messages</code></td>
        <td><code>content</code>, <code>tool_call_id</code>, <code>name</code></td>
        <td>Contains the output produced by a local tool, linked via <code>tool_call_id</code>.</td>
    </tr>
</table>

<!-- Section H: Common Errors, Debugging & Troubleshooting -->
<h2>H. Common Errors, Debugging & Troubleshooting</h2>

<div class="callout callout-error">
    <div class="callout-title">Trap 1: Mismatched tool_call_id in ToolMessage</div>
    <p><strong>Symptom:</strong> API returns <code>400 Bad Request: Invalid tool_call_id</code> or model produces bizarre hallucinations.</p>
    <p><strong>Root Cause:</strong> The model emits a tool call with a generated ID (e.g. <code>id="call_987abc"</code>). If the application returns a <code>ToolMessage</code> with a mismatched ID or hardcoded placeholder, the provider cannot link the observation back to the requesting call.</p>
    <p><strong>Fix:</strong> Always dynamically copy the ID directly from the tool call object: <code>ToolMessage(content=result, tool_call_id=tool_call['id'])</code>.</p>
</div>

<div class="callout callout-warning">
    <div class="callout-title">Trap 2: Passing Raw Strings in a Message List</div>
    <p><strong>Symptom:</strong> <code>ValueError: Expected a BaseMessage object, got 'Tell me a joke'</code>.</p>
    <p><strong>Root Cause:</strong> While <code>model.invoke("raw string")</code> is allowed, passing a list mixing strings and message objects (e.g. <code>[SystemMessage(...), "raw string"]</code>) is invalid.</p>
    <p><strong>Fix:</strong> Ensure all items in a message list are instances of <code>BaseMessage</code>: <code>[SystemMessage(...), HumanMessage(content="...")]</code>.</p>
</div>

<!-- Section I: Practical Example -->
<h2>I. Practical Example: Stateful Chat History Serializer</h2>
<p>In production applications, message histories must be serialized to JSON databases (PostgreSQL, Redis, MongoDB) and restored across web sessions:</p>

<pre><code>from langchain_core.messages import (
    messages_to_dict,
    messages_from_dict,
    SystemMessage,
    HumanMessage,
    AIMessage
)

# 1. Active conversation state in memory
history = [
    SystemMessage(content="You are a helpful coding tutor."),
    HumanMessage(content="What is Python list comprehension?", id="req_001"),
    AIMessage(content="It's a concise way to create lists: [x for x in iterable].", id="res_001")
]

# 2. Serialize to standard JSON for database storage
serialized_json = messages_to_dict(history)

# 3. Deserialize back into strongly-typed LangChain objects upon next user turn
restored_history = messages_from_dict(serialized_json)
assert isinstance(restored_history[0], SystemMessage)
assert restored_history[1].id == "req_001"</code></pre>

<!-- Section J: Key Takeaways -->
<h2>J. Key Takeaways & Conceptual Map</h2>
<ul>
    <li><strong>Messages Replace Strings:</strong> Professional LangChain development operates on sequences of <code>BaseMessage</code> objects, not plain strings.</li>
    <li><strong>SystemMessage Shapes the Persona:</strong> Use system messages to constrain output formats, adopt specialized domains, and establish boundaries.</li>
    <li><strong>Metadata Enables Enterprise Tracing:</strong> Use <code>id</code> for observability and <code>name</code> for speaker disambiguation in multi-agent environments.</li>
    <li><strong>Tool Calling is a Handshake:</strong> An <code>AIMessage</code> requests a tool via <code>tool_calls</code>; the host environment executes the tool and responds with a <code>ToolMessage</code> matching the exact <code>tool_call_id</code>.</li>
</ul>

<!-- Section K: Practice Exercises -->
<div class="page-break-before"></div>
<h2>K. Practice Exercises & Knowledge Checks</h2>

<div class="exercise-box">
    <div class="exercise-question">Question 1 (Conceptual): Why does ToolMessage require a tool_call_id attribute?</div>
    <p>Why can't LangChain just assume the latest tool result matches the latest user question?</p>
    <div class="answer-box">
        <strong>Answer:</strong> Modern LLMs support <em>parallel tool calling</em>, meaning a single model response can emit multiple tool calls simultaneously (e.g., fetching weather for Delhi, Tokyo, and London in one turn). The <code>tool_call_id</code> is the cryptographic foreign key that pairs each observation precisely with its specific request.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 2 (Code Tracing): In Cell 6, why is AIMessage initialized with content=[]?</div>
    <p>Does the model output text when making a tool call?</p>
    <div class="answer-box">
        <strong>Answer:</strong> When an LLM decides to invoke a tool, its generative budget is directed entirely into formulating the structured tool arguments inside <code>tool_calls</code>. It intentionally leaves conversational <code>content</code> empty (or as an empty list) because it must await the tool observation before generating natural-language text.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 3 (Architecture): How does the name attribute on HumanMessage prevent multi-agent confusion?</div>
    <div class="answer-box">
        <strong>Answer:</strong> In multi-agent architectures (or group chat systems), multiple participants write to the same shared message list. Attaching <code>name="researcher"</code> or <code>name="critic"</code> allows the downstream model to understand who said what without corrupting the message text itself.
    </div>
</div>

<!-- Section L: Further Learning -->
<h2>L. Further Learning & Official Documentation</h2>
<ul>
    <li><a href="https://python.langchain.com/docs/concepts/#messages">LangChain Messages Concept Guide</a></li>
    <li><a href="https://console.groq.com/docs/models">Groq Cloud Model Documentation</a></li>
    <li>Next study guide in sequence: <strong>5-structure.pdf</strong> (Structured Outputs & Pydantic Schemas).</li>
</ul>

</body>
</html>
"""
    return (html_template
            .replace("__FNAME__", fname)
            .replace("__TODAY__", today)
            .replace("__CSS_STYLES__", CSS_STYLES)
            .replace("__SVG_DIAGRAM__", svg_diagram))


def build_guide_5(fname, cells, today):
    """Build canonical 12-section educational guide for 5-structure.ipynb."""
    svg_diagram = get_svg_structured_output_pipeline()
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>__FNAME__ - Educational Study Guide</title>
    <style>__CSS_STYLES__</style>
</head>
<body>

<!-- Section A: Cover Page -->
<div class="cover-page">
    <span class="cover-badge">LangChain 1.4+ • Advanced Schema Extraction</span>
    <h1 class="cover-title">Structured Outputs &amp; Schema Extraction</h1>
    <p class="cover-subtitle">Enforcing Type Safety, Validation, and Deterministic Schemas via Pydantic, TypedDict, DataClasses, and Agent response_format</p>
    
    <p style="font-size: 10.5pt; color: #475569; max-width: 580px; margin-top: 15px;">
        An exhaustive architectural guide to deterministic LLM extraction. Explores how LangChain compiles
        Python type schemas into function-calling constraints, extracts flat and nested Pydantic models, leverages
        lightweight TypedDict structures, inspects raw reasoning metadata, and binds structured response formats directly into autonomous agents.
    </p>

    <div class="cover-meta">
        <div class="cover-meta-grid">
            <div class="meta-item"><strong>Target Notebook:</strong> <code>__FNAME__</code></div>
            <div class="meta-item"><strong>Generation Date:</strong> __TODAY__</div>
            <div class="meta-item"><strong>Language &amp; Runtime:</strong> Python 3.14 • Virtualenv (.venv)</div>
            <div class="meta-item"><strong>Core Framework:</strong> LangChain 1.4.7 • Pydantic v2 • Groq</div>
        </div>
    </div>
</div>

<!-- Section B: Learning Objectives -->
<h2>B. Learning Objectives</h2>
<p>After studying this notebook and study guide, you will master:</p>
<ul>
    <li><strong>The Deterministic Schema Guarantee:</strong> Understand why enterprise production applications demand validated data schemas over unstructured generative text.</li>
    <li><strong>Pydantic BaseModel Compilation:</strong> Construct robust Pydantic schemas with <code>Field(description=...)</code> and enforce data types across primitives and nested models.</li>
    <li><strong>Dual Payload Extraction with include_raw:</strong> Capture raw generation metadata (reasoning traces, token usage, tool call envelopes) alongside validated domain objects.</li>
    <li><strong>Hierarchical &amp; Nested Schemas:</strong> Design complex multi-level data models containing lists of sub-models and nullable optional attributes (<code>budget: float | None</code>).</li>
    <li><strong>Lightweight Schemas with TypedDict:</strong> Leverage native Python typing (<code>TypedDict</code> and <code>Annotated</code>) when third-party Pydantic classes are undesirable.</li>
    <li><strong>Agentic Extraction via response_format:</strong> Integrate structured extraction directly into LangChain's <code>create_agent</code> for autonomous extraction loops.</li>
</ul>

<!-- Section C: Prerequisites & Setup -->
<h2>C. Prerequisites &amp; Setup</h2>
<div class="callout callout-note">
    <div class="callout-title">Environment Specification</div>
    This notebook runs against the high-throughput <strong>Groq LPU Inference Cloud</strong> executing the <code>openai/gpt-oss-20b</code> open-weights reasoning model.
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
        <td>Modern runtime supporting advanced type hinting (<code>float | None</code>) and fast native execution.</td>
    </tr>
    <tr>
        <td>Virtual Environment</td>
        <td><code>.venv</code> (managed via <code>uv</code>)</td>
        <td>Isolates dependencies defined in <code>pyproject.toml</code>.</td>
    </tr>
    <tr>
        <td>Validation Libraries</td>
        <td><code>pydantic>=2.0</code>, <code>typing_extensions</code></td>
        <td>Provides runtime data validation, serialization, and type introspection.</td>
    </tr>
    <tr>
        <td>Core Dependencies</td>
        <td><code>langchain>=1.4.7</code>, <code>langchain-groq</code>, <code>python-dotenv</code></td>
        <td>Provides model initialization and <code>with_structured_output</code> compiler layer.</td>
    </tr>
</table>
<div class="callout callout-warning">
    <div class="callout-title">Security Best Practice</div>
    Never commit real API keys to version control. Always verify that <code>.env</code> is tracked in <code>.gitignore</code> and use <code>.env.example</code> for team onboarding.
</div>

<!-- Section D: Topic Overview -->
<div class="page-break-before"></div>
<h2>D. Topic Overview: The Shift from Generative Text to Deterministic Schemas</h2>
<p>
    Standard LLM completions return free-form text: strings of paragraphs, markdown bullet points, or informal prose. While pleasant for human reading, software applications, microservices, and databases cannot reliably ingest free-form text without fragile, regex-heavy post-processing.
</p>
<p>
    LangChain solves this through the universal <code>with_structured_output(schema)</code> abstraction. Rather than asking the model to "please output JSON" via system prompt formatting instructions, LangChain leverages modern model <strong>tool / function calling mechanisms</strong>:
</p>
<ol>
    <li><strong>Schema Compilation:</strong> LangChain inspects the Python schema (Pydantic model or TypedDict) and compiles it into an exact JSON Schema definition.</li>
    <li><strong>Tool Binding &amp; Enforcement:</strong> The JSON Schema is transmitted to the provider API as a mandatory tool call. The provider forces the model to emit arguments matching the schema.</li>
    <li><strong>Validation &amp; Coercion:</strong> Upon receiving the JSON payload, LangChain feeds it into Pydantic, validating types, enforcing constraints, and returning an instantiated Python object directly to your code.</li>
</ol>

<!-- Section E: Detailed Notebook Walkthrough -->
<h2>E. Detailed Notebook Walkthrough &amp; Cell Dissection</h2>

<h3>Cell 0: Markdown Section Header</h3>
<pre><code>### Structure</code></pre>
<p><strong>Analysis:</strong> Establishes the study module exploring structured data extraction.</p>

<h3>Cell 1: Model Initialization &amp; Provider Profile Inspection</h3>
<pre><code>import os
from langchain.chat_models import init_chat_model

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

model = init_chat_model("groq:openai/gpt-oss-20b")

model</code></pre>
<div class="output-box">
    <span class="output-label">Execution Output (Model Profile)</span>
ChatGroq(metadata={'lc_versions': {'langchain-core': '1.7.0', 'langchain': '1.4.7'}, profile={'name': 'GPT OSS 20B', 'release_date': '2025-08-05', 'open_weights': True, 'max_input_tokens': 131072, 'max_output_tokens': 65536, 'text_inputs': True, 'image_inputs': False, 'tool_calling': True, 'structured_output': True})
</div>
<p><strong>Key Mechanics:</strong></p>
<ul>
    <li>The model profile confirms native support for <code>'tool_calling': True</code> and <code>'structured_output': True</code>, enabling reliable schema enforcement without fallback prompt hacks.</li>
    <li><code>max_input_tokens: 131072</code> provides substantial headroom for ingesting large documents while extracting structured records.</li>
</ul>

<h3>Cell 2: Markdown Section Header</h3>
<pre><code>### Pyantic</code></pre>
<p><strong>Analysis:</strong> Focuses on Pydantic v2 schema definitions.</p>

<div class="avoid-break">
<h3>Cell 3: Flat Pydantic Model Definition &amp; Structured Invocation</h3>
<pre><code>from pydantic import BaseModel, Field

class Movie(BaseModel):
    title: str = Field(description="title of the movie")
    year: int = Field(description="year the move was released")
    director: str = Field(description="director of the movie")
    rating: float = Field(description="movie rating out of 10")

model_with_structure = model.with_structured_output(Movie)

response = model_with_structure.invoke("Tell me about movie avengers endgame")

response</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result (Validated Object)</span>
Movie(title='Avengers: Endgame', year=2019, director='Anthony Russo', rating=8.4)
</div>
<p><strong>Detailed Analysis:</strong></p>
<ul>
    <li><code>Field(description="...")</code>: Crucial pedagogical element. LangChain exports these descriptions directly into the JSON Schema. The LLM reads these descriptions to determine what data belongs in each property.</li>
    <li><code>response</code> is <em>not</em> a string or dictionary; it is a live <code>Movie</code> Pydantic class instance. Developers get complete IDE autocomplete: <code>response.title</code>, <code>response.year</code>, <code>response.rating</code>.</li>
</ul>
</div>

<div class="page-break-before"></div>
<h3>Cell 4: Dual Output Inspection via include_raw=True</h3>
<pre><code># Pydantic can also include raw message along with structure
model_with_structure = model.with_structured_output(Movie, include_raw=True)

response = model_with_structure.invoke("Tell me about movie avengers endgame")

response</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result (Dictionary with Raw and Parsed)</span>
{'raw': AIMessage(content='', additional_kwargs={'reasoning_content': 'We need to output a response. The user wants information about the movie "Avengers: Endgame". We can use the function. The function requires director, rating, title, year. We\\'ll call the function.', 'tool_calls': [{'id': 'fc_cfe...', 'function': {'arguments': '{"director":"Anthony Russo","rating":8.4,"title":"Avengers: Endgame","year":2019}', 'name': 'Movie'}, 'type': 'function'}]}, response_metadata={'token_usage': {'completion_tokens': 98, 'prompt_tokens': 165, 'total_tokens': 263}}),
 'parsed': Movie(title='Avengers: Endgame', year=2019, director='Anthony Russo', rating=8.4),
 'parsing_error': None}
</div>
<p><strong>Architectural Rationale:</strong></p>
<ul>
    <li>Setting <code>include_raw=True</code> returns a 3-key dictionary: <code>raw</code>, <code>parsed</code>, and <code>parsing_error</code>.</li>
    <li><strong>Observability &amp; Auditing:</strong> The <code>raw</code> key preserves the underlying <code>AIMessage</code>, complete with token usage and internal reasoning. If validation fails, <code>parsed</code> is <code>None</code> and <code>parsing_error</code> captures the exact Pydantic <code>ValidationError</code> for graceful recovery.</li>
</ul>

<div class="avoid-break">
<h3>Cell 5: Nested Pydantic Hierarchies &amp; Optional Fields</h3>
<pre><code># Nested pydantic structure
class actor(BaseModel):
    name: str
    role: str

class movie(BaseModel):
    title: str
    year: int
    cast: list[actor]
    genres: list[str]
    budget: float | None = Field(None, description="Budget In Millions USD")

model_with_structure = model.with_structured_output(movie)

response = model_with_structure.invoke("Tell me about movie avengers endgame")

response</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result (Nested Object)</span>
movie(title='Avengers: Endgame',
      year=2019,
      cast=[actor(name='Robert Downey Jr.', role='Tony Stark / Iron Man'),
            actor(name='Chris Evans', role='Steve Rogers / Captain America'),
            actor(name='Mark Ruffalo', role='Bruce Banner / Hulk'),
            actor(name='Chris Hemsworth', role='Thor'),
            actor(name='Scarlett Johansson', role='Natasha Romanoff / Black Widow')],
      genres=['Action', 'Adventure', 'Drama', 'Sci-Fi'],
      budget=356.0)
</div>
<p><strong>Advanced Modeling Features:</strong></p>
<ul>
    <li><code>cast: list[actor]</code>: The model automatically formats an array of JSON objects matching the <code>actor</code> schema.</li>
    <li><code>budget: float | None = Field(None, ...)</code>: Declares an optional attribute with a default of <code>None</code>. If the model does not know the budget, it will not fail validation.</li>
</ul>
</div>

<h3>Cell 6: Markdown Section Header</h3>
<pre><code>### TypedDict</code></pre>
<p><strong>Analysis:</strong> Transitioning to lightweight dictionary-based typing.</p>

<div class="avoid-break">
<h3>Cell 7: Flat TypedDict Schema Definition</h3>
<pre><code>from typing_extensions import TypedDict, Annotated

class movie(TypedDict):
    \"\"\"a movie with details\"\"\"
    title: Annotated[str, ..., "title of the movie"]
    year: Annotated[int, ..., "year the move was released"]
    director: Annotated[str, ..., "director of the movie"]
    rating: Annotated[float, ..., "movie rating out of 10"]

model_with_structure = model.with_structured_output(movie)

response = model_with_structure.invoke("Tell me about avengers endgame")

response</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result (Pure Python Dictionary)</span>
{'director': 'Anthony Russo and Joe Russo',
 'rating': 8.4,
 'title': 'Avengers: Endgame',
 'year': 2019}
</div>
<p><strong>Key Mechanics:</strong> <code>Annotated[type, ..., "description"]</code> injects field descriptions into the JSON Schema without requiring Pydantic. The result is a standard Python <code>dict</code>.</p>
</div>

<div class="avoid-break">
<h3>Cell 8: Nested TypedDict Schema</h3>
<pre><code># Nested TypedDict structure
class actor(TypedDict):
    name: str
    role: str

class movie(TypedDict):
    title: str
    year: int
    cast: list[actor]
    genres: list[str]
    budget: float | None = Field(None, description="Budget In Millions USD")

model_with_structure = model.with_structured_output(movie)

response = model_with_structure.invoke("Tell me about movie avengers endgame")

response</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result (Nested Dictionary)</span>
{'budget': 356000000,
 'cast': [{'name': 'Robert Downey Jr.', 'role': 'Tony Stark / Iron Man'},
          {'name': 'Chris Evans', 'role': 'Steve Rogers / Captain America'},
          {'name': 'Mark Ruffalo', 'role': 'Bruce Banner / Hulk'},
          {'name': 'Chris Hemsworth', 'role': 'Thor'},
          {'name': 'Scarlett Johansson', 'role': 'Natasha Romanoff / Black Widow'}],
 'genres': ['Action', 'Adventure', 'Sci-Fi'],
 'title': 'Avengers: Endgame',
 'year': 2019}
</div>
<p><strong>Observation:</strong> Returns a clean nested dictionary structure. Notice that while Pydantic returned <code>356.0</code> (millions), here the model emitted <code>356000000</code> integer.</p>
</div>

<h3>Cell 9: Markdown Section Header</h3>
<pre><code>### DataClasses</code></pre>
<p><strong>Analysis:</strong> Exploring Python dataclasses integrated into LangChain agents.</p>

<div class="avoid-break">
<h3>Cell 10: Agent Structured Output via response_format</h3>
<pre><code>from dataclasses import dataclass
from langchain.agents import create_agent

@dataclass
class ContactInfo(BaseModel):
    \"\"\"Contact information for a person.\"\"\"
    name: str = Field(description="The name of the person")
    email: str = Field(description="The email address of the person")
    phone: str = Field(description="The phone number of the person")

model = init_chat_model("groq:openai/gpt-oss-20b")

agent = create_agent(
    model=model,
    response_format=ContactInfo  # Auto-selects ProviderStrategy
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"
    }]
})

result</code></pre>
<div class="output-box">
    <span class="output-label">Agent State Output (Excerpts)</span>
{'messages': [HumanMessage(content='Extract contact info from: John Doe, john@example.com, (555) 123-4567'),
              AIMessage(content='{"name":"John Doe","email":"john@example.com","phone":"(555) 123-4567"}', ...)],
 'structured_response': ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')}
</div>
<p><strong>Architectural Breakthrough:</strong> In modern LangChain agents, passing <code>response_format=ContactInfo</code> automatically instructs the agent's <code>CompiledStateGraph</code> to extract and validate the final answer into a strongly-typed schema.</p>
</div>

<div class="avoid-break">
<h3>Cell 11: Accessing the Validated Agent Response</h3>
<pre><code>result["structured_response"]</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result</span>
ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
</div>
<p><strong>Explanation:</strong> The application extracts the typed entity directly via <code>result["structured_response"]</code> without needing to parse the raw text inside <code>result["messages"]</code>.</p>
</div>

<!-- Section F: End-to-End Execution Flow Diagram -->
<div class="page-break-before"></div>
<h2>F. End-to-End Structured Output Pipeline Diagram</h2>
<p>The diagram below traces the end-to-end lifecycle of schema compilation, model function-calling constraints, and validation:</p>

<div class="diagram-container">
    __SVG_DIAGRAM__
    <div class="diagram-caption">Figure 5.1: LangChain Structured Output Compilation and Validation Pipeline</div>
</div>

<!-- Section G: Important APIs & Classes Reference -->
<h2>G. Important APIs &amp; Classes Reference</h2>
<table>
    <tr>
        <th>API / Function</th>
        <th>Module / Class</th>
        <th>Parameters &amp; Flags</th>
        <th>Description &amp; Key Role</th>
    </tr>
    <tr>
        <td><code>with_structured_output</code></td>
        <td><code>BaseChatModel</code></td>
        <td><code>schema</code>, <code>include_raw=False</code>, <code>method="function_calling"</code></td>
        <td>Compiles a schema into a model-enforced output wrapper returning validated objects.</td>
    </tr>
    <tr>
        <td><code>BaseModel</code></td>
        <td><code>pydantic</code></td>
        <td>Class inheritance</td>
        <td>Primary schema base class providing type enforcement and automated JSON serialization.</td>
    </tr>
    <tr>
        <td><code>Field</code></td>
        <td><code>pydantic</code></td>
        <td><code>description</code>, <code>default</code>, <code>ge</code>, <code>le</code></td>
        <td>Attaches semantic field documentation passed into the LLM's function definition.</td>
    </tr>
    <tr>
        <td><code>TypedDict</code></td>
        <td><code>typing_extensions</code></td>
        <td>Dictionary typing</td>
        <td>Lightweight schema alternative returning native Python dictionaries.</td>
    </tr>
    <tr>
        <td><code>Annotated</code></td>
        <td><code>typing_extensions</code></td>
        <td><code>Annotated[type, ..., description]</code></td>
        <td>Injects documentation metadata into TypedDict fields for model schema generation.</td>
    </tr>
    <tr>
        <td><code>response_format</code></td>
        <td><code>langchain.agents.create_agent</code></td>
        <td><code>schema=Class</code></td>
        <td>Instructs an autonomous agent graph to produce a validated <code>structured_response</code>.</td>
    </tr>
</table>

<!-- Section H: Common Errors, Debugging & Troubleshooting -->
<h2>H. Common Errors, Debugging &amp; Troubleshooting</h2>

<div class="callout callout-error">
    <div class="callout-title">Trap 1: Missing Field Descriptions Lead to Hallucinated Data</div>
    <p><strong>Symptom:</strong> The model places irrelevant data into fields or guesses incorrect formats.</p>
    <p><strong>Root Cause:</strong> If a model has <code>budget: float</code> without a description, the LLM does not know if the unit is Dollars, Euros, Millions, or Exact Cents. In Cell 5, <code>Field(description="Budget In Millions USD")</code> ensured <code>356.0</code> rather than ambiguous integer units.</p>
    <p><strong>Fix:</strong> Always provide explicit descriptions for every field in Pydantic or TypedDict.</p>
</div>

<div class="callout callout-warning">
    <div class="callout-title">Trap 2: Strict Type Validation Rejections</div>
    <p><strong>Symptom:</strong> <code>pydantic_core._pydantic_core.ValidationError: Input should be a valid integer</code>.</p>
    <p><strong>Root Cause:</strong> The model emits <code>"year": "2019 (May)"</code> as a string when an <code>int</code> was strictly required.</p>
    <p><strong>Fix:</strong> Use <code>include_raw=True</code> to inspect the failure, or use flexible Pydantic field validators / string sanitizers before coercion.</p>
</div>

<!-- Section I: Practical Example -->
<h2>I. Practical Example: Enterprise Extractor with Validation Fallback</h2>
<pre><code>from pydantic import BaseModel, Field, ValidationError

class UserProfile(BaseModel):
    full_name: str = Field(description="Full personal name")
    age: int = Field(description="Age in years")
    interests: list[str] = Field(description="List of primary hobbies or interests")

extractor = model.with_structured_output(UserProfile, include_raw=True)

raw_text = "Hi, I am Sarah Jenkins, twenty-eight years old, and I love hiking and photography."

result = extractor.invoke(raw_text)

if result['parsed'] is not None:
    profile: UserProfile = result['parsed']
    print(f"Extracted: {profile.full_name}, Age: {profile.age}, Interests: {profile.interests}")
else:
    print(f"Validation Failed: {result['parsing_error']}")
    print(f"Raw Model Payload: {result['raw'].additional_kwargs}")</code></pre>

<!-- Section J: Key Takeaways -->
<h2>J. Key Takeaways &amp; Conceptual Map</h2>
<ul>
    <li><strong>Structure Replaces Regex:</strong> <code>with_structured_output</code> provides validated Python objects directly from generative models.</li>
    <li><strong>Descriptions Are Functional Prompts:</strong> Field descriptions are not comments; they are actively compiled into the LLM's function schema.</li>
    <li><strong>include_raw is Essential for Auditing:</strong> Always use <code>include_raw=True</code> in production to retain token usage, reasoning traces, and error context.</li>
    <li><strong>Agents Support response_format:</strong> In modern LangChain 1.4+, agents output structured records alongside full multi-turn conversational traces.</li>
</ul>

<!-- Section K: Practice Exercises -->
<div class="page-break-before"></div>
<h2>K. Practice Exercises &amp; Knowledge Checks</h2>

<div class="exercise-box">
    <div class="exercise-question">Question 1 (Conceptual): What is the core difference between Pydantic and TypedDict when used with with_structured_output?</div>
    <div class="answer-box">
        <strong>Answer:</strong> Pydantic validates inputs and returns a strongly-typed class instance with methods and attribute access (<code>obj.title</code>). <code>TypedDict</code> performs compile-time type-hinting and returns a standard Python dictionary (<code>obj['title']</code>).
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 2 (Code Tracing): What does response['raw'] contain when include_raw=True is passed?</div>
    <div class="answer-box">
        <strong>Answer:</strong> It contains the underlying <code>AIMessage</code> instance emitted by the model, including <code>content</code>, <code>tool_calls</code>, <code>response_metadata</code> (token usage, execution time), and <code>additional_kwargs['reasoning_content']</code>.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 3 (Implementation): How do you define an optional field in Pydantic v2 with a default of None?</div>
    <div class="answer-box">
        <strong>Answer:</strong> <code>field_name: type | None = Field(None, description="...")</code>. Specifying <code>None</code> as the default value allows Pydantic to instantiate the model even if the LLM omits the key.
    </div>
</div>

<!-- Section L: Further Learning -->
<h2>L. Further Learning &amp; Official Documentation</h2>
<ul>
    <li><a href="https://python.langchain.com/docs/how_to/structured_output/">LangChain Structured Outputs Guide</a></li>
    <li><a href="https://docs.pydantic.dev/latest/">Pydantic v2 Official Documentation</a></li>
    <li>Previous study guide in sequence: <strong>4-messages.pdf</strong> (Core Message Architecture).</li>
</ul>

</body>
</html>
"""
    return (html_template
            .replace("__FNAME__", fname)
            .replace("__TODAY__", today)
            .replace("__CSS_STYLES__", CSS_STYLES)
            .replace("__SVG_DIAGRAM__", svg_diagram))


def build_guide_6(fname, cells, today):
    """Build canonical 12-section educational guide for 6-middleware.ipynb."""
    svg1 = get_svg_middleware_interceptor_architecture()
    svg2 = get_svg_summarization_middleware_dataflow()
    svg3 = get_svg_hitl_middleware_dataflow()

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>__FNAME__ - Educational Study Guide</title>
    <style>__CSS_STYLES__</style>
</head>
<body>

<!-- Section A: Cover Page -->
<div class="cover-page">
    <span class="cover-badge">LangChain 1.4+ • Agentic Lifecycle &amp; Governance</span>
    <h1 class="cover-title">Agent Middleware &amp; Execution Governance</h1>
    <p class="cover-subtitle">Mastering SummarizationMiddleware (Message &amp; Token Triggers), HumanInTheLoopMiddleware (Approve, Edit, Reject), and Checkpointed Resilience</p>
    
    <p style="font-size: 10.5pt; color: #475569; max-width: 580px; margin-top: 15px;">
        An authoritative technical deep dive into agent lifecycle interception and governance. Deconstructs
        how enterprise AI agents bound context consumption using automated sliding-window summarizers, halt
        high-stakes tool execution via Human-In-The-Loop approval gates, and maintain persistent state checkpoints.
    </p>

    <div class="cover-meta">
        <div class="cover-meta-grid">
            <div class="meta-item"><strong>Target Notebook:</strong> <code>__FNAME__</code></div>
            <div class="meta-item"><strong>Generation Date:</strong> __TODAY__</div>
            <div class="meta-item"><strong>Language &amp; Runtime:</strong> Python 3.14 • Virtualenv (.venv)</div>
            <div class="meta-item"><strong>Core Framework:</strong> LangChain 1.4.7 • LangGraph 0.3+ • Groq</div>
        </div>
    </div>
</div>

<!-- Section B: Learning Objectives -->
<h2>B. Learning Objectives</h2>
<p>After studying this notebook and study guide, you will master:</p>
<ul>
    <li><strong>The Agent Interceptor Architecture:</strong> Understand how LangChain 1.4 wraps compiled state graphs with middleware to inject pre-model, pre-tool, and post-execution hooks without altering business logic.</li>
    <li><strong>Checkpointer &amp; Thread-State Binding:</strong> Configure <code>InMemorySaver</code> and understand why persistent session state via <code>thread_id</code> is mandatory for pausing and resuming agents.</li>
    <li><strong>Message-Count Summarization:</strong> Configure <code>SummarizationMiddleware(trigger=("messages", N), keep=("messages", K))</code> to automatically compact long conversation histories while preserving the latest turns.</li>
    <li><strong>Token-Budget Summarization:</strong> Enforce strict token consumption ceilings (<code>trigger=("tokens", 550), keep=("tokens", 200)</code>) to prevent context exhaustion, rate limits, and latency spikes across multi-turn tool loops.</li>
    <li><strong>Human-In-The-Loop Governance:</strong> Intercept dangerous or sensitive tool invocations (such as sending emails or modifying databases) before execution using <code>HumanInTheLoopMiddleware</code> and <code>interrupt_on</code>.</li>
    <li><strong>The 3-Way Human Review Protocol:</strong> Master the <code>langgraph.types.Command(resume=...)</code> protocol to dynamically <strong>Approve</strong>, <strong>Reject</strong>, or <strong>Edit</strong> tool parameters before dispatching actions.</li>
</ul>

<!-- Section C: Prerequisites & Setup -->
<h2>C. Prerequisites &amp; Setup</h2>
<div class="callout callout-note">
    <div class="callout-title">Environment Specification</div>
    This notebook runs against the high-throughput <strong>Groq LPU Inference Cloud</strong> executing the <code>openai/gpt-oss-20b</code> reasoning model (131,072 input context window, native tool-calling and reasoning traces enabled).
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
        <td>Modern runtime supporting advanced type hinting, dictionary unions, and high-performance execution.</td>
    </tr>
    <tr>
        <td>Virtual Environment</td>
        <td><code>.venv</code> (managed via <code>uv</code>)</td>
        <td>Strictly isolates dependencies defined in <code>pyproject.toml</code>.</td>
    </tr>
    <tr>
        <td>State Checkpointer</td>
        <td><code>langgraph.checkpoint.memory.InMemorySaver</code></td>
        <td>Thread-isolated in-memory storage required to suspend and resume graphs during human reviews.</td>
    </tr>
    <tr>
        <td>Core Dependencies</td>
        <td><code>langchain>=1.4.7</code>, <code>langchain-groq</code>, <code>langgraph</code>, <code>python-dotenv</code></td>
        <td>Supplies universal agent constructors, middleware abstractions, and Groq inference drivers.</td>
    </tr>
</table>
<div class="callout callout-warning">
    <div class="callout-title">Security &amp; Safety Rule</div>
    Never allow autonomous models unsupervised access to external side-effecting APIs (e.g., payment gateways, email dispatches, file deletion). In production, sensitive functions must always be guarded by <code>HumanInTheLoopMiddleware</code>.
</div>

<!-- Section D: Topic Overview -->
<div class="page-break-before"></div>
<h2>D. Topic Overview: The Architecture of Agent Middleware &amp; Governance</h2>
<p>
    In raw LLM pipelines, autonomous agents loop without friction: the model decides on a tool, the runtime executes it, and the observation is immediately fed back into the context. While powerful, this unconstrained autonomy introduces two major enterprise vulnerabilities:
</p>
<ol>
    <li><strong>Context Window Blowout &amp; Cost Explosion:</strong> Long-running conversational agents or multi-step researchers rapidly accumulate messages and tool outputs. Without proactive memory pruning, token counts grow linearly, quickly triggering provider rate limits, ballooning API costs, and causing latency degradation.</li>
    <li><strong>Uncontrolled Side Effects &amp; Hallucinated Actions:</strong> If an autonomous agent decides to execute a destructive or public action (e.g., emailing a customer, deleting database records, executing financial trades), standard autonomous loops dispatch the call immediately without human oversight.</li>
</ol>
<p>
    LangChain 1.4 addresses these challenges through the <strong>Agent Middleware System</strong> built atop LangGraph's <code>CompiledStateGraph</code>. Middleware acts as an interceptor pipeline surrounding the model decision node and tool execution nodes:
</p>

<!-- Embedded Master Architecture Diagram -->
<div style="text-align: center; margin: 15px 0;">
    __SVG_DIAGRAM_1__
    <p style="font-size: 8.5pt; color: #64748b; margin-top: 5px;"><em>Figure 6.1: LangChain 1.4 Agent Lifecycle Interceptor Pipeline with Checkpointer, Summarization, and HITL Gates.</em></p>
</div>

<p>
    As illustrated above, every incoming message is assigned a <code>thread_id</code> managed by a <code>checkpointer</code>. Before the model is called, <strong>SummarizationMiddleware</strong> checks memory thresholds and compacts history if required. When the model emits a tool call, <strong>HumanInTheLoopMiddleware</strong> checks whether the targeted tool requires approval. If intercepted, the entire state machine suspends execution, yields an <code>__interrupt__</code> payload to the client, and waits for a signed human <code>Command</code> before proceeding.
</p>

<!-- Section E: Detailed Notebook Walkthrough -->
<div class="page-break-before"></div>
<h2>E. Detailed Notebook Walkthrough &amp; Cell Dissection</h2>

<h3>Cell 0: Markdown Section Header</h3>
<pre><code>### Middleware</code></pre>
<p><strong>Analysis:</strong> Establishes the study module exploring agent middleware interceptors.</p>

<h3>Cell 1: Environment &amp; Secret Initialization</h3>
<pre><code>import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")</code></pre>
<p><strong>Deconstruction:</strong> Loads local environment variables from <code>.env</code> and configures the <code>GROQ_API_KEY</code> credential in the process environment. This ensures secure API communication without hardcoding keys.</p>

<h3>Cell 2: Markdown Section Header</h3>
<pre><code>### Summrization Middleware</code></pre>
<p><strong>Analysis:</strong> Initiates the analysis of automated context compression middleware.</p>

<h3>Cell 3: Imports &amp; Model Profile Inspection</h3>
<pre><code>from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

model = init_chat_model("groq:openai/gpt-oss-20b")
model</code></pre>
<div class="output-box">
    <span class="output-label">Execution Output (Model Profile)</span>
ChatGroq(metadata={'lc_versions': {'langchain-core': '1.7.0', 'langchain': '1.4.7'}}, profile={'name': 'GPT OSS 20B', 'release_date': '2025-08-05', 'open_weights': True, 'max_input_tokens': 131072, 'max_output_tokens': 65536, 'text_inputs': True, 'reasoning_output': True, 'tool_calling': True, 'structured_output': True}, ...)
</div>
<p><strong>Architectural Rationale:</strong></p>
<ul>
    <li><code>init_chat_model("groq:openai/gpt-oss-20b")</code>: Initializes Groq's high-throughput open-weights reasoning model.</li>
    <li><code>InMemorySaver()</code>: An essential component. Middleware that pauses execution or manages persistent thread state requires a state saver. <code>InMemorySaver</code> stores thread checkpoints in RAM.</li>
</ul>

<div class="avoid-break">
<h3>Cell 4: Message-Length Based Summarization</h3>
<pre><code># Message Length Based Summarization
agent = create_agent(
    model=model,
    checkpointer=InMemorySaver(),
    middleware=[
        SummarizationMiddleware(
            model=model,
            trigger=("messages", 10), # summarize after 10 messages
            keep=("messages", 4)
        )
    ]
)

config = {"configurable": {"thread_id": "test-1"}}

questions = [
    "What is 2+2?",
    "What is 10*5?",
    "What is 100/4?",
    "What is 15-7?",
    "What is 3*3?",
    "What is 4*4?",
]

for question in questions:
    response = agent.invoke({"messages": [HumanMessage(content=question)]}, config)
    print(f"Messages: {len(response['messages'])}")</code></pre>
<div class="output-box">
    <span class="output-label">Execution Output (Message Count Tracing)</span>
Messages: 2
Messages: 4
Messages: 6
Messages: 8
Messages: 10
Messages: 6
</div>
<p><strong>Detailed Analysis &amp; Compaction Mechanics:</strong></p>
<ol>
    <li><strong>Threshold Accumulation (Turns 1 to 5):</strong> Each user query produces 1 <code>HumanMessage</code> and 1 <code>AIMessage</code>. The conversation grows steadily: 2 $\rightarrow$ 4 $\rightarrow$ 6 $\rightarrow$ 8 $\rightarrow$ 10 messages.</li>
    <li><strong>Compaction Trigger Firing (Turn 6):</strong> On the 6th question (<code>"What is 4*4?"</code>), the middleware detects that message count has reached the trigger threshold of <code>10</code>.</li>
    <li><strong>Structured Background Summarization:</strong> The middleware invokes the background summarizer model with a specialized prompt to extract:
        <ul>
            <li><code>## SESSION INTENT</code>: Solves arithmetic queries.</li>
            <li><code>## SUMMARY</code>: Compact bullet points of questions 1 through 4 and their results.</li>
            <li><code>## ARTIFACTS</code>: Any code or data created.</li>
            <li><code>## NEXT STEPS</code>: Current pending question to answer.</li>
        </ul>
    </li>
    <li><strong>State Pruning:</strong> The oldest 6 messages are replaced by a single synthetic <code>HumanMessage</code> tagged with <code>additional_kwargs={'lc_source': 'summarization'}</code>.</li>
    <li><strong>Retention of Recent History:</strong> Because <code>keep=("messages", 4)</code> was specified, the 4 most recent messages (Turn 4 &amp; Turn 5 Q&amp;A) are preserved intact alongside the summary. Adding the new Turn 6 query and response yields: $1\text{ (Summary)} + 4\text{ (Retained)} + 1\text{ (New Turn AI)} = 6\text{ messages}$!</li>
</ol>
</div>

<div class="page-break-before"></div>
<h3>Cell 5: Token-Size Based Summarization</h3>
<pre><code># Token Size Summarization
@tool
def search_hostels(city: str) -> str:
    \"\"\"Search hotels - returns long response to use more tokens.\"\"\"
    return f\"\"\"Hotels in {city}:
    1. Grand Hotel - 5 star, $350/night, spa, pool, gym
    2. City Inn - 4 star, $180/night, business center
    3. Budget Stay - 3 star, $75/night, free wifi\"\"\"

agent = create_agent(
    model=model,
    tools=[search_hostels],
    checkpointer=InMemorySaver(),
    middleware=[
        SummarizationMiddleware(
            model=model,
            trigger=("tokens", 550),
            keep=("tokens", 200)
        )
    ]
)

config = {"configurable": {"thread_id": "test-1"}}

def count_tokens(messages):
    total_chars = sum(len(str(message.content)) for message in messages)
    return total_chars // 4

cities = ["Paris", "London", "Tokyo", "New York", "Dubai", "Singapore"]

for city in cities:
    response = agent.invoke({"messages": [HumanMessage(content=f"Find hotels in {city}")]}, config=config)
    tokens = count_tokens(response["messages"])
    print(f"{city}: ~{tokens} tokens, {len(response['messages'])} messages")</code></pre>
<div class="output-box">
    <span class="output-label">Execution Output (Token Stabilization Tracing)</span>
Paris: ~210 tokens, 4 messages
London: ~409 tokens, 8 messages
Tokyo: ~459 tokens, 5 messages
New York: ~499 tokens, 5 messages
Dubai: ~497 tokens, 5 messages
Singapore: ~512 tokens, 5 messages
</div>
<p><strong>Deconstruction &amp; Token Budget Mechanics:</strong></p>
<ul>
    <li><code>count_tokens(messages)</code>: Implements the industry heuristic of $\\sim 4\text{ characters} \approx 1\text{ token}$.</li>
    <li><strong>Turn 1 &amp; Turn 2:</strong> Paris generates 4 messages (User, AI tool_call, Tool result, AI formatted table) totaling 210 tokens. London appends another 4 messages, raising the token footprint to 409 tokens (8 messages).</li>
    <li><strong>Turn 3 (Tokyo - Trigger Met):</strong> Ingesting Tokyo would push the context past the 550 token ceiling. The middleware intercepts, invokes the summarizer, collapses Paris and London into a structured summary markdown, retains ~200 tokens of recent context, and returns a compacted 5-message state with only 459 tokens!</li>
    <li><strong>Continuous Token Bounding:</strong> Across New York, Dubai, and Singapore, the token count stabilizes in a tight band around ~497–512 tokens. The context never runs away linearly, ensuring predictable latency and zero token overflow errors.</li>
</ul>

<h3>Cell 6: Markdown Section Header</h3>
<pre><code>### Human In The Loop Middleware</code></pre>
<p><strong>Analysis:</strong> Introduces human approval gates and interactive execution control.</p>

<div class="avoid-break">
<h3>Cell 7: Intercepting High-Stakes Tools via interrupt_on</h3>
<pre><code>from langchain.agents.middleware import HumanInTheLoopMiddleware

def read_email_tool(email: str) -> str:
    \"\"\"Mock Function to read an email by its id\"\"\"
    return f"Email Content for ID: {email}"

def send_email_tool(recipient: str, subject: str, body: str) -> str:
    \"\"\"Mock function to send an email\"\"\"
    return f"Email sent to {recipient} with subject: {subject}"

agent = create_agent(
    model=model,
    tools=[read_email_tool, send_email_tool],
    checkpointer=InMemorySaver(),
    middleware=[HumanInTheLoopMiddleware(
        interrupt_on={
            "send_email_tool": {
                "allowed_decisions": ["approve", "edit", "reject"]
            },
            "read_email_tool": False,
        }
    )]
)

config = {"configurable": {"thread_id": "test-approve"}}

email = "varad0404@gmail.com"
subject = "greetings"
body = "how are you"

result = agent.invoke(
    {"messages": [HumanMessage(content=f"send email to {email}, with subject: {subject} containing text: {body}")]},
    config=config
)
result</code></pre>
<div class="output-box">
    <span class="output-label">Execution Output (State Suspension &amp; __interrupt__)</span>
{'messages': [HumanMessage(content='send email to varad0404@gmail.com...'),
              AIMessage(content='', tool_calls=[{'name': 'send_email_tool', 'args': {'body': 'how are you', 'recipient': 'varad0404@gmail.com', 'subject': 'greetings'}, 'id': 'fc_36d...'}])],
 '__interrupt__': [Interrupt(value={'action_requests': [{'name': 'send_email_tool',
                                                         'args': {'body': 'how are you', 'recipient': 'varad0404@gmail.com', 'subject': 'greetings'},
                                                         'description': "Tool execution requires approval\\n\\nTool: send_email_tool\\nArgs: {'body': 'how are you', 'recipient': 'varad0404@gmail.com', 'subject': 'greetings'}"}],
                                   'review_configs': [{'action_name': 'send_email_tool', 'allowed_decisions': ['approve', 'edit', 'reject']}]},
                             id='cac6e32465a2b8d14fc3f5bc59fb0358', response_schema=None)]}
</div>
<p><strong>Critical Architectural Highlights:</strong></p>
<ol>
    <li><strong>Selective Interception:</strong> <code>read_email_tool: False</code> executes automatically without pausing because reading data carries low operational risk. In contrast, <code>send_email_tool</code> is guarded with <code>allowed_decisions: ["approve", "edit", "reject"]</code>.</li>
    <li><strong>Halted Execution:</strong> Notice that <code>send_email_tool</code> was <em>not</em> executed. No <code>ToolMessage</code> exists in the message list.</li>
    <li><strong>The <code>__interrupt__</code> Structure:</strong> The graph yields an <code>Interrupt</code> object containing the exact proposed arguments (<code>action_requests</code>) and the approved decision schema. The current graph state is safely serialized into the <code>InMemorySaver</code> under <code>test-approve</code>.</li>
</ol>
</div>

<div class="page-break-before"></div>
<h3>Cell 8: Decision Path A - Human Approval (approve)</h3>
<pre><code># approve
from langgraph.types import Command

if "__interrupt__" in result:
    print("PAUSED waiting for approval...")

    result = agent.invoke(
        Command(
            resume={
                "decisions": [
                    {"type": "approve"}
                ]
            }
        ),
        config=config
    )

    print(f"Result: {result['messages'][-1].content}")</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result</span>
PAUSED waiting for approval...
Result: ✅ Your email has been sent to **varad0404@gmail.com** with the subject **“greetings”** and the message **“how are you.”**
</div>
<p><strong>Mechanics:</strong> Passing <code>Command(resume={"decisions": [{"type": "approve"}]})</code> informs the state machine that the human operator authorized the action. The graph resumes from the exact paused node, invokes <code>send_email_tool</code> with the original arguments, collects the tool result, and prompts the LLM to formulate the final confirmation response.</p>

<div class="avoid-break">
<h3>Cell 9: Decision Path B - Human Rejection (reject)</h3>
<pre><code># reject
# (Agent initialized with same config & prompt)
result = agent.invoke(
    {"messages": [HumanMessage(content=f"send email to {email}, with subject: {subject} containing text: {body}")]},
    config=config
)

if "__interrupt__" in result:
    print("PAUSED waiting for approval...")

    result = agent.invoke(
        Command(
            resume={
                "decisions": [
                    {"type": "reject"}
                ]
            }
        ),
        config=config
    )

    print(f"Result: {result['messages'][-1].content}")</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result</span>
PAUSED waiting for approval...
Result: I’m sorry, but I can’t send the email directly right now.  
Would you like me to draft the email for you so you can copy it into your own mail client?
</div>
<p><strong>Mechanics:</strong> When the human supplies <code>{"type": "reject"}</code>, the middleware cancels the tool execution. The underlying Python function is never called. A rejection notification is fed into the conversation state, allowing the LLM to understand that permission was denied and gracefully pivot to an alternative solution (offering to draft text instead of sending).</p>
</div>

<div class="avoid-break">
<h3>Cell 10: Decision Path C - Human Modification (edit)</h3>
<pre><code># edit
# (Agent initialized with same configuration)
correct_email = "varad0404@gmail.com"
wrong_email = "vrad0404@gmail.com"
subject = "greetings"
body = "how are you"

# Prompt contains typo in recipient
result = agent.invoke(
    {"messages": [HumanMessage(content=f"send email to {wrong_email}, with subject: {subject} containing text: {body}")]},
    config=config
)

if "__interrupt__" in result:
    print("PAUSED waiting for approval...")

    result = agent.invoke(
        Command(
            resume={
                "decisions": [
                    {
                        "type": "edit",
                        "edited_action": {
                            "name": "send_email_tool",
                            "args": {
                                "recipient": correct_email,
                                "subject": subject,
                                "body": body
                            }
                        }
                    }
                ]
            }
        ),
        config=config
    )

    print(f"Result: {result['messages'][-1].content}")</code></pre>
<div class="output-box">
    <span class="output-label">Execution Result</span>
PAUSED waiting for approval...
Result: ✅ Email sent to varad0404@gmail.com with subject “greetings” and body “how are you”.
</div>
<p><strong>Mechanics:</strong> The human detects a critical typo in the recipient's email address (<code>vrad0404@...</code>). Instead of rejecting the entire run or starting over, the operator provides <code>edited_action</code> containing the corrected parameters. The middleware injects the modified dictionary into the tool dispatcher, executing the function with <code>varad0404@gmail.com</code> without re-prompting the LLM.</p>
</div>

<!-- Section F: End-to-End Execution Flow & Dataflow Diagrams -->
<div class="page-break-before"></div>
<h2>F. End-to-End Execution Flow &amp; Dedicated Dataflow Diagrams</h2>
<p>
    The notebook highlights two distinct middleware paradigms: <strong>Autonomous Memory Optimization</strong> (Summarization) and <strong>Human-Supervised Execution Governance</strong> (HITL). Below are the explicit dataflow diagrams capturing the internal mechanics of each middleware.
</p>

<h3>1. SummarizationMiddleware Dataflow (Message Count &amp; Token Budgeting)</h3>
<p>
    When conversation length or token consumption crosses configured thresholds, the middleware interrupts the message append pipeline, invokes a dedicated summarizer model, and injects a single structured recap.
</p>

<!-- Diagram 2: Summarization Dataflow -->
<div style="text-align: center; margin: 15px 0;">
    __SVG_DIAGRAM_2__
    <p style="font-size: 8.5pt; color: #64748b; margin-top: 5px;"><em>Figure 6.2: State Compaction Cycle: 10 Accumulated Messages Compressed into 1 Summary Message + 4 Preserved Turns.</em></p>
</div>

<h3>2. HumanInTheLoopMiddleware 3-Way Decision Dataflow</h3>
<p>
    When an agent targets an intercepted tool, execution is suspended, allowing external operators to evaluate arguments and select one of three resolution paths.
</p>

<!-- Diagram 3: HITL 3-Way Dataflow -->
<div style="text-align: center; margin: 15px 0;">
    __SVG_DIAGRAM_3__
    <p style="font-size: 8.5pt; color: #64748b; margin-top: 5px;"><em>Figure 6.3: The 3-Way HITL Review Protocol: Interception, State Checkpointing, and Branching Resumption (Approve, Reject, Edit).</em></p>
</div>

<!-- Section G: Reference Guide -->
<div class="page-break-before"></div>
<h2>G. Reference Guide: Key Classes, Functions &amp; Configurations</h2>
<table>
    <tr>
        <th>Class / Function</th>
        <th>Import Path</th>
        <th>Key Parameters &amp; Configurations</th>
        <th>Runtime Role &amp; Behavior</th>
    </tr>
    <tr>
        <td><code>SummarizationMiddleware</code></td>
        <td><code>langchain.agents.middleware</code></td>
        <td><code>model</code>, <code>trigger=("messages"|"tokens", N)</code>, <code>keep=("messages"|"tokens", K)</code></td>
        <td>Lifecycle hook that monitors message history and replaces older turns with a structured summary when thresholds are met.</td>
    </tr>
    <tr>
        <td><code>HumanInTheLoopMiddleware</code></td>
        <td><code>langchain.agents.middleware</code></td>
        <td><code>interrupt_on: dict[str, dict | bool]</code>, <code>allowed_decisions: list[str]</code></td>
        <td>Intercepts designated tool calls, halts graph execution, and emits an <code>Interrupt</code> payload for human review.</td>
    </tr>
    <tr>
        <td><code>InMemorySaver</code></td>
        <td><code>langgraph.checkpoint.memory</code></td>
        <td>None (in-memory dictionary backend)</td>
        <td>Checkpointer required to serialize, persist, and resume graph execution states across thread boundaries.</td>
    </tr>
    <tr>
        <td><code>Command</code></td>
        <td><code>langgraph.types</code></td>
        <td><code>resume: dict</code>, <code>update: dict (optional)</code></td>
        <td>Control signal used to unpause an interrupted graph and pass back review decisions (approve, reject, edit).</td>
    </tr>
    <tr>
        <td><code>Interrupt</code></td>
        <td><code>langgraph.types</code></td>
        <td><code>value: dict</code>, <code>id: str</code></td>
        <td>Payload yielded in <code>response['__interrupt__']</code> describing the pending tool call and available decision options.</td>
    </tr>
</table>

<!-- Section H: Common Errors & Troubleshooting -->
<h2>H. Common Errors, Debugging &amp; Troubleshooting Guide</h2>

<div class="callout callout-error">
    <div class="callout-title">1. Missing Checkpointer When Using Interrupts or Memory</div>
    <p><strong>Symptom:</strong> <code>RuntimeError: State machine requires a checkpointer to support interrupt() or resume().</code></p>
    <p><strong>Cause:</strong> Attempting to initialize <code>create_agent(middleware=[HumanInTheLoopMiddleware(...)])</code> without supplying <code>checkpointer=InMemorySaver()</code>.</p>
    <p><strong>Fix:</strong> Always pass a checkpointer instance. LangGraph cannot pause execution or resume without a state storage layer.</p>
</div>

<div class="callout callout-warning">
    <div class="callout-title">2. Invoking an Interrupted Agent Without thread_id</div>
    <p><strong>Symptom:</strong> <code>ValueError: No thread_id provided in configuration. Cannot locate checkpoint.</code></p>
    <p><strong>Cause:</strong> Calling <code>agent.invoke(...)</code> without <code>config={"configurable": {"thread_id": "session_abc"}}</code>.</p>
    <p><strong>Fix:</strong> All stateful sessions and interrupted agents require an explicit <code>thread_id</code> so the checkpointer can index and retrieve the paused node.</p>
</div>

<div class="callout callout-warning">
    <div class="callout-title">3. Malformed Command.resume Payload Structure</div>
    <p><strong>Symptom:</strong> <code>ValidationError: Expected 'decisions' list with valid 'type' key.</code></p>
    <p><strong>Cause:</strong> Passing raw strings like <code>Command(resume="approve")</code> instead of the expected schema: <code>Command(resume={"decisions": [{"type": "approve"}]})</code>.</p>
    <p><strong>Fix:</strong> Always format the resume dictionary to match the <code>allowed_decisions</code> specified in <code>review_configs</code>.</p>
</div>

<!-- Section I: Practical Extensions -->
<div class="page-break-before"></div>
<h2>I. Practical Extensions &amp; Production Design Patterns</h2>

<h3>Pattern: Unified Production Agent with Persistent Database Checkpointing</h3>
<p>
    In real-world enterprise deployments, in-memory checkpointers lose all state if the application restarts. The code below demonstrates how to combine both <strong>Summarization</strong> and <strong>HITL</strong> with production-grade persistence and domain-specific approval filtering:
</p>

<pre><code>import os
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver # In production: from langgraph.checkpoint.postgres import PostgresSaver

# 1. Initialize models and checkpointer
# In production: checkpointer = PostgresSaver.from_conn_string(os.getenv("DATABASE_URL"))
checkpointer = InMemorySaver()

# 2. Define tools
def execute_sql_query(query: str) -> str:
    \"\"\"Execute SQL against reporting database.\"\"\"
    return f"Executed query: {query}"

def export_csv_report(filename: str) -> str:
    \"\"\"Export generated analytics data to CSV.\"\"\"
    return f"Saved report to {filename}"

# 3. Create agent with multi-middleware governance
governed_agent = create_agent(
    model=model,
    tools=[execute_sql_query, export_csv_report],
    checkpointer=checkpointer,
    middleware=[
        # A. Protect against token blowout
        SummarizationMiddleware(
            model=model,
            trigger=("tokens", 2000),
            keep=("tokens", 800)
        ),
        # B. Guard destructive SQL queries
        HumanInTheLoopMiddleware(
            interrupt_on={
                "execute_sql_query": {
                    "allowed_decisions": ["approve", "edit", "reject"]
                },
                "export_csv_report": False # Read-only action runs freely
            }
        )
    ]
)</code></pre>

<!-- Section J: Key Takeaways -->
<h2>J. Key Takeaways &amp; Conceptual Map</h2>
<ul>
    <li><strong>Middleware Decouples Concerns:</strong> Middleware allows developers to manage memory limits, auditing, and safety gates outside of the core prompt engineering workflow.</li>
    <li><strong>Checkpointers Enable State Resumption:</strong> Any agent workflow that requires pauses, reviews, or multi-turn conversational history must be bound to a checkpointer with an explicit <code>thread_id</code>.</li>
    <li><strong>Summarization Prevents Runaway Costs:</strong> <code>SummarizationMiddleware</code> converts linear token accumulation into a bounded, predictable memory ceiling via structured LLM recaps.</li>
    <li><strong>HITL Gives Humans Final Authority:</strong> The 3-way resume protocol (Approve, Reject, Edit) guarantees that autonomous agents never execute sensitive real-world side effects without human verification.</li>
</ul>

<!-- Section K: Practice Exercises -->
<div class="page-break-before"></div>
<h2>K. Practice Exercises &amp; Knowledge Checks</h2>

<div class="exercise-box">
    <div class="exercise-question">Question 1 (Conceptual): Why does HumanInTheLoopMiddleware require an active checkpointer to work?</div>
    <p>What would happen if an agent encountered an interrupt without a checkpointer configured?</p>
    <div class="answer-box">
        <strong>Answer:</strong> An interrupt suspends Python execution mid-graph. To allow the process to exit, return an HTTP response, or wait hours for a human review, the entire execution state (active node, call stack, message history) must be serialized and saved to durable storage. Without a checkpointer, the state would vanish from RAM upon function return.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 2 (Code Tracing): In Cell 4, why does the message count drop from 10 to 6 instead of 4?</div>
    <div class="answer-box">
        <strong>Answer:</strong> <code>keep=("messages", 4)</code> dictates how many *existing* messages to preserve alongside the new summary. When the trigger fired on Turn 6:
        <ul>
            <li>1 synthetic summary message is injected: <code>HumanMessage(lc_source='summarization')</code>.</li>
            <li>4 recent messages are retained from history (Turns 4 &amp; 5).</li>
            <li>1 new model response message is generated for the Turn 6 question.</li>
        </ul>
        Total messages = $1 + 4 + 1 = 6$ messages.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 3 (Operational): How does the 'edit' decision prevent hallucinated tool parameters?</div>
    <div class="answer-box">
        <strong>Answer:</strong> When an LLM generates a tool call with slight inaccuracies (e.g., misspelled email <code>vrad0404@gmail.com</code> or wrong SQL table name), passing <code>{"type": "edit", "edited_action": {...}}</code> replaces the tool arguments *in-flight*. The tool executes immediately with the verified human input without requiring another expensive or unreliable LLM re-generation turn.
    </div>
</div>

<div class="exercise-box">
    <div class="exercise-question">Question 4 (Architecture): What is the key advantage of token-based triggers over message-based triggers in tool-heavy agents?</div>
    <div class="answer-box">
        <strong>Answer:</strong> Tool outputs vary wildly in size: a single database or web search tool result can return 2,000 tokens in one message, whereas a simple greeting returns 5 tokens. Message-count triggers treat both identically, risking severe context overflow on data-dense outputs. Token-based triggers monitor actual byte and token volume, providing deterministic protection against rate limits.
    </div>
</div>

<!-- Section L: Further Learning -->
<h2>L. Further Learning &amp; Official Documentation</h2>
<ul>
    <li><a href="https://python.langchain.com/docs/how_to/agent_middleware/">LangChain Agent Middleware Guide</a></li>
    <li><a href="https://langchain-ai.github.io/langgraph/how-tos/human-in-the-loop/">LangGraph Human-In-The-Loop Documentation</a></li>
    <li><a href="https://langchain-ai.github.io/langgraph/concepts/persistence/">LangGraph Persistence &amp; Checkpointers</a></li>
    <li>Previous study guides in sequence: <strong>4-messages.pdf</strong> and <strong>5-structure.pdf</strong>.</li>
</ul>

</body>
</html>
"""
    return (html_template
            .replace("__FNAME__", fname)
            .replace("__TODAY__", today)
            .replace("__CSS_STYLES__", CSS_STYLES)
            .replace("__SVG_DIAGRAM_1__", svg1)
            .replace("__SVG_DIAGRAM_2__", svg2)
            .replace("__SVG_DIAGRAM_3__", svg3))

def build_guide_langgraph_1(fname, cells, today):
    """Build canonical 12-section educational guide for 1-BasicChatBot.ipynb."""
    svg1 = get_svg_langgraph_state_machine()
    svg2 = get_svg_langgraph_react_cycle()
    svg3 = get_svg_langgraph_memory_saver()
    svg4 = get_svg_langgraph_streaming_modes()

    html_template = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>__FNAME__ - Educational Study Guide</title>
    <style>__CSS_STYLES__</style>
</head>
<body>

<!-- Section A: Cover Page -->
<div class="cover-page">
    <span class="cover-badge">LangGraph 0.3+ • Agentic Workflows &amp; State Machines</span>
    <h1 class="cover-title">Building Stateful Agentic Chatbots with LangGraph</h1>
    <p class="cover-subtitle">StateGraph Architecture, add_messages Reducers, Dynamic ReAct Tool Cycles, MemorySaver Persistence, and Multi-Modal Streaming</p>
    
    <p style="font-size: 10.5pt; color: #475569; max-width: 580px; margin-top: 15px;">
        An authoritative, publication-grade technical study guide deconstructing stateful agent architectures.
        Covers the transition from linear LLM chains to cyclical state graphs, deterministic message reducers,
        closed-loop ReAct tool calling, cross-invocation state checkpointing via <code>MemorySaver</code>, and real-time
        streaming telemetry with <code>astream_events v2</code>.
    </p>

    <div class="cover-meta">
        <div class="cover-meta-grid">
            <div class="meta-item"><strong>Target Notebook:</strong> <code>__FNAME__</code></div>
            <div class="meta-item"><strong>Generation Date:</strong> __TODAY__</div>
            <div class="meta-item"><strong>Language &amp; Runtime:</strong> Python 3.14 • Virtualenv (.venv)</div>
            <div class="meta-item"><strong>Core Frameworks:</strong> LangGraph 0.3+ • LangChain 1.4.7 • Groq LPU • Tavily</div>
        </div>
    </div>
</div>

<!-- Section B: Learning Objectives -->
<h2>B. Learning Objectives</h2>
<p>After studying this notebook and study guide, you will master:</p>
<ul>
    <li><strong>The Graph-Based Agent Paradigm:</strong> Understand why cyclic directed graphs supersede sequential chains for autonomous agent control flow and multi-step reasoning.</li>
    <li><strong>State Definition &amp; Reducer Mechanics:</strong> Define schema contracts with <code>TypedDict</code> and master the <code>Annotated[list, add_messages]</code> reducer to intelligently append conversation turns and update messages by ID.</li>
    <li><strong>Pure Node Computations:</strong> Author decoupled node functions that ingest the global state snapshot and return atomic delta dictionaries without in-place mutation.</li>
    <li><strong>Tool Integration &amp; ToolNode:</strong> Bind search and calculation tools to LLMs using <code>bind_tools()</code> and execute them safely with LangGraph's prebuilt <code>ToolNode</code>.</li>
    <li><strong>Dynamic ReAct Feedback Loops:</strong> Route execution dynamically with <code>tools_condition</code> and construct cyclic feedback edges to enable continuous reasoning over tool observations.</li>
    <li><strong>State Checkpointing &amp; Session Continuity:</strong> Attach <code>MemorySaver</code> to persist multi-turn conversational memory across invocations using partitioned <code>thread_id</code> configurations.</li>
    <li><strong>Streaming Telemetry:</strong> Differentiate between node mutation streaming (<code>updates</code>), full state snapshots (<code>values</code>), and token-by-token lifecycle event streaming (<code>astream_events v2</code>).</li>
</ul>

<!-- Section C: Prerequisites, Environment & Security Setup -->
<h2>C. Prerequisites, Environment &amp; Security Setup</h2>
<div class="callout callout-note">
    <div class="callout-title">Runtime &amp; API Configuration</div>
    This notebook runs on <strong>Python 3.14</strong> within the project virtual environment. It connects to the <strong>Groq LPU Inference Engine</strong> utilizing the <code>openai/gpt-oss-20b</code> open-weights reasoning model, and the <strong>Tavily Search API</strong> for real-time external information retrieval.
</div>
<table>
    <tr>
        <th>Component</th>
        <th>Version / Identifier</th>
        <th>Source / Purpose</th>
    </tr>
    <tr>
        <td><code>langgraph</code></td>
        <td><code>>=0.3.0</code></td>
        <td>Cyclical state machine engine, <code>StateGraph</code>, <code>START</code>, <code>END</code>, <code>ToolNode</code></td>
    </tr>
    <tr>
        <td><code>langchain</code></td>
        <td><code>1.4.7</code></td>
        <td>Core agent abstractions, message schemas, and <code>init_chat_model</code> factory</td>
    </tr>
    <tr>
        <td><code>langchain-groq</code></td>
        <td><code>>=1.1.3</code></td>
        <td>Ultra-low-latency LPU model execution (Groq chat completions)</td>
    </tr>
    <tr>
        <td><code>langchain-tavily</code></td>
        <td><code>>=0.2.18</code></td>
        <td>Optimized autonomous search engine for AI agents (real-time web queries)</td>
    </tr>
    <tr>
        <td><code>python-dotenv</code></td>
        <td><code>>=1.2.4</code></td>
        <td>Secure environment variable loading from local <code>.env</code> file</td>
    </tr>
</table>

<div class="callout callout-warning">
    <div class="callout-title">Security &amp; API Key Masking Protocol</div>
    Never commit raw API keys to Git. Keep keys in <code>.env</code>, which is excluded by <code>.gitignore</code>:
    <pre><code>GROQ_API_KEY=gsk_your_groq_api_key_here
TAVILY_API_KEY=tvly-your_tavily_api_key_here</code></pre>
</div>

<!-- Section D: Comprehensive Topic Overview -->
<div class="page-break-before"></div>
<h2>D. Comprehensive Topic Overview</h2>
<p>
    Building production-grade autonomous agents requires more than prompt chaining. Real-world tasks demand
    <strong>cycles</strong>, <strong>state accumulation</strong>, <strong>tool feedback loops</strong>, and
    <strong>durable persistence</strong>. LangGraph was built by the LangChain team specifically to address the
    architectural limitations of linear Directed Acyclic Graphs (DAGs).
</p>

<h3>1. Why Cyclic Graphs? From Chains to State Machines</h3>
<p>
    Traditional LLM pipelines (such as LangChain Expression Language or LCEL chains) enforce linear, one-way dataflow:
    $$\text{Prompt} \longrightarrow \text{LLM} \longrightarrow \text{Parser} \longrightarrow \text{Output}$$
    While suitable for single-turn extraction or straightforward summarization, this linear paradigm fails when an agent
    must iterate: an agent may invoke a search tool, evaluate the returned snippets, realize that crucial facts are still
    missing, invoke a second tool (e.g., a calculator), inspect that output, and only then formulate a final response.
    This iterative thought-action-observation cycle is the foundation of the <strong>ReAct (Reasoning + Acting)</strong>
    pattern. LangGraph represents this lifecycle natively as a <strong>State Machine</strong> with nodes, edges, and cycles.
</p>

<h3>2. The Three Pillars of LangGraph Architecture</h3>
<ul>
    <li><strong>State:</strong> A central, typed data structure (typically a Python <code>TypedDict</code> or Pydantic model) that serves as the single source of truth for the entire workflow. Every node reads from and writes to this shared state.</li>
    <li><strong>Nodes:</strong> Regular Python functions (or prebuilt components like <code>ToolNode</code>) that receive the current state snapshot, perform a unit of computation (such as an LLM call or API query), and return a <em>delta dictionary</em> containing updates to specific state keys.</li>
    <li><strong>Edges:</strong> Rules governing control flow between nodes. Edges can be <em>unconditional</em> (always route from Node A to Node B) or <em>conditional</em> (dynamically inspect state to choose the next node or terminate at <code>END</code>).</li>
</ul>

<h3>3. The Critical Role of Reducers (<code>add_messages</code>)</h3>
<p>
    By default, when a node in LangGraph returns a dictionary like <code>{"messages": [new_msg]}</code>, standard Python dictionary
    semantics would overwrite the entire <code>messages</code> key, deleting all previous conversation history!
    To prevent accidental data loss, LangGraph introduces <strong>Reducers</strong> via Python's <code>typing.Annotated</code>.
    The <code>add_messages</code> reducer defines custom merge semantics:
</p>
<ul>
    <li><strong>List Concatenation:</strong> Appends new incoming messages to the existing list rather than overwriting.</li>
    <li><strong>Update-by-ID:</strong> If an incoming message shares the same unique <code>id</code> as an existing message in state, the existing message is replaced in-place (essential for Human-in-the-Loop revisions or tool response overwrites).</li>
    <li><strong>Type Normalization:</strong> Automatically converts raw strings or primitive dictionaries into first-class LangChain message objects (e.g., <code>HumanMessage</code>, <code>AIMessage</code>).</li>
</ul>

<div class="diagram-container avoid-break">
    <div class="diagram-title">Figure 1: Core LangGraph State Machine Architecture</div>
    __SVG_DIAGRAM_1__
    <div class="diagram-caption">
        <strong>Figure 1 Architectural Breakdown:</strong> Deconstruction of state definition, functional node execution,
        and graph compilation. The <code>add_messages</code> reducer prevents state key erasure by merging delta updates into the cumulative turn history.
    </div>
</div>

<!-- Section E: Detailed Notebook Walkthrough -->
<div class="page-break-before"></div>
<h2>E. Detailed Notebook Walkthrough</h2>
<p>
    The source notebook <code>1-BasicChatBot.ipynb</code> progresses methodically through four major evolutionary phases:
    from a basic single-node conversational graph to a full ReAct agent with tools, persistent checkpoint memory, and streaming telemetry.
</p>

<h3>Phase 1: Environment Setup &amp; Basic ChatBot Graph (Cells 0–4)</h3>

<h4>Cell 0 &amp; 1: Imports and Core Abstractions</h4>
<div class="code-header">Cell 1 • Library Imports</div>
<pre><code>import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages #Reducer
from IPython.display import Image, display
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode, tools_condition</code></pre>
<p><strong>Detailed Analysis:</strong></p>
<ul>
    <li><code>init_chat_model</code>: Unified model factory providing provider-agnostic model instantiation.</li>
    <li><code>StateGraph, START, END</code>: The foundational graph builder and virtual boundary nodes. <code>START</code> indicates where execution begins upon invocation; <code>END</code> marks the terminal sink.</li>
    <li><code>add_messages</code>: The built-in reducer function attached to the state message list.</li>
    <li><code>ToolNode, tools_condition</code>: LangGraph's prebuilt building blocks for tool execution and conditional routing.</li>
</ul>

<h4>Cell 2: Model Instantiation via Groq LPU</h4>
<div class="code-header">Cell 2 • Model Initialization</div>
<pre><code>load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

llm = init_chat_model("groq:openai/gpt-oss-20b")
llm</code></pre>
<p><strong>Execution Output:</strong></p>
<pre><code>ChatGroq(
  metadata={'lc_versions': {'langchain-core': '1.7.0', 'langchain': '1.4.7'}},
  profile={'name': 'GPT OSS 20B', 'max_input_tokens': 131072, 'max_output_tokens': 65536,
           'tool_calling': True, 'reasoning_output': True},
  model_name='openai/gpt-oss-20b'
)</code></pre>
<p><strong>Architectural Rationale:</strong> Using <code>openai/gpt-oss-20b</code> on Groq delivers sub-second inference with native tool-calling capabilities and explicit reasoning token outputs.</p>

<h4>Cell 3: State Schema &amp; Node Function Definition</h4>
<div class="code-header">Cell 3 • Defining State and Chatbot Node</div>
<pre><code>class State(TypedDict):
    messages: Annotated[list, add_messages]

# Node Functionality
def chatbot(state: State): # will act as node and llm calling takes place here (brain)
    return {
        "messages": [llm.invoke(state["messages"])]
    }</code></pre>
<p><strong>Line-by-Line Breakdown:</strong></p>
<ul>
    <li><code>class State(TypedDict):</code> Defines the graph state structure. Using <code>TypedDict</code> ensures zero runtime overhead while offering strict static type hints in modern IDEs.</li>
    <li><code>messages: Annotated[list, add_messages]</code>: Decorates the <code>list</code> type with the <code>add_messages</code> reducer metadata. Whenever a node returns a dictionary with key <code>"messages"</code>, LangGraph routes the update through <code>add_messages(existing_messages, new_messages)</code>.</li>
    <li><code>def chatbot(state: State):</code> The node function. Notice it receives the current <code>state</code> dictionary, calls <code>llm.invoke(state["messages"])</code>, and wraps the returned <code>AIMessage</code> in a single-element list.</li>
    <li><strong>Critical Rule:</strong> The node function never mutates <code>state</code> directly (e.g. never calls <code>state["messages"].append(...)</code>). It returns only the delta update dictionary.</li>
</ul>

<h4>Cell 4: Assembling, Compiling &amp; Invoking the Basic Graph</h4>
<div class="code-header">Cell 4 • Graph Assembly &amp; Execution</div>
<pre><code># Building the StateGraph
graph_builder = StateGraph(State)

# Add node
graph_builder.add_node("llmchatbot", chatbot)

# Add edges
graph_builder.add_edge(START, "llmchatbot")
graph_builder.add_edge("llmchatbot", END)

# Compile the graph
graph = graph_builder.compile()

display(Image(graph.get_graph().draw_mermaid_png()))

response = graph.invoke({"messages": "Hi"})
response["messages"][-1].content</code></pre>
<p><strong>Execution Output:</strong></p>
<pre><code>'Hello! How can I help you today?'</code></pre>
<p><strong>Execution Lifecycle:</strong></p>
<ol>
    <li>The client invokes <code>graph.invoke({"messages": "Hi"})</code>.</li>
    <li>The raw string <code>"Hi"</code> is normalized into a <code>HumanMessage(content="Hi")</code> by the reducer and placed into state.</li>
    <li>Execution flows from <code>START</code> to the node <code>"llmchatbot"</code>.</li>
    <li><code>chatbot(state)</code> invokes the Groq LLM with the message list. The model returns an <code>AIMessage(content="Hello! How can I help you today?")</code>.</li>
    <li>The reducer appends the <code>AIMessage</code> to state. Execution flows to <code>END</code>.</li>
    <li>The compiled graph returns the final accumulated state containing both the human query and AI response.</li>
</ol>

<div class="page-break-before"></div>
<h3>Phase 2: External Tools Setup (Cells 5–7)</h3>

<h4>Cell 6: Tavily Web Search Tool Exploration</h4>
<div class="code-header">Cell 6 • Standalone Tool Verification</div>
<pre><code># Tavily Search helps with internet exploration
tool = TavilySearch(max_results=2)
tool.invoke("what is LangGraph")</code></pre>
<p><strong>Execution Output:</strong></p>
<pre><code>{'query': 'what is LangGraph',
 'results': [
   {'url': 'https://www.geeksforgeeks.org/machine-learning/what-is-langgraph',
    'title': 'What is LangGraph - GeeksforGeeks',
    'content': 'LangGraph is an open-source framework from LangChain designed to build and manage AI agent workflows using graph-based structures...'},
   {'url': 'https://python.langchain.com/docs/langgraph',
    'title': 'LangGraph Documentation',
    'content': 'LangGraph is a library for building stateful, multi-actor applications with LLMs...'}
 ]}</code></pre>
<p><strong>Pedagogical Insight:</strong> Testing the tool in isolation via <code>tool.invoke()</code> confirms network access, API key validity, and expected dictionary return schema before binding it to an agent graph.</p>

<h4>Cell 7: Custom Python Tool &amp; Model Binding</h4>
<div class="code-header">Cell 7 • Defining Arithmetic Tool and Binding to LLM</div>
<pre><code># Custom tool
def multiply(a: int, b: int) -> int:
    \"\"\"
    Multiply a and b
    Args:
        a (int): first int
        b (int): second int

    Returns:
        int: output int
    \"\"\"
    return a * b

tools = [tool, multiply]
llm_with_tool = llm.bind_tools(tools)
llm_with_tool</code></pre>
<p><strong>Execution Output:</strong></p>
<pre><code>_ChatModelBinding(
  bound=ChatGroq(model_name='openai/gpt-oss-20b', ...),
  kwargs={'tools': [
    {'type': 'function', 'function': {'name': 'tavily_search', 'description': '...', 'parameters': {...}}},
    {'type': 'function', 'function': {'name': 'multiply', 'description': 'Multiply a and b', 'parameters': {'properties': {'a': {'type': 'integer'}, 'b': {'type': 'integer'}}, 'required': ['a', 'b']}}}
  ]}
)</code></pre>
<p><strong>Crucial Rule:</strong> The LLM <em>never executes Python functions directly</em>. <code>bind_tools()</code> extracts function signatures, type annotations, and docstrings into an OpenAI-compatible JSON schema. The model inspects this schema and decides when to emit a structured request to call a tool.</p>

<div class="page-break-before"></div>
<h3>Phase 3: The Static Tool Graph &amp; The "Premature Termination" Pitfall (Cell 8)</h3>

<h4>Cell 8: Static Graph with Linear Termination</h4>
<div class="code-header">Cell 8 • Graph with Non-Cyclic Edge: tools -&gt; END</div>
<pre><code># StateGraph
def tool_calling_llm(state: State): # brain
    return {
        "messages": [llm_with_tool.invoke(state["messages"])]
    }

builder = StateGraph(State)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode(tools))

# Add edges
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm", tools_condition)
builder.add_edge("tools", END) # &lt;-- PITFALL: Terminal edge!

graph = builder.compile()
display(Image(graph.get_graph().draw_mermaid_png()))

response = graph.invoke({
    "messages": "What is the recent mbappe vs china news about"
})

for message in response['messages']:
    message.pretty_print()</code></pre>
<p><strong>Execution Output Trace:</strong></p>
<pre><code>================================ Human Message =================================
What is the recent mbappe vs china news about

================================== Ai Message ==================================
Tool Calls:
  tavily_search (fc_31c85fb3-9df1-416c-b2e3-26253be060fc)
 Call ID: fc_31c85fb3-9df1-416c-b2e3-26253be060fc
  Args:
    query: Mbappe vs China news recent
    search_depth: advanced
    topic: news

================================= Tool Message =================================
Name: tavily_search
{"query": "Mbappe vs China news recent", "results": [{"url": "...", "content": "Mbappe jokingly commented..."}]}</code></pre>
<div class="callout callout-warning">
    <div class="callout-title">Architectural Deconstruction of the Premature Termination Trap</div>
    Look closely at the output: the graph executed <code>HumanMessage</code> $\rightarrow$ <code>AIMessage (Tool Call)</code> $\rightarrow$ <code>ToolMessage</code>, and then <strong>abruptly halted</strong>!
    Why? Because line 14 declared <code>builder.add_edge("tools", END)</code>.
    Once the <code>ToolNode</code> executed Tavily search and produced the <code>ToolMessage</code>, control routed directly to <code>END</code>.
    The LLM was <strong>never reinvoked</strong> to read the tool's findings and synthesize a human-readable answer!
</div>

<div class="page-break-before"></div>
<h3>Phase 4: The Dynamic ReAct Cyclic Loop (Cells 9–10)</h3>

<h4>Cell 10: Closing the Loop with a Cyclic Feedback Edge</h4>
<div class="code-header">Cell 10 • Closed-Loop ReAct Architecture</div>
<pre><code>def tool_calling_llm(state: State):
    return {
        "messages": [llm_with_tool.invoke(state["messages"])]
    }

builder = StateGraph(State)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm", tools_condition)
builder.add_edge("tools", "tool_calling_llm") # &lt;-- THE CYCLIC FEEDBACK EDGE!

graph = builder.compile()
display(Image(graph.get_graph().draw_mermaid_png()))

response = graph.invoke({"messages": "Give me the ballon d'or and then multiply 5 by 10"})
for m in response['messages']:
    m.pretty_print()</code></pre>
<p><strong>Execution Trace (The Complete 4-Turn ReAct Lifecycle):</strong></p>
<pre><code>1. HumanMessage:
   "Give me the ballon d'or and then multiply 5 by 10"

2. AIMessage (Reasoning &amp; Tool Request):
   Tool Calls:
     tavily_search (fc_f087ec7a-618c-406f-921c-ea0b11779201)
     Args: {'query': "most recent Ballon d'Or winner 2023", 'topic': 'general'}

3. ToolMessage (External Observation):
   Name: tavily_search
   Content: {"query": "most recent Ballon d'Or winner 2023", "results": [{"content": "Lionel Messi won the 2023 Ballon d'Or..."}]}

4. AIMessage (Synthesized Final Answer):
   "The most recent recipient of the Ballon d'Or (as of the 2023 ceremony) is Lionel Messi...
    Regarding the calculation: 5 * 10 = 50."</code></pre>
<p><strong>How the ReAct Cycle Worked:</strong></p>
<ol>
    <li><code>tool_calling_llm</code> decided it needed external data to answer the Ballon d'Or question. It emitted a tool call request for <code>tavily_search</code>.</li>
    <li><code>tools_condition</code> inspected the <code>AIMessage</code>. Because <code>tool_calls</code> was populated, it routed control to <code>"tools"</code>.</li>
    <li><code>ToolNode</code> executed <code>tavily_search(...)</code>, constructed a <code>ToolMessage</code> with the raw search results, and added it to state.</li>
    <li>The cyclic edge <code>builder.add_edge("tools", "tool_calling_llm")</code> routed execution <strong>back to the LLM node</strong>!</li>
    <li><code>tool_calling_llm</code> ran a second time. It now saw the full history: user query + tool call request + tool results. It formulated the complete answer and computed $5 \times 10 = 50$.</li>
    <li><code>tools_condition</code> ran again. Finding no further tool calls in the latest <code>AIMessage</code>, it routed to <code>END</code>.</li>
</ol>

<div class="page-break-before"></div>
<h3>Phase 5: State Persistence &amp; Checkpointing (Cells 11–12)</h3>

<h4>Cell 11: Compiling with <code>MemorySaver</code> and Thread Binding</h4>
<div class="code-header">Cell 11 • Attaching Checkpointer and First Conversational Turn</div>
<pre><code>from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

# Graph assembly
builder = StateGraph(State)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges("tool_calling_llm", tools_condition)
builder.add_edge("tools", "tool_calling_llm")

# Compile graph with checkpointer
graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}} # Session identifier

response = graph.invoke({"messages": "Hi my name is Varad"}, config=config)
response['messages'][-1].content</code></pre>
<p><strong>Execution Output:</strong> <code>'Hello Varad! How can I help you today?'</code></p>

<h4>Cell 12: Contextual Recall Across Invocations</h4>
<div class="code-header">Cell 12 • Second Turn with Zero Client History</div>
<pre><code>response = graph.invoke({"messages": "what is my name"}, config=config)
response['messages'][-1].content</code></pre>
<p><strong>Execution Output:</strong> <code>'Your name is Varad.'</code></p>
<div class="callout callout-tip">
    <div class="callout-title">The Power of Checkpointing</div>
    Notice that the client passed <em>only</em> <code>{"messages": "what is my name"}</code> in Cell 12! The client never passed the previous turn.
    Because <code>thread_id="1"</code> was provided in <code>config</code>, LangGraph automatically loaded the state checkpoint saved at the end of Cell 11, applied the <code>add_messages</code> reducer to append the new question, and passed the full history to the model.
</div>

<div class="page-break-before"></div>
<h3>Phase 6: Execution Streaming Paradigms (Cells 13–15)</h3>

<h4>Cell 14: Comparing <code>stream_mode="updates"</code> vs <code>stream_mode="values"</code></h4>
<div class="code-header">Cell 14 • Node Mutations vs State Snapshots</div>
<pre><code>from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

def superbot(state: State):
    return {"messages": [llm.invoke(state['messages'])]}

graph = StateGraph(State)
graph.add_node("SuperBot", superbot)
graph.add_edge(START, "SuperBot")
graph.add_edge("SuperBot", END)
graph_builder = graph.compile(checkpointer=memory)

# 1. Updates streaming -> yields node mutation deltas
config = {"configurable": {"thread_id": "2"}}
for chunk in graph_builder.stream({'messages': "Hi, My name is Varad And I like football"}, config, stream_mode="updates"):
    print(chunk)

# 2. Values streaming -> yields cumulative state snapshots
config = {"configurable": {"thread_id": "3"}}
for chunk in graph_builder.stream({'messages': "Hi, My name is Varad And I like football"}, config, stream_mode="values"):
    print(chunk)</code></pre>
<p><strong>Output Analysis &amp; Differences:</strong></p>
<ul>
    <li><code>stream_mode="updates"</code> yields:
        <pre><code>{'SuperBot': {'messages': [AIMessage(content="Hello Varad! Great to meet a fellow football fan...")]}}</code></pre>
        Only the changes produced by the executing node are emitted.
    </li>
    <li><code>stream_mode="values"</code> yields:
        <pre><code>Step 1 (Input/START): {'messages': [HumanMessage(content="Hi, My name is Varad...")]}
Step 2 (After SuperBot): {'messages': [HumanMessage(...), AIMessage(...)]}</code></pre>
        The complete cumulative graph state is emitted at every transition.
    </li>
</ul>

<h4>Cell 15: Fine-Grained Lifecycle &amp; Token Streaming with <code>astream_events v2</code></h4>
<div class="code-header">Cell 15 • Asynchronous Event Streaming</div>
<pre><code>config = {"configurable": {"thread_id": "4"}}

async for event in graph_builder.astream_events(
    {"messages": ["Hi My name is Varad and I like watching football"]},
    config,
    version="v2"
):
    print(event)</code></pre>
<p><strong>Event Stream Timeline:</strong></p>
<table>
    <tr>
        <th>Event Name</th>
        <th>Emitting Component</th>
        <th>Event Payload Details</th>
    </tr>
    <tr>
        <td><code>on_chain_start</code></td>
        <td><code>LangGraph Engine</code></td>
        <td>Graph initialization, input payload, run ID, and thread metadata</td>
    </tr>
    <tr>
        <td><code>on_chat_model_start</code></td>
        <td><code>ChatGroq</code></td>
        <td>Model invocation parameters, prompt messages, and temperature</td>
    </tr>
    <tr>
        <td><code>on_chat_model_stream</code></td>
        <td><code>ChatGroq</code></td>
        <td>Incremental token chunks (<code>AIMessageChunk</code>) emitted in real time as the LPU generates text</td>
    </tr>
    <tr>
        <td><code>on_chat_model_end</code></td>
        <td><code>ChatGroq</code></td>
        <td>Complete assembled <code>AIMessage</code>, token usage statistics, and finish reason</td>
    </tr>
    <tr>
        <td><code>on_chain_end</code></td>
        <td><code>LangGraph Engine</code></td>
        <td>Final serialized state checkpoint written to <code>MemorySaver</code></td>
    </tr>
</table>

<!-- Section F: End-to-End Execution Flow & Architectural Synthesis -->
<div class="page-break-before"></div>
<h2>F. End-to-End Execution Flow &amp; Architectural Synthesis</h2>
<p>
    The components explored across the notebook combine into a cohesive, fault-tolerant agent architecture.
    The diagrams below illustrate the dynamic cyclic loop, checkpointed multi-turn memory, and streaming modes.
</p>

<div class="diagram-container avoid-break">
    <div class="diagram-title">Figure 2: ReAct Dynamic Cyclic Execution vs Static Linear Termination</div>
    __SVG_DIAGRAM_2__
    <div class="diagram-caption">
        <strong>Figure 2 Architectural Breakdown:</strong> Panel A illustrates the premature termination defect in Cell 8, where
        the graph terminates immediately after tool execution. Panel B demonstrates the complete ReAct architecture in Cell 10,
        where the cyclic edge routes tool observations back to the LLM for synthesis and final answer generation.
    </div>
</div>

<div class="diagram-container avoid-break" style="margin-top: 25px;">
    <div class="diagram-title">Figure 3: MemorySaver State Checkpointing &amp; Multi-Turn Session Isolation</div>
    __SVG_DIAGRAM_3__
    <div class="diagram-caption">
        <strong>Figure 3 Architectural Breakdown:</strong> How <code>MemorySaver</code> maintains conversation state across independent
        invocations via <code>thread_id</code>, while guaranteeing strict isolation between concurrent user sessions.
    </div>
</div>

<div class="diagram-container avoid-break" style="margin-top: 25px;">
    <div class="diagram-title">Figure 4: LangGraph Execution &amp; Streaming Modes Comparison</div>
    __SVG_DIAGRAM_4__
    <div class="diagram-caption">
        <strong>Figure 4 Architectural Breakdown:</strong> Comparative matrix of LangGraph streaming modalities:
        mutation-level diffs (<code>updates</code>), snapshot states (<code>values</code>), and token-by-token lifecycle streams (<code>astream_events v2</code>).
    </div>
</div>

<!-- Section G: Reference Guide: Important APIs & Classes -->
<div class="page-break-before"></div>
<h2>G. Reference Guide: Important APIs &amp; Classes</h2>
<table>
    <tr>
        <th>Class / Function</th>
        <th>Module</th>
        <th>Key Parameters</th>
        <th>Return / Behavior</th>
    </tr>
    <tr>
        <td><code>StateGraph(state_schema)</code></td>
        <td><code>langgraph.graph</code></td>
        <td><code>state_schema: Type[TypedDict]</code></td>
        <td>Initializes an uncompiled graph builder enforcing the specified state schema contract.</td>
    </tr>
    <tr>
        <td><code>add_messages</code></td>
        <td><code>langgraph.graph.message</code></td>
        <td><code>(left: list, right: list | BaseMessage)</code></td>
        <td>Reducer function: appends new messages, updates messages with identical IDs, and normalizes primitives.</td>
    </tr>
    <tr>
        <td><code>ToolNode(tools)</code></td>
        <td><code>langgraph.prebuilt</code></td>
        <td><code>tools: Sequence[BaseTool | Callable]</code></td>
        <td>Prebuilt node that inspects the latest <code>AIMessage.tool_calls</code>, executes matching tools, and returns <code>[ToolMessage]</code>.</td>
    </tr>
    <tr>
        <td><code>tools_condition(state)</code></td>
        <td><code>langgraph.prebuilt</code></td>
        <td><code>state: dict | BaseMessage</code></td>
        <td>Conditional edge router: returns <code>"tools"</code> if the last message contains <code>tool_calls</code>; otherwise returns <code>END</code>.</td>
    </tr>
    <tr>
        <td><code>MemorySaver()</code></td>
        <td><code>langgraph.checkpoint.memory</code></td>
        <td>None</td>
        <td>In-memory key-value checkpointer persisting graph state snapshots indexed by <code>thread_id</code> and checkpoint ID.</td>
    </tr>
    <tr>
        <td><code>builder.compile(checkpointer=...)</code></td>
        <td><code>langgraph.graph.StateGraph</code></td>
        <td><code>checkpointer: BaseCheckpointSaver</code></td>
        <td>Validates graph topology and produces an immutable, executable <code>CompiledStateGraph</code> instance.</td>
    </tr>
    <tr>
        <td><code>graph.stream(input, config, stream_mode=...)</code></td>
        <td><code>langgraph.graph.state.CompiledStateGraph</code></td>
        <td><code>stream_mode: "updates" | "values"</code></td>
        <td>Generator yielding node-level deltas (<code>"updates"</code>) or cumulative state snapshots (<code>"values"</code>) at each step.</td>
    </tr>
    <tr>
        <td><code>graph.astream_events(input, config, version="v2")</code></td>
        <td><code>langgraph.graph.state.CompiledStateGraph</code></td>
        <td><code>version: "v2"</code></td>
        <td>Async generator yielding fine-grained execution lifecycle events (tokens, tool dispatches, model completions).</td>
    </tr>
</table>

<!-- Section H: Common Errors, Debugging & Troubleshooting -->
<h2>H. Common Errors, Debugging &amp; Troubleshooting</h2>

<div class="callout callout-error avoid-break">
    <div class="callout-title">Pitfall 1: Omission of Reducer Decorator (State Overwrite Trap)</div>
    <strong>Symptom:</strong> The agent only remembers the immediate last turn. All previous messages vanish from state.<br>
    <strong>Root Cause:</strong> Defining state as <code>messages: list</code> without <code>Annotated[list, add_messages]</code>. In standard Python, updating a dictionary key replaces the entire value.<br>
    <strong>Fix:</strong>
    <pre><code># Incorrect: Overwrites previous turns!
class State(TypedDict):
    messages: list

# Correct: Merges and accumulates history via reducer!
class State(TypedDict):
    messages: Annotated[list, add_messages]</code></pre>
</div>

<div class="callout callout-error avoid-break">
    <div class="callout-title">Pitfall 2: Premature Terminal Edge (The Broken ReAct Loop)</div>
    <strong>Symptom:</strong> The graph completes execution, but the user receives a raw <code>ToolMessage</code> or unparsed tool output instead of a conversational answer.<br>
    <strong>Root Cause:</strong> Adding <code>builder.add_edge("tools", END)</code>. Execution stops as soon as the tool completes, preventing the model from synthesizing the observation.<br>
    <strong>Fix:</strong>
    <pre><code># Incorrect: Dead end after tool call
builder.add_edge("tools", END)

# Correct: Dynamic cyclic loop back to model node!
builder.add_edge("tools", "tool_calling_llm")</code></pre>
</div>

<div class="callout callout-error avoid-break">
    <div class="callout-title">Pitfall 3: Checkpointing Memory Leaks &amp; Missing thread_id</div>
    <strong>Symptom:</strong> <code>ValueError: No thread_id provided in configurable</code>, or different users seeing each other's chat history.<br>
    <strong>Root Cause:</strong> Invoking a checkpointer-backed graph without passing <code>config={"configurable": {"thread_id": ...}}</code>, or reusing a static hardcoded <code>thread_id="1"</code> across distinct users.<br>
    <strong>Fix:</strong>
    <pre><code># Generate unique session thread IDs per user session
import uuid
session_config = {"configurable": {"thread_id": str(uuid.uuid4())}}
response = graph.invoke({"messages": "Hello"}, config=session_config)</code></pre>
</div>

<!-- Section I: Practical Extensions & Industry Best Practices -->
<div class="page-break-before"></div>
<h2>I. Practical Extensions &amp; Industry Best Practices</h2>
<ul>
    <li><strong>Production Checkpointers:</strong> While <code>MemorySaver</code> is ideal for local development, production multi-tenant deployments require durable, persistent storage such as <code>AsyncPostgresSaver</code> (from <code>langgraph-checkpoint-postgres</code>) or Redis checkpointers. This guarantees state survival across server restarts and horizontal scaling.</li>
    <li><strong>Graceful Tool Error Handling:</strong> External APIs fail or return rate limits. Configure <code>ToolNode</code> with <code>handle_tool_errors=True</code> so that exceptions are caught and converted into a polite <code>ToolMessage</code> explaining the error, allowing the LLM to recover or attempt alternative tools.</li>
    <li><strong>Context Window Pruning:</strong> Over hundreds of turns, message lists exceed LLM context windows. Combine LangGraph checkpointing with message trimming (e.g. <code>trim_messages</code>) or token-triggered summarization nodes to bound token consumption.</li>
</ul>

<!-- Section J: Key Takeaways & Conceptual Map -->
<h2>J. Key Takeaways &amp; Conceptual Map</h2>
<div class="callout callout-tip">
    <div class="callout-title">Core Principles of LangGraph Development</div>
    <ol>
        <li><strong>State is the Single Source of Truth:</strong> Everything the agent knows, sees, and remembers resides in the typed state dictionary.</li>
        <li><strong>Reducers Control State Mutations:</strong> Use <code>Annotated[list, add_messages]</code> to ensure conversation turns accumulate cleanly.</li>
        <li><strong>Nodes are Pure Transformers:</strong> Nodes receive the global state snapshot and return minimal delta dictionaries.</li>
        <li><strong>ReAct Requires Cycles:</strong> Never terminate after <code>tools</code>. Route <code>tools</code> back to the LLM node to close the thought-action-observation loop.</li>
        <li><strong>Persistence is Opt-In:</strong> Supply a checkpointer and pass <code>thread_id</code> in the configuration to achieve stateful multi-turn memory.</li>
        <li><strong>Stream According to Needs:</strong> Use <code>updates</code> for node debugging, <code>values</code> for full chat state, and <code>astream_events v2</code> for typewriter UI tokens.</li>
    </ol>
</div>

<!-- Section K: Practice Exercises & Knowledge Checks -->
<div class="page-break-before"></div>
<h2>K. Practice Exercises &amp; Knowledge Checks</h2>

<div class="callout callout-note avoid-break">
    <strong>Question 1 (Conceptual):</strong> Explain what happens under the hood if a node in a LangGraph graph returns <code>{"messages": [AIMessage(id="msg_123", content="Revised answer")]}</code> when a message with ID <code>msg_123</code> already exists in state.
</div>

<div class="callout callout-note avoid-break">
    <strong>Question 2 (Code Tracing):</strong> In a compiled ReAct graph with nodes <code>agent</code> and <code>tools</code>, how many times does the <code>agent</code> node execute if the user prompt is: <em>"Find the capital of France, and then find the capital of Japan"</em>, assuming the model executes searches sequentially?
</div>

<div class="callout callout-note avoid-break">
    <strong>Question 3 (Debugging):</strong> A developer compiles their graph with <code>MemorySaver()</code> and runs:
    <pre><code>res1 = graph.invoke({"messages": "I live in Berlin"}, config={"configurable": {"thread_id": "A"}})
res2 = graph.invoke({"messages": "Where do I live?"}, config={"configurable": {"thread_id": "B"}})</code></pre>
    Will <code>res2</code> know that the user lives in Berlin? Explain why or why not.
</div>

<div class="callout callout-note avoid-break">
    <strong>Question 4 (Implementation Challenge):</strong> Write a custom conditional routing function <code>route_by_urgency(state: State) -> str</code> that inspects the latest message: if it contains the word "emergency", it routes to a node named <code>human_escalation</code>; otherwise, it routes to <code>tools_condition</code>.
</div>

<h3>Answers &amp; Complete Explanations</h3>
<div class="callout callout-tip avoid-break">
    <strong>Answer 1:</strong> The <code>add_messages</code> reducer detects matching IDs. Instead of appending a duplicate message, it performs an in-place replacement of the existing message with <code>id="msg_123"</code>. This allows agents or human reviewers to revise or edit previous turns without corrupting conversation flow.
</div>
<div class="callout callout-tip avoid-break">
    <strong>Answer 2:</strong> The <code>agent</code> node executes <strong>3 times</strong>:
    <ol>
        <li>Execution 1: Emits tool call for Paris search.</li>
        <li>Execution 2: Receives Paris result, emits tool call for Tokyo search.</li>
        <li>Execution 3: Receives Tokyo result, synthesizes both observations, and emits the final response without tool calls, routing to <code>END</code>.</li>
    </ol>
</div>
<div class="callout callout-tip avoid-break">
    <strong>Answer 3:</strong> <strong>No.</strong> <code>MemorySaver</code> strictly partitions checkpoints by <code>thread_id</code>. Thread <code>"B"</code> has an empty independent state history and has no visibility into Thread <code>"A"</code>.
</div>
<div class="callout callout-tip avoid-break">
    <strong>Answer 4:</strong>
    <pre><code>def route_by_urgency(state: State) -> str:
    last_message = state["messages"][-1]
    if "emergency" in str(last_message.content).lower():
        return "human_escalation"
    return tools_condition(state)</code></pre>
</div>

<!-- Section L: Further Learning & Official Documentation -->
<h2>L. Further Learning &amp; Official Documentation</h2>
<ul>
    <li><a href="https://langchain-ai.github.io/langgraph/">LangGraph Official Documentation</a>: Concepts, how-to guides, and tutorials on cyclical graph architecture.</li>
    <li><a href="https://langchain-ai.github.io/langgraph/concepts/persistence/">LangGraph Persistence &amp; Checkpointing Guide</a>: Comprehensive overview of state backends, time travel, and human-in-the-loop workflows.</li>
    <li><a href="https://python.langchain.com/docs/integrations/chat/groq/">LangChain Groq Integration</a>: High-throughput LPU model inference with OpenAI compatibility.</li>
    <li><a href="https://docs.tavily.com/">Tavily AI Search Engine Documentation</a>: Real-time search optimization and query parameters for agentic exploration.</li>
</ul>

</body>
</html>
"""

    return (html_template
            .replace("__FNAME__", fname)
            .replace("__TODAY__", today)
            .replace("__CSS_STYLES__", CSS_STYLES)
            .replace("__SVG_DIAGRAM_1__", svg1)
            .replace("__SVG_DIAGRAM_2__", svg2)
            .replace("__SVG_DIAGRAM_3__", svg3)
            .replace("__SVG_DIAGRAM_4__", svg4))

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
