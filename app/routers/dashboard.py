from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from app.services.storage import get_data, connected_clients

router = APIRouter()

WS_SCRIPT = """
<script>
(function() {
    var proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    var wsUrl = proto + '//' + location.host + '/ws';
    var ws;

    function connect() {
        ws = new WebSocket(wsUrl);
        ws.onmessage = function(event) {
            var msg = JSON.parse(event.data);
            updateDashboard(msg.data, msg.timestamp);
        };
        ws.onclose = function() {
            setTimeout(connect, 2000);
        };
    }

    function updateDashboard(data, timestamp) {
        // If we're on the empty page, rebuild the whole page
        if (document.querySelector('.empty')) {
            location.reload();
            return;
        }

        // Update header
        document.querySelector('.header h1').textContent = data.strategy;
        var spans = document.querySelectorAll('.subtitle span:not(.sep)');
        spans[0].textContent = data.symbol;
        spans[1].textContent = data.exchange;
        spans[2].textContent = 'TF ' + data.timeframe;

        // Aggregate totals
        var totalTrades = 0, totalWins = 0, totalLosses = 0, bestPnl = -Infinity;
        data.data.forEach(function(r) {
            totalTrades += r.total_trades;
            totalWins += r.wins;
            totalLosses += r.losses;
            if (r.pnl_percent > bestPnl) bestPnl = r.pnl_percent;
        });
        var winrate = totalTrades ? Math.round(totalWins / totalTrades * 1000) / 10 : 0;

        // Update cards
        var cards = document.querySelectorAll('.card .value');
        cards[0].textContent = totalTrades;
        cards[1].textContent = totalWins;
        cards[2].textContent = totalLosses;
        cards[3].textContent = winrate + '%';
        cards[3].className = 'value ' + (winrate >= 50 ? 'green' : 'red');
        cards[4].textContent = bestPnl + '%';
        cards[4].className = 'value ' + (bestPnl >= 0 ? 'green' : 'red');

        // Update table rows
        var tbody = document.querySelector('table');
        // Keep header row, remove data rows
        while (tbody.rows.length > 1) tbody.deleteRow(1);
        data.data.forEach(function(row) {
            var tr = tbody.insertRow();
            tr.insertCell().textContent = row.rr;
            tr.insertCell().textContent = row.total_trades;
            var wc = tr.insertCell(); wc.textContent = row.wins; wc.className = 'green';
            var lc = tr.insertCell(); lc.textContent = row.losses; lc.className = 'red';
            var wrc = tr.insertCell(); wrc.textContent = row.winrate + '%'; wrc.className = row.winrate >= 50 ? 'green' : 'red';
            var pfc = tr.insertCell(); pfc.textContent = row.profit_factor; pfc.className = row.profit_factor >= 1 ? 'green' : 'red';
            var pnlc = tr.insertCell(); pnlc.textContent = row.pnl_percent + '%'; pnlc.className = row.pnl_percent >= 0 ? 'green' : 'red';
        });

        // Update footer timestamp
        document.querySelector('.footer').innerHTML = '<span class="dot"></span> Ultima actualizacion: ' + timestamp;
    }

    connect();
})();
</script>
"""


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


@router.get("/", response_class=HTMLResponse)
def dashboard():
    data, timestamp = get_data()
    if not data:
        return f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="/static/style.css">
            <title>Trading Journal</title>
        </head>
        <body>
            <div class="empty">
                <h2>No hay datos aun</h2>
                <p>Esperando datos del webhook de TradingView...</p>
            </div>
            {WS_SCRIPT}
        </body>
        </html>
        """

    # Aggregate totals from all RR rows
    total_trades = sum(row['total_trades'] for row in data['data'])
    total_wins = sum(row['wins'] for row in data['data'])
    total_losses = sum(row['losses'] for row in data['data'])
    winrate = round(total_wins / total_trades * 100, 1) if total_trades else 0
    best_pnl = max(row['pnl_percent'] for row in data['data'])

    rows = ""
    for row in data["data"]:
        pnl_val = row['pnl_percent']
        pnl_class = "green" if pnl_val >= 0 else "red"
        pf_val = row['profit_factor']
        pf_class = "green" if pf_val >= 1 else "red"
        wr_val = row['winrate']
        wr_class = "green" if wr_val >= 50 else "red"

        rows += f"""
            <tr>
                <td>{row['rr']}</td>
                <td>{row['total_trades']}</td>
                <td class="green">{row['wins']}</td>
                <td class="red">{row['losses']}</td>
                <td class="{wr_class}">{wr_val}%</td>
                <td class="{pf_class}">{pf_val}</td>
                <td class="{pnl_class}">{pnl_val}%</td>
            </tr>"""

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/style.css">
        <title>Trading Journal</title>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{data['strategy']}</h1>
                <div class="subtitle">
                    <span>{data['symbol']}</span>
                    <span class="sep">|</span>
                    <span>{data['exchange']}</span>
                    <span class="sep">|</span>
                    <span>TF {data['timeframe']}</span>
                </div>
            </div>

            <div class="cards">
                <div class="card">
                    <div class="label">Total Trades</div>
                    <div class="value blue">{total_trades}</div>
                </div>
                <div class="card">
                    <div class="label">Wins</div>
                    <div class="value green">{total_wins}</div>
                </div>
                <div class="card">
                    <div class="label">Losses</div>
                    <div class="value red">{total_losses}</div>
                </div>
                <div class="card">
                    <div class="label">Winrate</div>
                    <div class="value {'green' if winrate >= 50 else 'red'}">{winrate}%</div>
                </div>
                <div class="card">
                    <div class="label">Mejor PNL</div>
                    <div class="value {'green' if best_pnl >= 0 else 'red'}">{best_pnl}%</div>
                </div>
            </div>

            <div class="table-wrapper">
                <h2>Detalle por Risk-Reward</h2>
                <table>
                    <tr>
                        <th>RR</th>
                        <th>Trades</th>
                        <th>Wins</th>
                        <th>Losses</th>
                        <th>Winrate</th>
                        <th>PF</th>
                        <th>PNL %</th>
                    </tr>
                    {rows}
                </table>
            </div>

            <div class="footer">
                <span class="dot"></span> Ultima actualizacion: {timestamp}
            </div>
        </div>
        {WS_SCRIPT}
    </body>
    </html>
    """

    return html
