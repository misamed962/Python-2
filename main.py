import webview
import random

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Крестики-нолики</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: 'Segoe UI', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white; min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    user-select: none;
}
.container {
    background: rgba(0,0,0,0.35); padding: 40px;
    border-radius: 24px; text-align: center;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    max-width: 95vw;
}
h1 { margin: 0 0 20px 0; font-size: 28px; }
h2 { margin: 10px 0; }
p { font-size: 18px; margin: 12px 0; }
input {
    padding: 12px 16px; font-size: 18px;
    border: none; border-radius: 8px;
    outline: none; width: 250px;
}
button {
    padding: 12px 28px; font-size: 18px;
    border: none; border-radius: 8px;
    background: #ff6b6b; color: white;
    cursor: pointer; margin: 8px;
    transition: transform 0.1s, background 0.2s;
    font-weight: bold;
}
button:hover { background: #ff5252; transform: translateY(-2px); }
.symbol-btn {
    font-size: 48px; width: 100px; height: 100px; padding: 0;
    background: rgba(255,255,255,0.2);
    border: 3px solid rgba(255,255,255,0.4);
}
.symbol-btn:hover { background: rgba(255,255,255,0.35); }
.board {
    display: grid; gap: 3px; margin: 20px auto;
    background: rgba(0,0,0,0.3); padding: 3px;
    border-radius: 8px; width: fit-content;
}
.cell {
    background: rgba(255,255,255,0.15);
    display: flex; align-items: center; justify-content: center;
    font-weight: bold; cursor: pointer; border-radius: 4px;
    transition: background 0.15s; color: white;
}
.cell:hover { background: rgba(255,255,255,0.35); }
.cell.filled { cursor: default; }
.cell.filled:hover { background: rgba(255,255,255,0.15); }
.cell.x { color: #ffdd57; }
.cell.o { color: #5ce1e6; }
#status {
    font-size: 20px; min-height: 30px;
    margin: 15px 0; font-weight: bold;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
.hidden { display: none !important; }
</style>
</head>
<body>
<div class="container">
    <div id="welcome">
        <h1>🎮 Крестики-нолики</h1>
        <p>Как вас зовут, капитан?</p>
        <input id="nameInput" type="text" placeholder="Введите имя" autofocus>
        <br><br>
        <button onclick="submitName()">Далее →</button>
    </div>
    <div id="choose" class="hidden">
        <h2>Привет, <span id="playerName"></span>! 👋</h2>
        <p>Выберите свою фигуру:</p>
        <div>
            <button class="symbol-btn" onclick="chooseSymbol('X')">X</button>
            <button class="symbol-btn" onclick="chooseSymbol('O')">O</button>
        </div>
    </div>
    <div id="game" class="hidden">
        <div id="status"></div>
        <div id="board" class="board"></div>
        <button id="restartBtn" class="hidden" onclick="restartGame()">Играть снова</button>
    </div>
</div>
<script>
let playerName = "";

function submitName() {
    const name = document.getElementById('nameInput').value.trim();
    if (!name) { alert('Введите имя'); return; }
    playerName = name;
    document.getElementById('playerName').textContent = name;
    document.getElementById('welcome').classList.add('hidden');
    document.getElementById('choose').classList.remove('hidden');
}

async function chooseSymbol(symbol) {
    document.getElementById('choose').classList.add('hidden');
    document.getElementById('game').classList.remove('hidden');
    const result = await window.pywebview.api.setup(playerName, symbol);
    renderBoard(result.board);
    updateStatus(`Сетка ${result.size}×${result.size}. Ваш ход!`);
}

function renderBoard(board) {
    const el = document.getElementById('board');
    const n = board.length;
    const cellSize = Math.min(60, Math.floor(560 / n));
    el.style.gridTemplateColumns = `repeat(${n}, ${cellSize}px)`;
    el.style.gridTemplateRows = `repeat(${n}, ${cellSize}px)`;
    el.innerHTML = '';
    for (let r = 0; r < n; r++) {
        for (let c = 0; c < n; c++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.style.fontSize = Math.floor(cellSize * 0.65) + 'px';
            const v = board[r][c];
            cell.textContent = v;
            if (v === 'X') cell.classList.add('x', 'filled');
            if (v === 'O') cell.classList.add('o', 'filled');
            if (v === '') cell.onclick = () => playerMove(r, c);
            else cell.classList.add('filled');
            el.appendChild(cell);
        }
    }
}

function updateStatus(msg) {
    document.getElementById('status').textContent = msg;
}

async function playerMove(r, c) {
    const result = await window.pywebview.api.player_move(r, c);
    if (result.error) return;
    renderBoard(result.board);
    if (result.result === 'continue') {
        updateStatus('Ваш ход.');
    } else if (result.result === 'win') {
        updateStatus('🎉 Вы выиграли эту сетку! Переход к следующей...');
        setTimeout(async () => {
            const next = await window.pywebview.api.next_game();
            renderBoard(next.board);
            updateStatus(`Сетка ${next.size}×${next.size}. Ваш ход!`);
        }, 1600);
    } else if (result.result === 'final_win') {
        updateStatus('🏆 Молодец! Теперь вы настоящий КАПИТАН!');
        document.getElementById('restartBtn').classList.remove('hidden');
    } else if (result.result === 'lose') {
        updateStatus('😔 Вы проиграли. Начинаем заново на этой сетке...');
        setTimeout(async () => {
            const next = await window.pywebview.api.next_game();
            renderBoard(next.board);
            updateStatus(`Сетка ${next.size}×${next.size}. Ваш ход!`);
        }, 1600);
    } else if (result.result === 'draw') {
        updateStatus('🤝 Ничья. Начинаем заново...');
        setTimeout(async () => {
            const next = await window.pywebview.api.next_game();
            renderBoard(next.board);
            updateStatus(`Сетка ${next.size}×${next.size}. Ваш ход!`);
        }, 1600);
    }
}

async function restartGame() {
    const result = await window.pywebview.api.restart();
    document.getElementById('restartBtn').classList.add('hidden');
    renderBoard(result.board);
    updateStatus(`Сетка ${result.size}×${result.size}. Ваш ход!`);
}
</script>
</body>
</html>
"""

class GameAPI:
    def __init__(self):
        self.player_symbol = "X"
        self.ai_symbol = "O"
        self.grid_size = 3
        self.board = []

    def setup(self, name, symbol):
        self.player_symbol = symbol
        self.ai_symbol = "O" if symbol == "X" else "X"
        self.grid_size = 3
        self._new_board()
        return {"size": self.grid_size, "board": self.board}

    def restart(self):
        self.grid_size = 3
        self._new_board()
        return {"size": self.grid_size, "board": self.board}

    def next_game(self):
        self._new_board()
        return {"size": self.grid_size, "board": self.board}

    def _new_board(self):
        self.board = [["" for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def _check_win(self, symbol):
        n = self.grid_size
        b = self.board
        for r in range(n):
            for c in range(n):
                if b[r][c] != symbol:
                    continue
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    cnt = 1
                    rr, cc = r + dr, c + dc
                    while 0 <= rr < n and 0 <= cc < n and b[rr][cc] == symbol:
                        cnt += 1
                        rr += dr
                        cc += dc
                    if cnt >= 3:
                        return True
        return False

    def _is_full(self):
        return all(cell != "" for row in self.board for cell in row)

    def _ai_move(self):
        n = self.grid_size
        # 1. Победный ход
        for r in range(n):
            for c in range(n):
                if self.board[r][c] == "":
                    self.board[r][c] = self.ai_symbol
                    won = self._check_win(self.ai_symbol)
                    self.board[r][c] = ""
                    if won:
                        return (r, c)
        # 2. Блок игрока
        for r in range(n):
            for c in range(n):
                if self.board[r][c] == "":
                    self.board[r][c] = self.player_symbol
                    won = self._check_win(self.player_symbol)
                    self.board[r][c] = ""
                    if won:
                        return (r, c)
        # 3. Рядом с существующими фигурами (с рандомом)
        candidates = []
        for r in range(n):
            for c in range(n):
                if self.board[r][c] != "":
                    continue
                score = 0
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        if dr == 0 and dc == 0:
                            continue
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < n and 0 <= cc < n and self.board[rr][cc] != "":
                            score += 1
                candidates.append((score, r, c))
        if candidates:
            best_score = max(x[0] for x in candidates)
            best = [x for x in candidates if x[0] == best_score]
            _, r, c = random.choice(best)
            return (r, c)
        empty = [(r, c) for r in range(n) for c in range(n) if self.board[r][c] == ""]
        return random.choice(empty) if empty else None

    def player_move(self, r, c):
        if not (0 <= r < self.grid_size and 0 <= c < self.grid_size):
            return {"error": "invalid"}
        if self.board[r][c] != "":
            return {"error": "occupied"}
        self.board[r][c] = self.player_symbol
        if self._check_win(self.player_symbol):
            if self.grid_size >= 12:
                return {"result": "final_win", "board": self.board}
            self.grid_size += 1
            return {"result": "win", "board": self.board}
        if self._is_full():
            return {"result": "draw", "board": self.board}
        move = self._ai_move()
        if move:
            self.board[move[0]][move[1]] = self.ai_symbol
            if self._check_win(self.ai_symbol):
                return {"result": "lose", "board": self.board}
            if self._is_full():
                return {"result": "draw", "board": self.board}
        return {"result": "continue", "board": self.board}

if __name__ == "__main__":
    api = GameAPI()
    webview.create_window("Крестики-нолики", html=HTML, js_api=api, width=850, height=800)
    webview.start()
