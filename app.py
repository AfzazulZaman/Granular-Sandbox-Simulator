from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Granular Sandbox Simulator</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #1e1e1e;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        #controls {
            margin: 20px;
        }
        .button {
            background: #333;
            color: white;
            padding: 10px 20px;
            border: 2px solid #555;
            margin: 0 5px;
            cursor: pointer;
            border-radius: 5px;
        }
        .button.selected {
            border-color: #0f0;
        }
        canvas {
            border: 1px solid #888;
            image-rendering: pixelated;
        }
    </style>
</head>
<body>
    <h1>Granular Sandbox Simulator</h1>
    <div id="controls">
        <button class="button" data-element="sand">Sand</button>
        <button class="button" data-element="water">Water</button>
        <button class="button" data-element="fire">Fire</button>
        <button class="button" data-element="plant">Plant</button>
    </div>
    <canvas id="canvas" width="300" height="300"></canvas>

    <script>
        // Constants
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const gridSize = 100;
        const cellSize = width / gridSize;
        const grid = Array.from({ length: gridSize }, () => Array(gridSize).fill(null));
        let currentElement = 'sand';
        let mouseDown = false;

        const colors = {
            sand: '#c2b280',
            water: '#3399ff',
            fire: '#ff4500',
            plant: '#00cc44'
        };

        const buttons = document.querySelectorAll('.button');
        buttons.forEach(button => {
            button.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('selected'));
                button.classList.add('selected');
                currentElement = button.getAttribute('data-element');
            });
        });
        buttons[0].classList.add('selected'); // Default

        canvas.addEventListener('mousedown', () => mouseDown = true);
        canvas.addEventListener('mouseup', () => mouseDown = false);
        canvas.addEventListener('mouseleave', () => mouseDown = false);

        canvas.addEventListener('mousemove', e => {
            if (!mouseDown) return;
            const rect = canvas.getBoundingClientRect();
            const x = Math.floor((e.clientX - rect.left) / cellSize);
            const y = Math.floor((e.clientY - rect.top) / cellSize);
            if (inBounds(x, y)) {
                grid[y][x] = { type: currentElement, life: 100 };
            }
        });

        function inBounds(x, y) {
            return x >= 0 && y >= 0 && x < gridSize && y < gridSize;
        }

        function updateGrid() {
            for (let y = gridSize - 1; y >= 0; y--) {
                for (let x = 0; x < gridSize; x++) {
                    const cell = grid[y][x];
                    if (!cell) continue;

                    switch (cell.type) {
                        case 'sand':
                            if (inBounds(x, y + 1) && !grid[y + 1][x]) {
                                grid[y + 1][x] = cell;
                                grid[y][x] = null;
                            }
                            break;
                        case 'water':
                            let dirs = [[0, 1], [-1, 1], [1, 1], [-1, 0], [1, 0]];
                            for (let [dx, dy] of dirs) {
                                let nx = x + dx, ny = y + dy;
                                if (inBounds(nx, ny) && !grid[ny][nx]) {
                                    grid[ny][nx] = cell;
                                    grid[y][x] = null;
                                    break;
                                }
                            }
                            break;
                        case 'fire':
                            cell.life -= 1;
                            let burned = false;
                            for (let [dx, dy] of [[0, -1], [0, 1], [-1, 0], [1, 0]]) {
                                let nx = x + dx, ny = y + dy;
                                if (inBounds(nx, ny) && grid[ny][nx]?.type === 'plant') {
                                    grid[ny][nx] = { type: 'fire', life: 100 };
                                    burned = true;
                                }
                            }
                            if (cell.life <= 0 || !burned) {
                                grid[y][x] = null;
                            }
                            break;
                        case 'plant':
                            for (let [dx, dy] of [[0, -1], [0, 1], [-1, 0], [1, 0]]) {
                                let nx = x + dx, ny = y + dy;
                                if (inBounds(nx, ny) && grid[ny][nx]?.type === 'water') {
                                    let growDirs = [[-1, -1], [1, -1], [-1, 1], [1, 1]];
                                    for (let [gx, gy] of growDirs) {
                                        let gx_ = x + gx, gy_ = y + gy;
                                        if (inBounds(gx_, gy_) && !grid[gy_][gx_]) {
                                            grid[gy_][gx_] = { type: 'plant', life: 100 };
                                            break;
                                        }
                                    }
                                    break;
                                }
                            }
                            break;
                    }
                }
            }
        }

        function drawGrid() {
            ctx.clearRect(0, 0, width, height);
            for (let y = 0; y < gridSize; y++) {
                for (let x = 0; x < gridSize; x++) {
                    const cell = grid[y][x];
                    if (cell) {
                        ctx.fillStyle = colors[cell.type];
                        ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
                    }
                }
            }
        }

        function loop() {
            updateGrid();
            drawGrid();
            requestAnimationFrame(loop);
        }

        loop(); // Start simulation
    </script>
</body>
</html>
""")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
