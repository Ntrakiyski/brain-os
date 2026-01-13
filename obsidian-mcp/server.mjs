#!/usr/bin/env node
/**
 * HTTP wrapper for YuNaga224/obsidian-memory-mcp
 *
 * The original MCP server only supports stdio transport.
 * This wrapper provides an HTTP endpoint for Docker networking.
 *
 * Phase 5.1: Basic Neo4j → Obsidian sync
 */

import express from 'express';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8001;

// Obsidian vault path (from env or default)
const MEMORY_DIR = process.env.MEMORY_DIR || '/vault';
// In Docker: /app/obsidian-memory-mcp, in local dev: /app/temp_repo
const MCP_SERVER_PATH = process.env.MCP_SERVER_PATH || join(__dirname, 'obsidian-memory-mcp');

let mcpProcess = null;
let mcpStdin = null;
let pendingRequests = new Map();
let requestId = 0;

/**
 * Start the MCP server (stdio)
 */
function startMCPServer() {
    console.log(`Starting Obsidian MCP server...`);
    console.log(`  Memory dir: ${MEMORY_DIR}`);
    console.log(`  MCP server: ${MCP_SERVER_PATH}`);

    mcpProcess = spawn('node', ['dist/index.js'], {
        cwd: MCP_SERVER_PATH,
        env: {
            ...process.env,
            MEMORY_DIR,
        },
        stdio: ['pipe', 'pipe', 'inherit'],
    });

    mcpStdin = mcpProcess.stdin;

    // Handle stdout (MCP responses)
    mcpProcess.stdout.on('data', (data) => {
        const output = data.toString();
        // Process MCP JSON-RPC responses
        const lines = output.split('\n').filter(line => line.trim());

        for (const line of lines) {
            try {
                const response = JSON.parse(line);

                // Match response to pending request
                if (response.id !== undefined && pendingRequests.has(response.id)) {
                    const { resolve } = pendingRequests.get(response.id);
                    pendingRequests.delete(response.id);
                    resolve(response);
                }
            } catch (e) {
                // Not JSON, ignore
            }
        }
    });

    // Handle MCP server errors
    mcpProcess.on('error', (err) => {
        console.error(`MCP process error: ${err.message}`);
    });

    mcpProcess.on('exit', (code) => {
        console.log(`MCP process exited with code ${code}`);
        // Auto-restart
        setTimeout(startMCPServer, 1000);
    });

    console.log('MCP server started');
}

/**
 * Send JSON-RPC request to MCP server
 */
function sendMCPRequest(method, params = {}) {
    return new Promise((resolve, reject) => {
        const currentId = requestId++;

        // Set up response handler
        pendingRequests.set(currentId, { resolve, reject });

        // Timeout after 5 seconds
        const timeout = setTimeout(() => {
            pendingRequests.delete(currentId);
            reject(new Error('MCP request timeout'));
        }, 5000);

        // Send request
        const request = {
            jsonrpc: '2.0',
            id: currentId,
            method,
            params,
        };

        mcpStdin.write(JSON.stringify(request) + '\n');

        // Clear timeout on response
        const originalResolve = resolve;
        resolve = (value) => {
            clearTimeout(timeout);
            originalResolve(value);
        };
    });
}

/**
 * Initialize MCP server (send initialize request)
 */
async function initializeMCP() {
    await sendMCPRequest('initialize', {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: {
            name: 'brainos-http-wrapper',
            version: '1.0.0',
        },
    });

    await sendMCPRequest('notifications/initialized');
    console.log('MCP server initialized');
}

// Express middleware
app.use(express.json());

/**
 * Main MCP endpoint
 */
app.post('/mcp', async (req, res) => {
    try {
        const { method, params } = req.body;

        // Forward to MCP server
        const response = await sendMCPRequest(method, params);

        res.json(response);
    } catch (error) {
        console.error(`HTTP request error: ${error.message}`);
        res.status(500).json({
            error: {
                code: -32603,
                message: error.message,
            },
        });
    }
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
    const isHealthy = mcpProcess !== null && mcpProcess.exitCode === null;
    res.json({
        status: isHealthy ? 'healthy' : 'unhealthy',
        mcp: isHealthy ? 'connected' : 'disconnected',
        memoryDir: MEMORY_DIR,
    });
});

// Start server
startMCPServer();

// Wait a bit for MCP to start, then initialize
setTimeout(async () => {
    try {
        await initializeMCP();
        app.listen(PORT, () => {
            console.log(`HTTP wrapper listening on port ${PORT}`);
            console.log(`POST /mcp - MCP endpoint`);
            console.log(`GET /health - Health check`);
        });
    } catch (error) {
        console.error(`Failed to initialize MCP: ${error.message}`);
        process.exit(1);
    }
}, 1000);

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('Shutting down...');
    if (mcpProcess) {
        mcpProcess.kill();
    }
    process.exit(0);
});
