"""
Лабораторная работа 13: Паттерн Circuit Breaker
Предметная область: Филиалы и сотрудники

Локальный филиал запрашивает фонд оплаты у удалённого HR-сервиса.
Предохранитель после серии сбоев переходит в OPEN и временно
не пускает вызовы, чтобы не копить ошибки. По таймеру пробует
HALF-OPEN и либо закрывается, либо снова открывается.
"""

import time
import tkinter as tk
from tkinter import ttk


class RemoteHRService:
    """Имитация микросервиса расчёта фонда. Может быть недоступен."""

    def __init__(self):
        self.available = True

    def payroll(self, employees):
        if not self.available:
            raise ConnectionError("HR-сервис не ответил")
        return sum(emp["salary"] for emp in employees)


class CircuitOpenError(Exception):
    pass


class CircuitBreaker:
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, service, threshold=3, recovery_seconds=8):
        self.service = service
        self.threshold = threshold
        self.recovery_seconds = recovery_seconds
        self.state = self.CLOSED
        self.failures = 0
        self.opened_at = None

    def call(self, employees):
        now = time.time()
        if self.state == self.OPEN:
            if now - self.opened_at < self.recovery_seconds:
                left = self.recovery_seconds - (now - self.opened_at)
                raise CircuitOpenError("цепь разомкнута, повтор через {:.0f} с".format(left))
            self.state = self.HALF_OPEN
        try:
            result = self.service.payroll(employees)
        except ConnectionError:
            self._on_failure(now)
            raise
        self.failures = 0
        self.state = self.CLOSED
        self.opened_at = None
        return result

    def _on_failure(self, now):
        self.failures += 1
        if self.state == self.HALF_OPEN or self.failures >= self.threshold:
            self.state = self.OPEN
            self.opened_at = now


class BreakerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР13 — Circuit Breaker")
        self.root.geometry("860x560")
        self.employees = [
            {"name": "Иванов", "salary": 90000},
            {"name": "Петрова", "salary": 75000},
        ]
        self.service = RemoteHRService()
        self.breaker = CircuitBreaker(self.service)
        self._build()
        self._refresh()

    def _build(self):
        left = tk.Frame(self.root, padx=12, pady=10)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Предохранитель", font=("Arial", 13, "bold"),
                 fg="#2c3e50").pack(anchor=tk.W)
        tk.Label(left, text="Порог: 3 ошибки подряд\nПауза OPEN: 8 секунд",
                 justify=tk.LEFT, font=("Arial", 9)).pack(anchor=tk.W, pady=4)

        self.state_label = tk.Label(left, text="CLOSED", font=("Arial", 16, "bold"))
        self.state_label.pack(anchor=tk.W, pady=8)

        self.name = self._entry(left, "ФИО")
        self.salary = self._entry(left, "Зарплата")
        tk.Button(left, text="Добавить локально", command=self._add,
                  bg="#27ae60", fg="white").pack(fill=tk.X, pady=6)
        self.down = tk.BooleanVar(value=False)
        tk.Checkbutton(left, text="HR-сервис недоступен", variable=self.down,
                       command=self._toggle).pack(anchor=tk.W, pady=4)
        tk.Button(left, text="Запросить фонд у HR", command=self._call,
                  bg="#2980b9", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=8)

        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(right, columns=("name", "salary"), show="headings", height=6)
        self.tree.heading("name", text="Сотрудник")
        self.tree.heading("salary", text="Оклад")
        self.tree.pack(fill=tk.X)
        self.log = tk.Text(right, font=("Consolas", 10))
        self.log.pack(fill=tk.BOTH, expand=True, pady=8)
        self._write("Сервис доступен. Состояние цепи CLOSED.\n")

    def _entry(self, parent, label):
        tk.Label(parent, text=label).pack(anchor=tk.W, pady=(6, 0))
        entry = tk.Entry(parent, width=24)
        entry.pack(fill=tk.X)
        return entry

    def _toggle(self):
        self.service.available = not self.down.get()
        self._write("Доступность HR-сервиса: {}\n".format(
            "да" if self.service.available else "нет"))

    def _add(self):
        name = self.name.get().strip()
        try:
            salary = int(self.salary.get().strip())
        except ValueError:
            self._write("Зарплата должна быть числом.\n")
            return
        if not name:
            return
        self.employees.append({"name": name, "salary": salary})
        self._refresh()

    def _call(self):
        try:
            total = self.breaker.call(self.employees)
        except CircuitOpenError as error:
            self._write("[OPEN] вызов отклонён предохранителем: {}\n".format(error))
        except ConnectionError as error:
            self._write("[FAIL] {} | ошибки: {} | состояние {}\n".format(
                error, self.breaker.failures, self.breaker.state))
        else:
            self._write("[OK] фонд филиала {:,} руб. | состояние {}\n".format(
                total, self.breaker.state))
        self._paint_state()

    def _paint_state(self):
        colors = {"CLOSED": "#27ae60", "OPEN": "#c0392b", "HALF_OPEN": "#f39c12"}
        state = self.breaker.state
        self.state_label.config(text=state, fg=colors[state])

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for emp in self.employees:
            self.tree.insert("", tk.END, values=(emp["name"], "{:,}".format(emp["salary"])))

    def _write(self, text):
        self.log.insert(tk.END, text)
        self.log.see(tk.END)


def main():
    root = tk.Tk()
    BreakerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
