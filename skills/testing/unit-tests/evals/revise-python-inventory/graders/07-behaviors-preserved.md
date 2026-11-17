---
type: llm
focus: trace
weight: 1
---

Every behavior the original file checked is still covered: add accumulates, add rejects non-positive qty, reserve reduces available, commit removes stock, over-reserve raises OutOfStock, holds expire and then commit raises UnknownReservation, release restores stock and releasing twice raises UnknownReservation
