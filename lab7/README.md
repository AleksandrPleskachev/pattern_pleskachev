# Лабораторная работа 7: Паттерны Команда + Итератор

## Предметная область
**Филиалы и сотрудники** — операции с отменой и обход коллекции.

## Паттерн 1: Команда (Command)

### Назначение
Оборачивает операцию как объект, позволяя параметризовать клиенты, ставить в очередь и отменять операции.

### Проблема
Операции (добавить, удалить, изменить зарплату) напрямую вызывают методы менеджера. Нет возможности отменить действие.

### Решение
Каждая операция — объект с `execute()` и `undo()`:
```python
# Создание команды
cmd = AddCommand(manager, "Иванов", "IT", "Разработчик", 80000)

# Выполнение через историю
history.execute(cmd)

# Отмена
history.undo()  # вызывает cmd.undo() — удаляет сотрудника

# Повтор
history.redo()  # вызывает cmd.execute() — добавляет снова
```

### Участники
| Участник | Роль | В коде |
|---|---|---|
| Command | Интерфейс команды | `Command.execute()`, `Command.undo()` |
| ConcreteCommand | Конкретная команда | `AddCommand`, `RemoveCommand`, `ChangeSalaryCommand` |
| Invoker | Вызыватель | `CommandHistory` — хранит историю, управляет undo/redo |
| Receiver | Получатель | `EmployeeManager` — выполняет реальные операции |

### Команды
| Команда | execute() | undo() |
|---|---|---|
| `AddCommand` | `manager.add_employee(...)` | `manager.remove_employee(name)` |
| `RemoveCommand` | `manager.remove_employee(name)` | `manager.add_employee(...)` |
| `ChangeSalaryCommand` | `manager.change_salary(name, new)` | `manager.change_salary(name, old)` |

## Паттерн 2: Итератор (Iterator)

### Назначение
Предоставляет способ последовательного доступа к элементам коллекции без раскрытия её структуры.

### Проблема
Нужно обходить список сотрудников по-разному: по алфавиту, по зарплате, по отделу. Клиент не должен знать о внутренней структуре.

### Решение
Каждый итератор реализует один интерфейс:
```python
it = agg.create_salary_iterator()  # по убыванию зарплаты
it.first()
while not it.is_done():
    emp = it.current()  # текущий сотрудник
    it.next()           # следующий
```

### Участники
| Участник | Роль | В коде |
|---|---|---|
| Iterator | Интерфейс итератора | `EmployeeIterator.first()`, `next()`, `is_done()`, `current()` |
| ConcreteIterator | Конкретный итератор | `AlphabeticalIterator`, `SalaryIterator`, `DepartmentIterator` |
| Aggregate | Агрегат | `EmployeesAggregate` — создаёт итераторы |

### Типы итераторов
| Итератор | Порядок |
|---|---|
| `AlphabeticalIterator` | По алфавиту (A→Я) |
| `SalaryIterator` | По зарплате (убывание) |
| `DepartmentIterator` | По отделам (A→Я) |

### Как запустить
```bash
python lab7/main.py
```

### Что видно в GUI
- **Команда (слева):** добавляешь → меняешь → удаляешь → Undo/Redo отменяет и повторяет. В логе видны все команды
- **Итератор (справа):** нажимаешь «По алфавиту» / «По зарплате» / «По отделу» → в логе видишь порядок обхода
