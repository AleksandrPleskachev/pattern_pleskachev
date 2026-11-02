@startuml
interface DataSource {
  +get_employees() list
}

class CSVDataSource {
  -list data
  +get_employees() list
}

class JSONDataSource {
  -dict data
  +get_raw_data() dict
}

class JSONToCSVAdapter {
  -JSONDataSource json_source
  +get_employees() list
}

DataSource <|.. CSVDataSource
DataSource <|.. JSONToCSVAdapter
JSONToCSVAdapter --> JSONDataSource : wraps
@enduml

@startuml
class Employee {
  +String name
  +String department
  +String position
  +int base_salary
  +PayStrategy pay_strategy
  +get_salary() int
}

interface PayStrategy {
  +calculate_salary(base, extra) int
}

class MonthlyPay {
  +calculate_salary(base, extra) int
}

class HourlyPay {
  +calculate_salary(base, extra) int
}

class PieceworkPay {
  +calculate_salary(base, extra) int
}

Employee --> PayStrategy : uses
PayStrategy <|-- MonthlyPay
PayStrategy <|-- HourlyPay
PayStrategy <|-- PieceworkPay
@enduml

@startuml
participant User
participant GUI
participant Employee
participant "PayStrategy" as PS

User -> GUI: Заполняет форму, выбирает "Почасовая"
GUI -> Employee: Employee(name, dept, pos, 40, HourlyPay())
Employee -> Employee: pay_strategy = HourlyPay()
User -> GUI: Нажимает "Создать"
GUI -> Employee: emp.get_salary()
Employee -> PS: pay_strategy.calculate_salary(40)
PS -> PS: 40 * 500 = 20000
PS -> Employee: 20000
Employee -> GUI: 20000
GUI -> User: Зарплата: 20 000 руб.
@enduml
