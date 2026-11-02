@startuml
class Employee {
  +String name
  +String department
  +int salary
  +String position
  +String emp_type
  +bonus() int
}

class Manager {
  +bonus() int
}

class Engineer {
  +bonus() int
}

class Accountant {
  +bonus() int
}

class Director {
  +bonus() int
}

class EmployeeFactory {
  +create(type, name, dept, salary) Employee
}

Employee <|-- Manager
Employee <|-- Engineer
Employee <|-- Accountant
Employee <|-- Director
EmployeeFactory ..> Employee : creates
@enduml

@startuml
class EmployeeTemplate {
  +String name
  +String department
  +int salary
  +String position
  +clone() EmployeeTemplate
  +with_name(name) EmployeeTemplate
  +with_department(dept) EmployeeTemplate
  +with_salary(sal) EmployeeTemplate
}

class GUI {
  +_proto_name()
  +_proto_dept()
  +_proto_chain()
}

EmployeeTemplate ..> EmployeeTemplate : clone()
GUI --> EmployeeTemplate : uses
@enduml

@startuml
participant User
participant GUI
participant "Base" as Base
participant "Cloned" as Cloned

User -> GUI: Нажимает with_name("Петров")
GUI -> Base: base.clone()
Base -> Cloned: deep copy
Cloned -> Cloned: name = "Петров"
Cloned -> GUI: cloned
GUI -> User: Новый объект создан
note right: Base не изменился!
@enduml
