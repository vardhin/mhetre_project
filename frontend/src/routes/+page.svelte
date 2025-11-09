<script lang="ts">
    import { onMount } from 'svelte';

    let raspberryPiIp = '';
    let isConnected = false;
    let isLoading = false;
    let error = '';
    let detectionData: any = null;
    let lastUpdated = '';

    // Load saved IP from localStorage
    onMount(() => {
        const savedIp = localStorage.getItem('raspberryPiIp');
        if (savedIp) {
            raspberryPiIp = savedIp;
        }
    });

    async function testConnection() {
        if (!raspberryPiIp) {
            error = 'Please enter Raspberry Pi IP address';
            return;
        }

        isLoading = true;
        error = '';

        try {
            const response = await fetch(`http://${raspberryPiIp}:8000/health`);
            const data = await response.json();

            if (data.camera === 'ok' && data.model === 'ok') {
                isConnected = true;
                localStorage.setItem('raspberryPiIp', raspberryPiIp);
                error = '';
            } else {
                error = `Connection issues - Camera: ${data.camera}, Model: ${data.model}`;
                isConnected = false;
            }
        } catch (err) {
            error = 'Failed to connect. Check IP address and network connection.';
            isConnected = false;
        } finally {
            isLoading = false;
        }
    }

    async function detectObjects() {
        if (!raspberryPiIp) {
            error = 'Please enter Raspberry Pi IP address';
            return;
        }

        isLoading = true;
        error = '';

        try {
            const response = await fetch(`http://${raspberryPiIp}:8000/detect`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error('Detection failed');
            }

            detectionData = await response.json();
            lastUpdated = new Date().toLocaleString();
        } catch (err) {
            error = 'Detection failed. Please try again.';
            console.error(err);
        } finally {
            isLoading = false;
        }
    }

    function disconnect() {
        isConnected = false;
        detectionData = null;
        raspberryPiIp = '';
        localStorage.removeItem('raspberryPiIp');
    }
</script>

<svelte:head>
    <title>Object Detection System</title>
</svelte:head>

<div class="container">
    <header>
        <h1>🎯 Real-Time Object Detection</h1>
        <p class="subtitle">Powered by YOLOv8 on Raspberry Pi</p>
    </header>

    <!-- Connection Section -->
    <div class="connection-card">
        <div class="connection-header">
            <h2>📡 Connection Setup</h2>
            {#if isConnected}
                <span class="status-badge connected">Connected</span>
            {:else}
                <span class="status-badge disconnected">Disconnected</span>
            {/if}
        </div>

        {#if !isConnected}
            <div class="input-group">
                <label for="ip-input">Raspberry Pi IP Address</label>
                <input
                    id="ip-input"
                    type="text"
                    bind:value={raspberryPiIp}
                    placeholder="e.g., 10.245.25.140"
                    disabled={isLoading}
                />
                <p class="hint">Enter the IP address of your Raspberry Pi on the local network</p>
            </div>

            <button class="btn btn-primary" on:click={testConnection} disabled={isLoading}>
                {#if isLoading}
                    <span class="spinner"></span> Connecting...
                {:else}
                    Connect
                {/if}
            </button>
        {:else}
            <div class="connected-info">
                <p><strong>Connected to:</strong> {raspberryPiIp}:8000</p>
                <div class="button-group">
                    <button class="btn btn-primary" on:click={detectObjects} disabled={isLoading}>
                        {#if isLoading}
                            <span class="spinner"></span> Detecting...
                        {:else}
                            🔍 Detect Objects
                        {/if}
                    </button>
                    <button class="btn btn-secondary" on:click={disconnect}>Disconnect</button>
                </div>
            </div>
        {/if}

        {#if error}
            <div class="error-message">⚠️ {error}</div>
        {/if}
    </div>

    <!-- Detection Results -->
    {#if detectionData}
        <div class="results-section">
            <!-- Summary Cards -->
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="card-icon">📊</div>
                    <div class="card-content">
                        <h3>Total Objects</h3>
                        <p class="card-value">{detectionData.total_objects}</p>
                    </div>
                </div>

                <div class="summary-card">
                    <div class="card-icon">🏷️</div>
                    <div class="card-content">
                        <h3>Unique Classes</h3>
                        <p class="card-value">{Object.keys(detectionData.object_counts).length}</p>
                    </div>
                </div>

                <div class="summary-card">
                    <div class="card-icon">⏰</div>
                    <div class="card-content">
                        <h3>Last Updated</h3>
                        <p class="card-timestamp">{lastUpdated}</p>
                    </div>
                </div>
            </div>

            <!-- Image Display -->
            <div class="image-card">
                <h2>📷 Detection Results</h2>
                <div class="image-container">
                    <img src={detectionData.annotated_image} alt="Detected objects" />
                </div>
            </div>

            <!-- Object Counts -->
            <div class="counts-card">
                <h2>📈 Object Counts</h2>
                <div class="counts-grid">
                    {#each Object.entries(detectionData.object_counts) as [className, count]}
                        <div class="count-item">
                            <span class="count-label">{className}</span>
                            <span class="count-badge">{count}</span>
                        </div>
                    {/each}
                </div>
            </div>

            <!-- Detailed Detections -->
            <div class="detections-card">
                <h2>🔍 Detailed Detections</h2>
                <div class="detections-table">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Class</th>
                                <th>Confidence</th>
                                <th>Bounding Box</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each detectionData.detections as detection, index}
                                <tr>
                                    <td>{index + 1}</td>
                                    <td>
                                        <span class="class-tag">{detection.class}</span>
                                    </td>
                                    <td>
                                        <div class="confidence-bar">
                                            <div
                                                class="confidence-fill"
                                                style="width: {detection.confidence * 100}%"
                                            ></div>
                                            <span class="confidence-text"
                                                >{(detection.confidence * 100).toFixed(1)}%</span
                                            >
                                        </div>
                                    </td>
                                    <td class="bbox-cell">
                                        <code
                                            >({detection.bounding_box.x1.toFixed(0)}, {detection.bounding_box.y1.toFixed(
                                                0
                                            )}) - ({detection.bounding_box.x2.toFixed(
                                                0
                                            )}, {detection.bounding_box.y2.toFixed(0)})</code
                                        >
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    {/if}
</div>

<style>
    :global(body) {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell,
            sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    header {
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }

    h1 {
        font-size: 3rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }

    .subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }

    .connection-card,
    .image-card,
    .counts-card,
    .detections-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        margin-bottom: 2rem;
    }

    .connection-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }

    .connection-header h2 {
        margin: 0;
        color: #333;
    }

    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .status-badge.connected {
        background: #d4edda;
        color: #155724;
    }

    .status-badge.disconnected {
        background: #f8d7da;
        color: #721c24;
    }

    .input-group {
        margin-bottom: 1.5rem;
    }

    label {
        display: block;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #333;
    }

    input {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        font-size: 1rem;
        transition: border-color 0.3s;
    }

    input:focus {
        outline: none;
        border-color: #667eea;
    }

    .hint {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.5rem;
    }

    .btn {
        padding: 0.75rem 2rem;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }

    .btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .btn-primary:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    .btn-secondary {
        background: #6c757d;
        color: white;
    }

    .btn-secondary:hover:not(:disabled) {
        background: #5a6268;
    }

    .button-group {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }

    .connected-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
    }

    .connected-info p {
        margin: 0 0 1rem 0;
        color: #333;
    }

    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        border: 1px solid #f5c6cb;
    }

    .spinner {
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 0.6s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .results-section {
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .summary-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }

    .card-icon {
        font-size: 2.5rem;
    }

    .card-content h3 {
        margin: 0;
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
    }

    .card-value {
        margin: 0.5rem 0 0 0;
        font-size: 2rem;
        font-weight: 700;
    }

    .card-timestamp {
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
        font-weight: 600;
    }

    h2 {
        color: #333;
        margin: 0 0 1.5rem 0;
        font-size: 1.5rem;
    }

    .image-container {
        background: #f8f9fa;
        border-radius: 8px;
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 400px;
    }

    .image-container img {
        max-width: 100%;
        height: auto;
        display: block;
    }

    .counts-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
    }

    .count-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .count-label {
        font-weight: 600;
        color: #333;
        text-transform: capitalize;
    }

    .count-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 700;
    }

    .detections-table {
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th {
        background: #f8f9fa;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        color: #333;
        border-bottom: 2px solid #dee2e6;
    }

    td {
        padding: 1rem;
        border-bottom: 1px solid #dee2e6;
    }

    tbody tr:hover {
        background: #f8f9fa;
    }

    .class-tag {
        background: #e7f3ff;
        color: #0066cc;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        text-transform: capitalize;
    }

    .confidence-bar {
        position: relative;
        background: #e9ecef;
        border-radius: 20px;
        height: 24px;
        overflow: hidden;
    }

    .confidence-fill {
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        background: linear-gradient(90deg, #28a745, #20c997);
        transition: width 0.3s;
    }

    .confidence-text {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        font-weight: 600;
        font-size: 0.85rem;
        color: #333;
    }

    .bbox-cell code {
        background: #f8f9fa;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        color: #495057;
    }

    @media (max-width: 768px) {
        .container {
            padding: 1rem;
        }

        h1 {
            font-size: 2rem;
        }

        .summary-grid {
            grid-template-columns: 1fr;
        }

        .button-group {
            flex-direction: column;
        }

        .btn {
            width: 100%;
            justify-content: center;
        }
    }
</style>