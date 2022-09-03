(set-logic LIA)
(synth-fun findSum ( (y1 Int) (y2 Int) )Int
    ((Start Int (y1 y2 5
                 (+ Start Start)
                 (- Start Start)
                 (ite StartBool Start1 Start1)
                ))
     (Start1 Int (
                 y1 y2 5
                 (+ Start1 Start1)
                 (- Start1 Start1)
                 (ite StartBool Start2 Start2)
                 ))
     (Start2 Int (
                 y1 y2 5
                 (+ Start2 Start2)
                 (- Start2 Start2)
                 (ite StartBool Start3 Start3)
                 ))
     (Start3 Int (
                 y1 y2 5
                 (+ Start3 Start3)
                 (- Start3 Start3)
                 ))
     (StartBool Bool (
                     (and StartBool StartBool)
                     (or StartBool StartBool)
                     (not StartBool)
                     (<=  Start3 Start3)
                     (=   Start3 Start3)
                     (>=  Start3 Start3)
                     ))
    )
)
