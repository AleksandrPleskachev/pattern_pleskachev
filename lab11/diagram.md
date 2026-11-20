@startuml
class PayStrategy {
  +calculate(employee)
}
class FixedStrategy
class HourlyStrategy
class BonusStrategy
class PayrollContext {
  -strategy
  +set_strategy()
  +amount()
}
PayStrategy <|-- FixedStrategy
PayStrategy <|-- HourlyStrategy
PayStrategy <|-- BonusStrategy
PayrollContext o--> PayStrategy

class ReportTemplate {
  +generate()
  +header()
  +body()
  +footer()
}
class TextReport
class HtmlReport
ReportTemplate <|-- TextReport
ReportTemplate <|-- HtmlReport
@enduml
