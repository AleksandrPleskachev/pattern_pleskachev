@startuml
participant GUI as Producer
queue TaskQueue
participant "Worker-1" as W1
participant "Worker-2" as W2
queue ResultQueue

Producer -> TaskQueue: put(BonusTask)
W1 -> TaskQueue: get()
W2 -> TaskQueue: get()
W1 -> ResultQueue: премия
W2 -> ResultQueue: премия
GUI -> ResultQueue: after() забирает результат
@enduml
