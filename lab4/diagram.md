@startuml
abstract class BranchComponent {
  +get_salary() int
  +get_name() String
}

class Employee {
  +String name
  +String position
  +int salary
  +get_salary() int
  +get_name() String
}

class Department {
  +String name
  -Component[] _children
  +add(Component)
  +remove(Component)
  +get_salary() int
  +get_name() String
}

class Branch {
  +String name
  -Component[] _children
  +add(Component)
  +get_salary() int
  +get_name() String
}

BranchComponent <|-- Employee
BranchComponent <|-- Department
BranchComponent <|-- Branch
Department o-- BranchComponent : _children
Branch o-- BranchComponent : _children
@enduml

@startuml
interface SalaryComponent {
  +get_salary() int
  +get_description() String
}

class BaseEmployee {
  +String name
  +int base_salary
  +get_salary() int
  +get_description() String
}

class SeniorityDecorator {
  -SalaryComponent component
  -int years
  +get_salary() int
  +get_description() String
}

class CategoryDecorator {
  -SalaryComponent component
  -int category_bonus
  +get_salary() int
  +get_description() String
}

class BonusDecorator {
  -SalaryComponent component
  -int bonus_amount
  +get_salary() int
  +get_description() String
}

SalaryComponent <|-- BaseEmployee
SalaryComponent <|-- SeniorityDecorator
SalaryComponent <|-- CategoryDecorator
SalaryComponent <|-- BonusDecorator
SeniorityDecorator --> SalaryComponent : wraps
CategoryDecorator --> SalaryComponent : wraps
BonusDecorator --> SalaryComponent : wraps
@enduml

@startuml
participant User
participant GUI
participant emp
participant Seniority
participant Category
participant Bonus

User -> GUI: Базовая 50000, стаж 5 лет, категория 10000, премия 15000
GUI -> emp: BaseEmployee("Иванов", 50000)
GUI -> Seniority: new SeniorityDecorator(emp, 5)
Seniority -> emp: get_salary() = 50000
Seniority -> Seniority: 50000 + 50000*5*0.10 = 75000
GUI -> Category: new CategoryDecorator(Seniority, 10000)
Category -> Seniority: get_salary() = 75000
Category -> Category: 75000 + 10000 = 85000
GUI -> Bonus: new BonusDecorator(Category, 15000)
Bonus -> Category: get_salary() = 85000
Bonus -> Bonus: 85000 + 15000 = 100000
Bonus -> GUI: 100000
GUI -> User: Итого: 100 000 руб.
@enduml
