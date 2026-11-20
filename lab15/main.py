"""
Лабораторная работа 15: Паттерн Producer-Consumer
Предметная область: Филиалы и сотрудники

Производитель складывает задания на расчёт премии в очередь.
Два постоянных работника забирают задания и считают результат.
Число потоков фиксировано: это небольшой пул, новые потоки
на каждое задание не создаются.
"""

import queue
import threading
import time
import tkinter as tk
from tkinter import ttk


class BonusTask:
    def __init__(self, name, department, salary, percent):
        self.name = name
        self.department = department
        self.salary = salary
        self.percent = percent


class WorkerPool:
    """Фиксированные потребители. Очередь — буфер между производителем и ими."""

    def __init__(self, size, results, log_queue):
        self.tasks = queue.Queue(maxsize=10)
        self.results = results
        self.log_queue = log_queue
        self._stop = threading.Event()
        self.workers = []
        for index in range(size):
            thread = threading.Thread(target=self._consume, args=(index + 1,), daemon=True)
            thread.start()
            self.workers.append(thread)

    def produce(self, task):
        self.log_queue.put("[Producer] в очередь: {} (+{}%)".format(task.name, task.percent))
        self.tasks.put(task)

    def _consume(self, worker_id):
        while not self._stop.is_set():
            try:
                task = self.tasks.get(timeout=0.2)
            except queue.Empty:
                continue
            self.log_queue.put("[Worker-{}] взял {}".format(worker_id, task.name))
            time.sleep(0.8)
            bonus = int(task.salary * task.percent / 100)
            self.results.put({
                "worker": worker_id,
                "name": task.name,
                "department": task.department,
                "salary": task.salary,
                "bonus": bonus,
                "total": task.salary + bonus,
            })
            self.log_queue.put("[Worker-{}] готов {}: премия {:,}".format(
                worker_id, task.name, bonus))
            self.tasks.task_done()

    def stop(self):
        self._stop.set()


class ProducerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР15 — Producer-Consumer")
        self.root.geometry("900x560")
        self.log_queue = queue.Queue()
        self.results = queue.Queue()
        self.pool = WorkerPool(2, self.results, self.log_queue)
        self._build()
        self._poll()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _build(self):
        left = tk.Frame(self.root, padx=12, pady=10)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Производитель", font=("Arial", 13, "bold"),
                 fg="#2c3e50").pack(anchor=tk.W)
        tk.Label(left, text="2 потока-потребителя уже запущены",
                 font=("Arial", 9)).pack(anchor=tk.W, pady=(0, 6))
        self.name = self._entry(left, "ФИО", "Иванов")
        self.dept = self._entry(left, "Отдел", "IT")
        self.salary = self._entry(left, "Оклад", "80000")
        self.percent = self._entry(left, "Премия, %", "20")
        tk.Button(left, text="Поставить одно задание", command=self._one,
                  bg="#2980b9", fg="white").pack(fill=tk.X, pady=6)
        tk.Button(left, text="Поставить 4 задания", command=self._batch,
                  bg="#8e44ad", fg="white").pack(fill=tk.X, pady=2)
        self.depth = tk.Label(left, text="в очереди: 0", font=("Arial", 11, "bold"))
        self.depth.pack(anchor=tk.W, pady=10)

        right = tk.Frame(self.root, padx=8, pady=8)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(
            right, columns=("worker", "name", "dept", "bonus", "total"),
            show="headings", height=8)
        for col, title in (
            ("worker", "Поток"), ("name", "ФИО"), ("dept", "Отдел"),
            ("bonus", "Премия"), ("total", "Итого"),
        ):
            self.tree.heading(col, text=title)
        self.tree.pack(fill=tk.X)
        self.log = tk.Text(right, font=("Consolas", 10))
        self.log.pack(fill=tk.BOTH, expand=True, pady=8)
        self.log.insert(tk.END, "Пул из 2 потребителей ждёт очередь.\n")

    def _entry(self, parent, label, value):
        tk.Label(parent, text=label).pack(anchor=tk.W)
        entry = tk.Entry(parent, width=24)
        entry.insert(0, value)
        entry.pack(fill=tk.X, pady=(0, 4))
        return entry

    def _task(self, name, percent_shift=0):
        try:
            salary = int(self.salary.get().strip())
            percent = int(self.percent.get().strip()) + percent_shift
        except ValueError:
            self.log.insert(tk.END, "Оклад и процент должны быть числами.\n")
            return None
        department = self.dept.get().strip() or "отдел"
        if not name:
            return None
        return BonusTask(name, department, salary, percent)

    def _one(self):
        task = self._task(self.name.get().strip())
        if task:
            self.pool.produce(task)

    def _batch(self):
        base = self.name.get().strip() or "Сотрудник"
        for index in range(4):
            task = self._task("{}-{}".format(base, index + 1), index)
            if task:
                self.pool.produce(task)

    def _poll(self):
        while True:
            try:
                line = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self.log.insert(tk.END, line + "\n")
            self.log.see(tk.END)
        while True:
            try:
                result = self.results.get_nowait()
            except queue.Empty:
                break
            self.tree.insert("", tk.END, values=(
                "Worker-{}".format(result["worker"]),
                result["name"],
                result["department"],
                "{:,}".format(result["bonus"]),
                "{:,}".format(result["total"]),
            ))
        self.depth.config(text="в очереди: {}".format(self.pool.tasks.qsize()))
        self.root.after(200, self._poll)

    def _close(self):
        self.pool.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    ProducerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
