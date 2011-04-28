x [y]
y [z]
z [w]
w [x]
god [immortal]
goddess [immortal]
immortal [beings]
titan [immortal] 
monster [mortal] 
centaurs [mortal] 
giants [mortal]
beings []
problem [] 
geometric-figure [] 
mortal [beings]
giants [human]
human [mortal]


Transform-to  := "<> transformed to <> polynomially.".
NP-Complete   := "<> is an NP-complete problem.".
*   := "<problem> transformed to <problem> 
-   polynomially.".
Polygon	:= "<geometric-figure> has <no-of-edge:n> edges.".
"   ?< ( \no-of-edge < 0 )
-   : warn "Number of edges cannot be negative"
-   ?: ( \no-of-edge > 10 ) 
-   : warn "More than 10 edges are not considered"
-   ?: ( \no-of-edge = 1 )
-   : warn "Circle or straight line ?"
-   : satisfied >?.
Instance   := "<problem> instance is <:s>.".
Question   := "<problem> question is <:s>.".
Membership   := "<problem> belons to <set:w>.".
Transform-to   := "<problem> transformed to <problem> polynomially.".
NP-Complete   := "<problem> is an NP-complete problem.". 
problem   ?< ( \*Instance < 1 ) 
-   : warn "Problem must have an instance."
-   ?: ( \Instance > 1 ) 
-   : warn "Problem has more than one instance." >?.

"   ?< ( \*Question < 1 )
-   : warn "Problem lacks a question." 
-   ?: ( \Question > 1 )
-   : warn "Problem has more than one question." >?.

"   ?< ( \*Membership < 1 )
-   : warn "Problem belongs to which category?" >?.

"   ?< ( !\NP-Complete )
-   : warn "Problem NP-Complete?" >?.   [citation]

mother	:= "<s:w> is the other of <o:w>.".
"   ~> "<o> mother is <s>.".
"   ~> "<o> is child of <s>.".
Donation := "<donor:w> gives <money:n> dollars to <receiver:w>.".
"   =>> "<receiver> receives <money> dollars from <donor>.".
"   =>> "<receiver> gains <money> dollars.".
"   =>> "<donor> is a donor.". #hello
"   =>> "Donation <donor>, <receiver>.".

