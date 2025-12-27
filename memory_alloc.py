import tkinter as tk
from tkinter import messagebox
import copy
import random

BLOCK_WIDTH = 500
CANVAS_HEIGHT = 185


# THUẬT TOÁN
def first_fit(blocks, processes):
    alloc = [-1] * len(processes)
    for i, p in enumerate(processes):
        for j in range(len(blocks)):
            if blocks[j] >= p:
                alloc[i] = j
                blocks[j] -= p
                break
    return alloc, blocks

def best_fit(blocks, processes):
    alloc = [-1] * len(processes)
    for i, p in enumerate(processes):
        best = -1
        for j in range(len(blocks)):
            if blocks[j] >= p:
                if best == -1 or blocks[j] < blocks[best]:
                    best = j
        if best != -1:
            alloc[i] = best
            blocks[best] -= p
    return alloc, blocks

def worst_fit(blocks, processes):
    alloc = [-1] * len(processes)
    for i, p in enumerate(processes):
        worst = -1
        for j in range(len(blocks)):
            if blocks[j] >= p:
                if worst == -1 or blocks[j] > blocks[worst]:
                    worst = j
        if worst != -1:
            alloc[i] = worst
            blocks[worst] -= p
    return alloc, blocks

def next_fit(blocks, processes):
    alloc = [-1] * len(processes)
    pos = 0
    n = len(blocks)
    for i, p in enumerate(processes):
        start = pos
        while True:
            if blocks[pos] >= p:
                alloc[i] = pos
                blocks[pos] -= p
                break
            pos = (pos + 1) % n
            if pos == start:
                break
    return alloc, blocks

# TÍNH TOÁN
def fragmentation(original, remain):
    total = sum(original)
    free = sum(remain)
    used = total - free
    percent = round((free / total) * 100, 2) if total > 0 else 0
    return total, used, free, percent

def unallocated_processes(alloc):
    return [f"P{i+1}" for i, a in enumerate(alloc) if a == -1]

def calc_block_height(num_blocks):
    return max(40, 260 // num_blocks)


# VẼ BỘ NHỚ
def draw_memory(canvas, title, original_blocks, processes, alloc):
    canvas.delete("all")
    canvas.create_text(10, 10, anchor="w",
                       text=title, font=("Arial", 12, "bold"))

    block_height = calc_block_height(len(original_blocks))
    y = 40
    colors = {}

    for i, block_size in enumerate(original_blocks):
        x = 10
        canvas.create_rectangle(
            x, y,
            x + BLOCK_WIDTH, y + block_height,
            outline="black"
        )
        canvas.create_text(x + 5, y + 5,
                           anchor="nw", text=f"Block {i+1}")

        used_width = 0
        for p, a in enumerate(alloc):
            if a == i:
                if p not in colors:
                    colors[p] = "#%06x" % random.randint(0, 0xFFFFFF)
                w = processes[p] / block_size * BLOCK_WIDTH
                canvas.create_rectangle(
                    x + used_width, y + 25,
                    x + used_width + w,
                    y + block_height,
                    fill=colors[p]
                )
                canvas.create_text(
                    x + used_width + 5, y + 30,
                    anchor="nw", text=f"P{p+1}"
                )
                used_width += w

        if used_width < BLOCK_WIDTH:
            canvas.create_rectangle(
                x + used_width, y + 25,
                x + BLOCK_WIDTH, y + block_height,
                fill="#dddddd"
            )
            canvas.create_text(
                x + used_width + 5, y + 30,
                anchor="nw", text="Free"
            )

        y += block_height + 15

    canvas.config(scrollregion=canvas.bbox("all"))


# CHẠY 1 THUẬT TOÁN
def run_single(name):
    try:
        blocks = list(map(int, entry_blocks.get().split()))
        processes = list(map(int, entry_processes.get().split()))
    except:
        messagebox.showerror("Lỗi", "Nhập sai định dạng!")
        return

    algorithms = {
        "FIRST FIT": first_fit,
        "BEST FIT": best_fit,
        "WORST FIT": worst_fit,
        "NEXT FIT": next_fit
    }

    for c in canvases:
        c.delete("all")
    info_text.delete(1.0, tk.END)

    b = copy.deepcopy(blocks)
    alloc, remain = algorithms[name](b, processes)

    idx = list(algorithms.keys()).index(name)
    draw_memory(canvases[idx], name, blocks, processes, alloc)

    total, used, free, percent = fragmentation(blocks, remain)
    unalloc = unallocated_processes(alloc)

    info_text.insert(tk.END, f"=== {name} ===\n")
    info_text.insert(tk.END, f"Tổng bộ nhớ: {total}\n")
    info_text.insert(tk.END, f"Đã cấp phát: {used}\n")
    info_text.insert(tk.END, f"Còn trống: {free}\n")
    info_text.insert(tk.END, f"% Phân mảnh: {percent}%\n\n")

    if unalloc:
        info_text.insert(tk.END, "Tiến trình KHÔNG cấp phát:\n")
        info_text.insert(tk.END, ", ".join(unalloc))
    else:
        info_text.insert(tk.END, "Tất cả tiến trình được cấp phát")

# GIAO DIỆN
root = tk.Tk()
root.title("MÔ PHỎNG CẤP PHÁT BỘ NHỚ - HỆ ĐIỀU HÀNH")

# Khung nhập liệu
tk.Label(root, text="Kích thước Block bộ nhớ (VD: 100 500 200 300 600)").pack(pady=(5,0))
entry_blocks = tk.Entry(root, width=60)
entry_blocks.pack(padx=10)
entry_blocks.insert(0, "100 500 200 300 600") 

tk.Label(root, text="Kích thước Tiến trình (VD: 212 417 112 426)").pack(pady=(5,0))
entry_processes = tk.Entry(root, width=60)
entry_processes.pack(padx=10)
entry_processes.insert(0, "212 417 112 426") 

# Khung chứa 4 nút bấm
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

# 4 nút bấm riêng biệt để chạy 1 thuật toán
for name in ["FIRST FIT", "BEST FIT", "WORST FIT", "NEXT FIT"]:
    tk.Button(btn_frame, text=name,
              # Khi nhấn nút nào, chỉ chạy thuật toán đó
              command=lambda n=name: run_single(n), 
              width=12).pack(side=tk.LEFT, padx=5)

# Khung chứa 4 Canvas (Bố cục 2 hàng x 2 cột)
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=5)

canvases = []
names = ["FIRST FIT", "BEST FIT", "WORST FIT", "NEXT FIT"]

for i in range(4):
    container = tk.Frame(main_frame)
    row = i // 2
    col = i % 2
    container.grid(row=row, column=col, padx=10, pady=10, sticky="n")

    # Thêm Label tên thuật toán phía trên Canvas
    tk.Label(container, text=names[i], font=("Arial", 11, "bold")).pack(pady=(0, 2))

    scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Canvas 
    c = tk.Canvas(container, width=480, height=CANVAS_HEIGHT,
                  bg="white", yscrollcommand=scrollbar.set, relief=tk.SUNKEN, borderwidth=1)
    c.pack(side=tk.LEFT)

    scrollbar.config(command=c.yview)
    canvases.append(c)

# Khung Text hiển thị thông số thống kê
tk.Label(root, text="THÔNG SỐ THỐNG KÊ", font=("Arial", 10, "bold")).pack()
info_text = tk.Text(root, width=120, height=10)
info_text.pack(pady=10, padx=10)

root.mainloop()
