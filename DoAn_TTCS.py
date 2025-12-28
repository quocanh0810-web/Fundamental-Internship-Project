import tkinter as tk
from tkinter import messagebox, ttk
import copy
import random
import time

# Cấu hình hằng số giao diện
BLOCK_WIDTH = 550
CANVAS_MIN_HEIGHT = 200

class MemoryAllocator:
    @staticmethod
    def first_fit(blocks, processes):
        alloc = [-1] * len(processes)
        for i, p in enumerate(processes):
            for j in range(len(blocks)):
                if blocks[j] >= p:
                    alloc[i] = j
                    blocks[j] -= p
                    break
        return alloc, blocks

    @staticmethod
    def best_fit(blocks, processes):
        alloc = [-1] * len(processes)
        for i, p in enumerate(processes):
            best_idx = -1
            for j in range(len(blocks)):
                if blocks[j] >= p:
                    if best_idx == -1 or blocks[j] < blocks[best_idx]:
                        best_idx = j
            if best_idx != -1:
                alloc[i] = best_idx
                blocks[best_idx] -= p
        return alloc, blocks

    @staticmethod
    def worst_fit(blocks, processes):
        alloc = [-1] * len(processes)
        for i, p in enumerate(processes):
            worst_idx = -1
            for j in range(len(blocks)):
                if blocks[j] >= p:
                    if worst_idx == -1 or blocks[j] > blocks[worst_idx]:
                        worst_idx = j
            if worst_idx != -1:
                alloc[i] = worst_idx
                blocks[worst_idx] -= p
        return alloc, blocks

    @staticmethod
    def next_fit(blocks, processes):
        alloc = [-1] * len(processes)
        n = len(blocks)
        pos = 0
        for i, p in enumerate(processes):
            start_pos = pos
            while True:
                if blocks[pos] >= p:
                    alloc[i] = pos
                    blocks[pos] -= p
                    break
                pos = (pos + 1) % n
                if pos == start_pos: break
        return alloc, blocks

class MemoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PHẦN MỀM MÔ PHỎNG QUẢN LÝ BỘ NHỚ - NTU 2025")
        self.root.geometry("1300x950")
        self.algorithms = ["FIRST FIT", "BEST FIT", "WORST FIT", "NEXT FIT"]
        self.setup_ui()

    def setup_ui(self):
        # 1. Khu vực nhập liệu
        input_frame = ttk.LabelFrame(self.root, text=" Cấu hình hệ thống ")
        input_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(input_frame, text="Danh sách Blocks (K):").grid(row=0, column=0, padx=10, pady=5)
        self.entry_blocks = tk.Entry(input_frame, width=80)
        self.entry_blocks.grid(row=0, column=1, padx=10)
        self.entry_blocks.insert(0, "100 500 200 300 600")

        tk.Label(input_frame, text="Danh sách Processes (K):").grid(row=1, column=0, padx=10, pady=5)
        self.entry_processes = tk.Entry(input_frame, width=80)
        self.entry_processes.grid(row=1, column=1, padx=10)
        self.entry_processes.insert(0, "212 417 112 426")

        # 2. Nút điều khiển
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        for name in self.algorithms:
            btn = tk.Button(btn_frame, text=name, width=12, bg="#3498db", fg="white", font=("Arial", 9, "bold"),
                            command=lambda n=name: self.run_simulation(n))
            btn.pack(side=tk.LEFT, padx=5)

        btn_compare = tk.Button(btn_frame, text="SO SÁNH TẤT CẢ", width=20, bg="#e67e22", fg="white", font=("Arial", 9, "bold"),
                               command=self.compare_all)
        btn_compare.pack(side=tk.LEFT, padx=20)

        # 3. Vùng hiển thị Canvas
        self.main_display = tk.Frame(self.root)
        self.main_display.pack(expand=True, fill="both", padx=20)
        
        self.canvases = []
        for i, name in enumerate(self.algorithms):
            frame = ttk.LabelFrame(self.main_display, text=f" {name} ")
            frame.grid(row=i//2, column=i%2, padx=5, pady=2, sticky="nsew")
            self.main_display.grid_columnconfigure(i%2, weight=1)
            self.main_display.grid_rowconfigure(i//2, weight=1)

            canvas = tk.Canvas(frame, bg="white", height=200)
            v_scroll = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="white")
            scrollable_frame.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=v_scroll.set)
            v_scroll.pack(side="right", fill="y")
            canvas.pack(side="left", expand=True, fill="both")
            self.canvases.append((canvas, scrollable_frame))

        # 4. Bảng thống kê so sánh 
        table_frame = ttk.LabelFrame(self.root, text=" Bảng so sánh hiệu năng chi tiết ")
        table_frame.pack(fill="x", padx=20, pady=10)

        columns = ("algo", "success", "used", "free", "largest", "ext_frag", "time")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
        
        self.tree.heading("algo", text="Thuật toán")
        self.tree.heading("success", text="Thành công")
        self.tree.heading("used", text="Đã dùng (K)")
        self.tree.heading("free", text="Còn trống (K)")
        self.tree.heading("largest", text="Lỗ lớn nhất")
        self.tree.heading("ext_frag", text="Phân mảnh ngoài")
        self.tree.heading("time", text="Thời gian (ms)")

        for col in columns:
            self.tree.column(col, width=150, anchor="center")
        
        self.tree.pack(fill="x", padx=5, pady=5)

    def draw_memory_pro(self, parent_frame, original_blocks, processes, alloc):
        for widget in parent_frame.winfo_children(): widget.destroy()
        colors = ["#e74c3c", "#f1c40f", "#2ecc71", "#9b59b6", "#1abc9c", "#e67e22"]
        
        for i, b_size in enumerate(original_blocks):
            f = tk.Frame(parent_frame, bg="white")
            f.pack(pady=5, padx=10, anchor="w")
            tk.Label(f, text=f"B{i+1}({b_size}K)", bg="white", font=("Arial", 8)).pack(side="left")
            b_frame = tk.Frame(f, width=BLOCK_WIDTH, height=35, bd=1, relief="solid", bg="#ecf0f1")
            b_frame.pack_propagate(False)
            b_frame.pack(side="left", padx=5)

            used_in_block = 0
            for p_idx, b_idx in enumerate(alloc):
                if b_idx == i:
                    p_size = processes[p_idx]
                    p_width = (p_size / b_size) * BLOCK_WIDTH
                    p_box = tk.Frame(b_frame, width=p_width, bg=random.choice(colors), bd=1, relief="raised")
                    p_box.pack(side="left", fill="y")
                    used_in_block += p_size
            
            if used_in_block < b_size:
                tk.Label(b_frame, text="FREE", fg="#7f8c8d", bg="#ecf0f1", font=("Arial", 7)).pack(side="left", expand=True)

    def run_simulation(self, name, clear_table=True):
        try:
            blocks = list(map(int, self.entry_blocks.get().split()))
            processes = list(map(int, self.entry_processes.get().split()))
        except:
            messagebox.showerror("Lỗi", "Dữ liệu không hợp lệ!")
            return None

        b_work = copy.deepcopy(blocks)
        start_t = time.perf_counter()
        
        if name == "FIRST FIT": alloc, remain = MemoryAllocator.first_fit(b_work, processes)
        elif name == "BEST FIT": alloc, remain = MemoryAllocator.best_fit(b_work, processes)
        elif name == "WORST FIT": alloc, remain = MemoryAllocator.worst_fit(b_work, processes)
        else: alloc, remain = MemoryAllocator.next_fit(b_work, processes)
        
        duration = (time.perf_counter() - start_t) * 1000

        # Cập nhật đồ họa
        idx = self.algorithms.index(name)
        self.draw_memory_pro(self.canvases[idx][1], blocks, processes, alloc)

        # Tính toán chỉ số
        total_mem = sum(blocks)
        total_free = sum(remain)
        total_used = total_mem - total_free
        success_count = len([a for a in alloc if a != -1])
        largest_free = max(remain) if remain else 0
        failed_ps = [processes[i] for i, a in enumerate(alloc) if a == -1]
        ext_frag_count = len([p for p in failed_ps if p <= total_free and p > largest_free])

        stats = (name, f"{success_count}/{len(processes)}", total_used, total_free, largest_free, ext_frag_count, f"{duration:.4f}")
        
        if clear_table:
            for item in self.tree.get_children(): self.tree.delete(item)
        self.tree.insert("", tk.END, values=stats)
        return stats

    def compare_all(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for algo in self.algorithms:
            self.run_simulation(algo, clear_table=False)

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryApp(root)
    root.mainloop()