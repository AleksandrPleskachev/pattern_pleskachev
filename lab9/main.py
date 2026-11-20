"""
Лабораторная работа 9: Паттерны Посредник + Снимок
Предметная область: Филиалы и сотрудники

Посредник — отделы не вызывают друг друга напрямую.
Перевод сотрудника и объявления идут через HRMediator.

Снимок — можно сохранить состав филиала и откатить его
без раскрытия внутреннего устройства списков отделов.
"""

import tkinter as tk
from tkinter import ttk


class Employee:
    def __init__(self, name, position, salary):
        self.name = name
        self.position = position
        self.salary = salary

    def clone(self):
        return Employee(self.name, self.position, self.salary)


class Department:
    """Коллега. Общается с другими отделами только через посредника."""

    def __init__(self, name, mediator):
        self.name = name
        self.mediator = mediator
        self.staff = []
        mediator.register(self)

    def add_local(self, employee):
        self.staff.append(employee)

    def remove_local(self, name):
        for i, emp in enumerate(self.staff):
            if emp.name == name:
                return self.staff.pop(i)
        return None

    def hire(self, employee):
        self.mediator.notify(self, "hire", employee)

    def transfer(self, employee_name, target_name):
        self.mediator.notify(self, "transfer", (employee_name, target_name))

    def announce(self, text):
        self.mediator.notify(self, "announce", text)


class HRMediator:
    """Посредник: вся связь между отделами проходит через него."""

    def __init__(self):
        self.departments = {}
        self.log = []

    def register(self, department):
        self.departments[department.name] = department

    def notify(self, sender, event, data):
        if event == "hire":
            sender.add_local(data)
            self._write("{} принял сотрудника {} через посредника".format(sender.name, data.name))
        elif event == "transfer":
            employee_name, target_name = data
            target = self.departments.get(target_name)
            if target is None:
                self._write("Отдел «{}» не найден".format(target_name))
                return
            employee = sender.remove_local(employee_name)
            if employee is None:
                self._write("{}: сотрудника {} нет".format(sender.name, employee_name))
                return
            target.add_local(employee)
            self._write("Посредник перевёл {} из «{}» в «{}»".format(
                employee.name, sender.name, target.name))
        elif event == "announce":
            receivers = [d.name for d in self.departments.values() if d is not sender]
            self._write("«{}» объявляет: {}. Получатели: {}".format(
                sender.name, data, ", ".join(receivers)))

    def _write(self, line):
        self.log.append(line)


class Memento:
    """Снимок. Хранит копию состояния, наружу её не отдаёт."""

    def __init__(self, state, label):
        self._state = state
        self.label = label

    def get_state(self):
        return self._state


class BranchOriginator:
    """Создатель снимков. Состояние — состав всех отделов."""

    def __init__(self, departments):
        self.departments = departments

    def save(self, label):
        state = {
            name: [emp.clone() for emp in dept.staff]
            for name, dept in self.departments.items()
        }
        return Memento(state, label)

    def restore(self, memento):
        state = memento.get_state()
        for name, dept in self.departments.items():
            dept.staff = [emp.clone() for emp in state.get(name, [])]


class Caretaker:
    def __init__(self):
        self.snapshots = []

    def push(self, memento):
        self.snapshots.append(memento)

    def pop(self):
        if not self.snapshots:
            return None
        return self.snapshots.pop()


class MediatorMementoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР9 — Посредник и Снимок")
        self.root.geometry("980x600")

        self.mediator = HRMediator()
        self.it = Department("IT", self.mediator)
        self.sales = Department("Продажи", self.mediator)
        self.hr = Department("Кадры", self.mediator)
        self.originator = BranchOriginator(self.mediator.departments)
        self.caretaker = Caretaker()
        self._seed()
        self._build()
        self._refresh()

    def _seed(self):
        self.it.add_local(Employee("Иванов", "Разработчик", 90000))
        self.sales.add_local(Employee("Петрова", "Менеджер", 70000))
        self.hr.add_local(Employee("Сидорова", "Кадровик", 65000))

    def _build(self):
        left = tk.Frame(self.root, padx=10, pady=8)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(left, text="Посредник (Mediator)", font=("Arial", 12, "bold"),
                 fg="#2c3e50").pack(anchor=tk.W)
        tk.Label(left, text="Отделы не знают друг о друге, связь только через HR",
                 font=("Arial", 9)).pack(anchor=tk.W)

        form = tk.Frame(left)
        form.pack(fill=tk.X, pady=8)
        tk.Label(form, text="ФИО").grid(row=0, column=0, sticky=tk.W)
        tk.Label(form, text="Должность").grid(row=0, column=1, sticky=tk.W)
        tk.Label(form, text="Зарплата").grid(row=0, column=2, sticky=tk.W)
        self.name = tk.Entry(form, width=16)
        self.position = tk.Entry(form, width=16)
        self.salary = tk.Entry(form, width=10)
        self.name.grid(row=1, column=0, padx=2)
        self.position.grid(row=1, column=1, padx=2)
        self.salary.grid(row=1, column=2, padx=2)

        self.source = ttk.Combobox(left, values=["IT", "Продажи", "Кадры"], state="readonly")
        self.source.set("IT")
        self.target = ttk.Combobox(left, values=["IT", "Продажи", "Кадры"], state="readonly")
        self.target.set("Продажи")
        tk.Label(left, text="Откуда / куда").pack(anchor=tk.W)
        row = tk.Frame(left)
        row.pack(fill=tk.X, pady=4)
        self.source.pack(in_=row, side=tk.LEFT, padx=2)
        self.target.pack(in_=row, side=tk.LEFT, padx=2)

        buttons = tk.Frame(left)
        buttons.pack(fill=tk.X, pady=6)
        tk.Button(buttons, text="Принять в отдел", command=self._hire,
                  bg="#27ae60", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(buttons, text="Перевести", command=self._transfer,
                  bg="#2980b9", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(buttons, text="Объявление", command=self._announce,
                  bg="#8e44ad", fg="white").pack(side=tk.LEFT, padx=2)

        self.tree = ttk.Treeview(left, columns=("dept", "name", "pos", "salary"),
                                  show="headings", height=12)
        for col, title, width in (
            ("dept", "Отдел", 90),
            ("name", "ФИО", 120),
            ("pos", "Должность", 120),
            ("salary", "Зарплата", 90),
        ):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=6)

        right = tk.Frame(self.root, padx=10, pady=8)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(right, text="Снимок (Memento)", font=("Arial", 12, "bold"),
                 fg="#8e44ad").pack(anchor=tk.W)
        snap_btns = tk.Frame(right)
        snap_btns.pack(fill=tk.X, pady=6)
        tk.Button(snap_btns, text="Сохранить снимок", command=self._save,
                  bg="#16a085", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(snap_btns, text="Откатить последний", command=self._restore,
                  bg="#c0392b", fg="white").pack(side=tk.LEFT, padx=2)

        self.snap_list = tk.Listbox(right, height=6, font=("Consolas", 10))
        self.snap_list.pack(fill=tk.X, pady=4)
        tk.Label(right, text="Журнал посредника", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.log = tk.Text(right, font=("Consolas", 10), height=16)
        self.log.pack(fill=tk.BOTH, expand=True)

    def _selected_department(self, combo):
        return self.mediator.departments[combo.get()]

    def _hire(self):
        name = self.name.get().strip()
        position = self.position.get().strip() or "Сотрудник"
        try:
            salary = int(self.salary.get().strip())
        except ValueError:
            self._flush_log("Зарплата должна быть числом")
            return
        if not name:
            return
        dept = self._selected_department(self.source)
        dept.hire(Employee(name, position, salary))
        self._flush_log()
        self._refresh()

    def _transfer(self):
        selected = self.tree.selection()
        if not selected:
            self._flush_log("Выберите сотрудника в таблице")
            return
        values = self.tree.item(selected[0])["values"]
        source_name, employee_name = values[0], values[1]
        target_name = self.target.get()
        if source_name == target_name:
            self._flush_log("Отдел назначения совпадает с текущим")
            return
        self.mediator.departments[source_name].transfer(employee_name, target_name)
        self._flush_log()
        self._refresh()

    def _announce(self):
        self._selected_department(self.source).announce("планёрка в 10:00")
        self._flush_log()

    def _save(self):
        label = "снимок {}".format(len(self.caretaker.snapshots) + 1)
        self.caretaker.push(self.originator.save(label))
        self.snap_list.insert(tk.END, label)
        self._flush_log("Снимок «{}» сохранён".format(label))

    def _restore(self):
        memento = self.caretaker.pop()
        if memento is None:
            self._flush_log("Снимков нет")
            return
        self.originator.restore(memento)
        self.snap_list.delete(tk.END)
        self._flush_log("Восстановлено состояние до «{}»".format(memento.label))
        self._refresh()

    def _refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for dept in (self.it, self.sales, self.hr):
            for emp in dept.staff:
                self.tree.insert("", tk.END, values=(
                    dept.name, emp.name, emp.position, "{:,}".format(emp.salary)))

    def _flush_log(self, extra=None):
        if extra:
            self.mediator.log.append(extra)
        for line in self.mediator.log:
            self.log.insert(tk.END, line + "\n")
        self.mediator.log.clear()
        self.log.see(tk.END)


def main():
    root = tk.Tk()
    MediatorMementoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
