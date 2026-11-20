"""
Лабораторная работа 10: Паттерны Наблюдатель + Состояние
Предметная область: Филиалы и сотрудники

Состояние — поведение сотрудника зависит от статуса
(кандидат, испытательный срок, в штате, в отпуске, уволен).

Наблюдатель — расчётный отдел, журнал кадров и директор
подписываются на смену статуса и зарплаты.
"""

import tkinter as tk
from tkinter import ttk


class EmployeeSubject:
    """Издатель. Не знает конкретных подписчиков."""

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        self.state = None
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers = [item for item in self._observers if item is not observer]

    def notify(self, event, payload):
        for observer in self._observers:
            observer.update(self, event, payload)

    def change_state(self, state):
        self.state = state
        state.enter(self)
        self.notify("state", state.title)

    def set_salary(self, salary):
        self.salary = salary
        self.notify("salary", salary)

    def pay(self):
        return self.state.pay(self)

    def next_action(self, action):
        self.state.handle(self, action)


class EmployeeState:
    title = "состояние"

    def enter(self, employee):
        return None

    def pay(self, employee):
        raise RuntimeError("выплата недоступна")

    def handle(self, employee, action):
        employee.notify("rejected", "действие «{}» недоступно в статусе «{}»".format(
            action, self.title))


class CandidateState(EmployeeState):
    title = "кандидат"

    def pay(self, employee):
        employee.notify("rejected", "кандидат ещё не принят, выплата недоступна")
        return 0

    def handle(self, employee, action):
        if action == "принять":
            employee.change_state(ProbationState())
            return
        super().handle(employee, action)


class ProbationState(EmployeeState):
    title = "испытательный срок"

    def pay(self, employee):
        amount = int(employee.salary * 0.8)
        employee.notify("pay", amount)
        return amount

    def handle(self, employee, action):
        if action == "в штат":
            employee.change_state(ActiveState())
        elif action == "уволить":
            employee.change_state(DismissedState())
        else:
            super().handle(employee, action)


class ActiveState(EmployeeState):
    title = "в штате"

    def pay(self, employee):
        employee.notify("pay", employee.salary)
        return employee.salary

    def handle(self, employee, action):
        if action == "отпуск":
            employee.change_state(VacationState())
        elif action == "уволить":
            employee.change_state(DismissedState())
        else:
            super().handle(employee, action)


class VacationState(EmployeeState):
    title = "в отпуске"

    def pay(self, employee):
        amount = int(employee.salary * 0.5)
        employee.notify("pay", amount)
        return amount

    def handle(self, employee, action):
        if action == "выйти":
            employee.change_state(ActiveState())
        else:
            super().handle(employee, action)


class DismissedState(EmployeeState):
    title = "уволен"

    def pay(self, employee):
        employee.notify("rejected", "уволенному выплата не начисляется")
        return 0


class Observer:
    def __init__(self, name):
        self.name = name
        self.lines = []

    def update(self, employee, event, payload):
        if event == "state":
            text = "{}: {} теперь «{}»".format(self.name, employee.name, payload)
        elif event == "salary":
            text = "{}: зарплата {} = {:,}".format(self.name, employee.name, payload)
        elif event == "pay":
            text = "{}: начислено {} — {:,}".format(self.name, employee.name, payload)
        else:
            text = "{}: {}".format(self.name, payload)
        self.lines.append(text)


class StateObserverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР10 — Наблюдатель и Состояние")
        self.root.geometry("920x580")
        self.payroll = Observer("Расчётный отдел")
        self.journal = Observer("Журнал кадров")
        self.director = Observer("Директор")
        self.employee = None
        self._build()
        self._create_employee()

    def _build(self):
        left = tk.Frame(self.root, padx=12, pady=10)
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Состояние (State)", font=("Arial", 13, "bold"),
                 fg="#2c3e50").pack(anchor=tk.W)
        tk.Label(left, text="Одни и те же кнопки ведут себя по-разному",
                 font=("Arial", 9)).pack(anchor=tk.W)

        self.name = self._entry(left, "ФИО", "Иванов")
        self.salary = self._entry(left, "Оклад", "80000")
        tk.Button(left, text="Новый кандидат", command=self._create_employee,
                  bg="#34495e", fg="white").pack(fill=tk.X, pady=8)

        self.status = tk.Label(left, text="статус: —", font=("Arial", 12, "bold"), fg="#8e44ad")
        self.status.pack(anchor=tk.W, pady=6)

        for title, action, color in (
            ("Принять на испытательный", "принять", "#27ae60"),
            ("Перевести в штат", "в штат", "#2980b9"),
            ("Отправить в отпуск", "отпуск", "#f39c12"),
            ("Выйти из отпуска", "выйти", "#16a085"),
            ("Уволить", "уволить", "#c0392b"),
        ):
            tk.Button(left, text=title, bg=color, fg="white",
                      command=lambda a=action: self._action(a)).pack(fill=tk.X, pady=2)

        tk.Button(left, text="Начислить оплату по текущему статусу",
                  command=self._pay, bg="#8e44ad", fg="white").pack(fill=tk.X, pady=(10, 2))
        row = tk.Frame(left)
        row.pack(fill=tk.X, pady=6)
        self.new_salary = tk.Entry(row, width=12)
        self.new_salary.pack(side=tk.LEFT)
        tk.Button(row, text="Сменить оклад", command=self._salary).pack(side=tk.LEFT, padx=4)

        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(right, text="Наблюдатель (Observer)", font=("Arial", 13, "bold"),
                 fg="#8e44ad").pack(anchor=tk.W)
        tk.Label(right, text="Подписчики: расчётный отдел, журнал кадров, директор",
                 font=("Arial", 9)).pack(anchor=tk.W)
        self.log = tk.Text(right, font=("Consolas", 10))
        self.log.pack(fill=tk.BOTH, expand=True, pady=8)

        self.subs = tk.Listbox(right, height=4, font=("Arial", 10))
        for name in ("Расчётный отдел", "Журнал кадров", "Директор"):
            self.subs.insert(tk.END, "подписан: " + name)
        self.subs.pack(fill=tk.X)

    def _entry(self, parent, label, value):
        tk.Label(parent, text=label).pack(anchor=tk.W, pady=(8, 0))
        entry = tk.Entry(parent, width=28)
        entry.insert(0, value)
        entry.pack(fill=tk.X)
        return entry

    def _create_employee(self):
        name = self.name.get().strip() or "Сотрудник"
        try:
            salary = int(self.salary.get().strip())
        except ValueError:
            salary = 80000
        self.employee = EmployeeSubject(name, salary)
        for observer in (self.payroll, self.journal, self.director):
            self.employee.attach(observer)
        self.employee.change_state(CandidateState())
        self._flush()

    def _action(self, action):
        if self.employee is None:
            return
        self.employee.next_action(action)
        self._flush()

    def _pay(self):
        if self.employee is None:
            return
        self.employee.pay()
        self._flush()

    def _salary(self):
        if self.employee is None:
            return
        try:
            salary = int(self.new_salary.get().strip())
        except ValueError:
            return
        self.employee.set_salary(salary)
        self._flush()

    def _flush(self):
        self.status.config(text="статус: {} | оклад {:,}".format(
            self.employee.state.title, self.employee.salary))
        for observer in (self.payroll, self.journal, self.director):
            for line in observer.lines:
                self.log.insert(tk.END, line + "\n")
            observer.lines.clear()
        self.log.see(tk.END)


def main():
    root = tk.Tk()
    StateObserverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
