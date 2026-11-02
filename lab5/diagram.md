@startuml
class PayrollFacade {
  -TaxCalculator tax
  -BonusCalculator bonus
  -DeductionCalculator deduction
  +calculate_payroll(base, bonus%, children) dict
  +get_summary(result) String
}

class TaxCalculator {
  +calculate_income_tax(salary) int
  +calculate_social_tax(salary) int
}

class BonusCalculator {
  +calculate_bonus(salary, percent) int
}

class DeductionCalculator {
  +calculate_deductions(salary, has_children) int
}

PayrollFacade --> TaxCalculator : uses
PayrollFacade --> BonusCalculator : uses
PayrollFacade --> DeductionCalculator : uses
@enduml

@startuml
class DepartmentFlyweight {
  +String name
  +int budget
  +String manager
}

class DepartmentFactory {
  -Map<String, DepartmentFlyweight> _departments
  +get_department(name, budget, manager) DepartmentFlyweight
  +get_stats() int
}

class Employee {
  +String name
  +DepartmentFlyweight department
  +int salary
}

DepartmentFactory --> DepartmentFlyweight : creates/caches
Employee o-- DepartmentFlyweight : shares (flyweight)
@enduml

@startuml
participant User
participant GUI
participant Facade
participant Tax
participant Bonus
participant Deduction

User -> GUI: Зарплата 80000, премия 10%, есть дети
GUI -> Facade: calculate_payroll(80000, 10, true)
Facade -> Tax: calculate_income_tax(80000)
Tax -> Facade: 10400 (НДФЛ 13%)
Facade -> Tax: calculate_social_tax(80000)
Tax -> Facade: 24000 (страховые 30%)
Facade -> Bonus: calculate_bonus(80000, 10)
Bonus -> Facade: 8000
Facade -> Deduction: calculate_deductions(80000, true)
Deduction -> Facade: 3200 (вычет 4%)
Facade -> Facade: total = 80000 + 8000 - 10400 - 24000 - 3200 = 50400
Facade -> GUI: result
GUI -> User: Итого: 50 400 руб.
@enduml
