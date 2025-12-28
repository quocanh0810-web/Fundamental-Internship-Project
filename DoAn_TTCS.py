import tkinter as tk
from tkinter import messagebox, ttk
import copy
import random
import time

BLOCK_WIDTH = 550
CANVAS_MIN_HEIGHT = 250

class MemoryAllocator:
    """Lớp chứa các thuật toán cấp phát bộ nhớ"""
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
    def next_fit(blocks, processes, last_pos=0):
        alloc = [-1] * len(processes)
        n = len(blocks)
        pos = last_pos
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
        self.root.geometry("1200x900")
        
        self.setup_ui()

    def setup_ui(self):
        #. Khu vực nhập liệu
        input_frame = ttk.LabelFrame(self.root, text=" Cấu hình hệ thống ")
        input_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(input_frame, text="Danh sách Blocks (K):").grid(row=0, column=0, padx=10, pady=5)
        self.entry_blocks = tk.Entry(input_frame, width=80)
        self.entry_blocks.grid(row=0, column=1, padx=10)
        self.entry_blocks.insert(0, "100 500 200 300 600")

        tk.Label(input_frame, text="Danh sách Processes (K):").grid(row=1, column=0, padx=10, pady=5)
        self.entry_processes = tk.Entry(input_frame, width=80)
        self.entry_processes.grid(row=1, column=1, padx=10)
        self.entry_processes.insert(0, "212 417 112 426")

        #. Nút điều khiển
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        self.algorithms = ["FIRST FIT", "BEST FIT", "WORST FIT", "NEXT FIT"]
        for name in self.algorithms:
            btn = tk.Button(btn_frame, text=name, width=15, height=2, 
                            command=lambda n=name: self.run_simulation(n),
                            bg="#3498db", fg="white", font=("Arial", 9, "bold"))
            btn.pack(side=tk.LEFT, padx=10)

        #. Vùng hiển thị Canvas có Scrollbar
        self.main_display = tk.Frame(self.root)
        self.main_display.pack(expand=True, fill="both", padx=20)
        
        self.canvases = []
        for i, name in enumerate(self.algorithms):
            frame = ttk.LabelFrame(self.main_display, text=f" {name} ")
            frame.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="nsew")
            self.main_display.grid_columnconfigure(i%2, weight=1)
            self.main_display.grid_rowconfigure(i//2, weight=1)

            canvas = tk.Canvas(frame, bg="white", highlightthickness=0)
            v_scroll = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            h_scroll = tk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
            
            scrollable_frame = tk.Frame(canvas, bg="white")
            scrollable_frame.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
            
            v_scroll.pack(side="right", fill="y")
            h_scroll.pack(side="bottom", fill="x")
            canvas.pack(side="left", expand=True, fill="both")
            
            self.canvases.append((canvas, scrollable_frame))

        #. Bảng thống kê số liệu
        stat_frame = ttk.LabelFrame(self.root, text=" Báo cáo phân tích hiệu năng ")
        stat_frame.pack(fill="both", padx=20, pady=10)
        self.info_text = tk.Text(stat_frame, height=10, font=("Consolas", 10), bg="#2c3e50", fg="#ecf0f1")
        self.info_text.pack(fill="both", padx=5, pady=5)

    def draw_memory_pro(self, parent_frame, title, original_blocks, processes, alloc):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        colors = ["#e74c3c", "#f1c40f", "#2ecc71", "#9b59b6", "#1abc9c", "#e67e22"]
        
        for i, b_size in enumerate(original_blocks):
            f = tk.Frame(parent_frame, bg="white")
            f.pack(pady=10, padx=10, anchor="w")
            
            tk.Label(f, text=f"Block {i+1} ({b_size}K)", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
            
            # Khung biểu diễn bộ nhớ
            b_frame = tk.Frame(f, width=BLOCK_WIDTH, height=50, bd=1, relief="solid", bg="#ecf0f1")
            b_frame.pack_propagate(False)
            b_frame.pack()

            used_in_block = 0
            for p_idx, b_idx in enumerate(alloc):
                if b_idx == i:
                    p_size = processes[p_idx]
                    p_width = (p_size / b_size) * BLOCK_WIDTH
                    p_box = tk.Frame(b_frame, width=p_width, bg=random.choice(colors), bd=1, relief="raised")
                    p_box.pack(side="left", fill="y")
                    tk.Label(p_box, text=f"P{p_idx+1}\n{p_size}K", fg="white", font=("Arial", 7), bg=p_box["bg"]).place(relx=0.5, rely=0.5, anchor="center")
                    used_in_block += p_size
            
            if used_in_block < b_size:
                tk.Label(b_frame, text="FREE", fg="#7f8c8d", bg="#ecf0f1").pack(side="left", expand=True)

    def run_simulation(self, name):
        try:
            blocks = list(map(int, self.entry_blocks.get().split()))
            processes = list(map(int, self.entry_processes.get().split()))
        except:
            messagebox.showerror("Lỗi", "Định dạng dữ liệu không hợp lệ!")
            return

        # Tính toán
        b_work = copy.deepcopy(blocks)
        start_t = time.perf_counter()
        
        if name == "FIRST FIT": alloc, remain = MemoryAllocator.first_fit(b_work, processes)
        elif name == "BEST FIT": alloc, remain = MemoryAllocator.best_fit(b_work, processes)
        elif name == "WORST FIT": alloc, remain = MemoryAllocator.worst_fit(b_work, processes)
        else: alloc, remain = MemoryAllocator.next_fit(b_work, processes)
        
        duration = (time.perf_counter() - start_t) * 1000

        # Vẽ
        idx = self.algorithms.index(name)
        self.draw_memory_pro(self.canvases[idx][1], name, blocks, processes, alloc)

        # Thống kê chuyên sâu
        total_free = sum(remain)
        largest_free = max(remain) if remain else 0
        failed_ps = [processes[i] for i, a in enumerate(alloc) if a == -1]
        
        # Chỉ số phân mảnh ngoài (External Fragmentation)
        ext_frag_procs = [p for p in failed_ps if p <= total_free and p > largest_free]
        
        self.info_text.delete(1.0, tk.END)
        report = f"--- BÁO CÁO PHÂN TÍCH: {name} ---\n"
        report += f"1. Tỷ lệ bộ nhớ trống: {round((total_free/sum(blocks))*100, 2)}%\n"
        report += f"2. Lỗ trống lớn nhất (Largest Free Block): {largest_free}K\n"
        report += f"3. Số tiến trình thất bại do PHÂN MẢNH NGOÀI: {len(ext_frag_procs)}\n"
        report += f"4. Thời gian chạy thuật toán: {duration:.4f} ms\n"
        report += "-"*50 + "\n"
        
        if ext_frag_procs:
            report += f"NHẬN XÉT: Hệ thống còn {total_free}K trống nhưng không thể cấp phát cho các tiến trình {ext_frag_procs} \n"
            report += "do các lỗ trống bị chia cắt (Phân mảnh ngoài).\n"
        elif failed_ps:
            report += "NHẬN XÉT: Tiến trình thất bại do cạn kiệt tổng bộ nhớ thực tế.\n"
        else:
            report += "NHẬN XÉT: Thuật toán hoạt động tối ưu, không có phân mảnh ngoài với bộ test này.\n"

        self.info_text.insert(tk.END, report)

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryApp(root)
    root.mainloop()