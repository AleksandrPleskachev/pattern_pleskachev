@startuml
interface Command {
  +execute()
  +undo()
}

class AddCommand {
  -EmployeeManager manager
  -String name
  -String department
  -int salary
  +execute()
  +undo()
}

class RemoveCommand {
  -EmployeeManager manager
  -String name
  -Employee employee
  +execute()
  +undo()
}

class ChangeSalaryCommand {
  -EmployeeManager manager
  -String name
  -int new_salary
  -int old_salary
  +execute()
  +undo()
}

class CommandHistory {
  -Command[] _history
  -Command[] _redo_stack
  +execute(Command)
  +undo()
  +redo()
}

class EmployeeManager {
  -Employee[] employees
  +add_employee(...)
  +remove_employee(name)
  +change_salary(name, new)
}

Command <|-- AddCommand
Command <|-- RemoveCommand
Command <|-- ChangeSalaryCommand
CommandHistory --> Command : stores
AddCommand --> EmployeeManager : executes on
RemoveCommand --> EmployeeManager : executes on
ChangeSalaryCommand --> EmployeeManager : executes on
@enduml

@startuml
interface EmployeeIterator {
  +first()
  +next()
  +is_done() boolean
  +current() Employee
}

class AlphabeticalIterator {
  -Employee[] _sorted
  -int _index
  +first()
  +next()
  +is_done() boolean
  +current() Employee
}

class SalaryIterator {
  -Employee[] _sorted
  -int _index
  +first()
  +next()
  +is_done() boolean
  +current() Employee
}

class DepartmentIterator {
  -Employee[] _sorted
  -int _index
  +first()
  +next()
  +is_done() boolean
  +current() Employee
}

class EmployeesAggregate {
  -Employee[] employees
  +create_alphabetical_iterator()
  +create_salary_iterator()
  +create_department_iterator()
}

EmployeeIterator <|-- AlphabeticalIterator
EmployeeIterator <|-- SalaryIterator
EmployeeIterator <|-- DepartmentIterator
EmployeesAggregate --> EmployeeIterator : creates
@enduml

@startuml
participant User
participant GUI
participant History
participant AddCmd
participant Manager

User -> GUI: Вводит данные, нажимает "Добавить"
GUI -> AddCmd: new AddCommand(manager, "Иванов", 80000)
GUI -> History: history.execute(AddCmd)
History -> AddCmd: AddCmd.execute()
AddCmd -> Manager: manager.add_employee(...)
Manager -> Manager: employees.append(emp)
Manager -> AddCmd: emp
AddCmd -> History: history.append(AddCmd)
History -> GUI: OK
GUI -> User: Сотрудник добавлен

User -> GUI: Нажимает "Undo"
GUI -> History: history.undo()
History -> History: cmd = history.pop()
History -> AddCmd: AddCmd.undo()
AddCmd -> Manager: manager.remove_employee("Иванов")
Manager -> Manager: employees.remove(emp)
Manager -> AddCmd: emp
AddCmd -> History: redo_stack.append(AddCmd)
History -> GUI: Отменено
GUI -> User: Сотрудник удалён
@enduml
