; max3.sl
; Synthesize the maximum of 3 integers, from a purely declarative spec
(set-logic LIA)
(synth-fun max3 ((x Int) (y Int) (z Int)) Int
    ((Start Int (
                 x y z 0 1 2 3 4 5 6 7 8
                 (+ Start Start)
                 (- Start Start)
                 (ite StartBool Start1 Start1)
                ))
     (Start1 Int (
                 x y z 0 1 2 3 4 5 6 7 8
                 (+ Start1 Start1)
                 (- Start1 Start1)
                 (ite StartBool Start2 Start2)
                 ))
     (Start2 Int (
                 x y z 0 1 2 3 4 5 6 7 8
                 (+ Start2 Start2)
                 (- Start2 Start2)
                 (ite StartBool FinalStart FinalStart)
                 ))
     (FinalStart Int (
                 x y z 0 1 2 3 4 5 6 7 8
                 (+ FinalStart FinalStart)
                 (- FinalStart FinalStart)
                 ))
     (StartBool Bool (
                     (and StartBool StartBool)
                     (or StartBool StartBool)
                     (not StartBool)
                     (<=  FinalStart FinalStart)
                     (=   FinalStart FinalStart)
                     (>=  FinalStart FinalStart)
                     ))
    )
)
