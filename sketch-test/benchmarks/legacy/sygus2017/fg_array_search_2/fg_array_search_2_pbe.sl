(set-logic LIA)
(synth-fun findIdx ( (y1 Int) (y2 Int) (k1 Int)) Int 
	((Start Int (
				 0 1 2 y1 y2 k1
				 (+ Start Start)
                 (- Start Start)
				 (ite StartBool Start1 Start1)
	 			))
	 (Start1 Int (
				 0 1 2 y1 y2 k1
				 (+ Start1 Start1)
                 (- Start1 Start1)
				 (ite StartBool Start2 Start2)
	 			))
	 (Start2 Int (
				 0 1 2 y1 y2 k1
				 (+ Start2 Start2)
                 (- Start2 Start2)
				 (ite StartBool Start3 Start3)
	 			))
	 (Start3 Int (
				 0 1 2 y1 y2 k1
				 (+ Start3 Start3)
                 (- Start3 Start3)
	 			))
	 (StartBool Bool (
	 				  (and StartBool StartBool)
	 				  (or StartBool StartBool)
	 				  (not StartBool)
	 				  (<=  Start Start)
                      (=   Start Start)
                      (>=  Start Start)
	 			     ))
	)
)
