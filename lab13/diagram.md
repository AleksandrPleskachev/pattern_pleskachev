@startuml
class RemoteHRService {
  +available
  +payroll(employees)
}
class CircuitBreaker {
  +state
  +failures
  +call(employees)
}
class BreakerApp

CircuitBreaker --> RemoteHRService
BreakerApp --> CircuitBreaker

state CLOSED
state OPEN
state HALF_OPEN
CLOSED --> OPEN : 3 ошибки
OPEN --> HALF_OPEN : прошло 8 с
HALF_OPEN --> CLOSED : успех
HALF_OPEN --> OPEN : ошибка
@enduml
