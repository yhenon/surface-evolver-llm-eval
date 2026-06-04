Surface Evolver Documentation - Constraints

# Surface Evolver Documentation
Back to top of Surface Evolver documentation. Index.

# Constraints and Boundaries

The usual mode of operation of the Surface Evolver is to minimize energy subject to constraints. There are two broad categories of constraints:

- Pointwise constraints:

- Fixed vertices

- Level set constraints

- One-sided constraints

- Parametric "boundary" curves and surfaces

- Global constraints:

- Volume constraints

- Named quantity constraints

## Level set constraints
A level-set constraint is a restriction of vertices to lie on the zero level-set of a function. The formula may include any expressions whose values are known to the Evolver, given the particular vertex. Most commonly one just uses the coordinates (x,y,z) of the vertex, but one can use variables, quantity values, or vertex extra attributes. Using a vertex extra attribute is a good way to customize one formula to individual vertices. For example, if there were a vertex extra attribute called zfix, one could force vertices to individual z values with one constraint with the formula z = zfix, after of course assigning proper values to zfix for each vertex. A level set constraint may have several roles:

- Vertices may be required to lie on a constraint (equality constraint) or on one side ( inequality constraint). A constraint may be declared GLOBAL, in which case it applies to all vertices. See mound.fe for an example.

- A constraint may have an energy vectorfield associated with it that is integrated over edges lying in the constraint to give an energy. This is useful for specifying wall contact angles and for calculating gravitational energy. Integrals are not evaluated over edges that are FIXED. See mound.fe for an example. In the string model, the energy integrand is a single component evaluated on vertices on the constraint.

- A constraint may have a content vectorfield associated with it that is integrated over edges lying in the constraint to give a volume contribution to a body whose boundary facets contain the edges. This is useful for getting correct volumes for bodies without completely surrounding them with otherwise useless facets. It is important to understand how the content is added to the body in order to get the signs right. The integral is evaluated along the positive direction of the edge. If the edge is positively oriented on a facet, and the facet is positively oriented on a body, then the integral is added to the body. This may wind up giving the opposite sign to the integrand from what you think may be natural. Integrals are not evaluated over edges that are FIXED. See tankex.fe for an example. In the string model, the content integrand is a single component evaluated on vertices on the constraint.

- There is a constraint attribute content_rank such that if a vertex (string model) or an edge (soapfilm model) is on multiple boundaries with content integrals (say where walls meet) then if content ranks are present, the content integral with the least rank will contribute to the content on the negative side body and the highest rank content will contribute to the content of the positive side body.
- A constraint may be declared CONVEX, in which case edges in the constraint have an energy associated with them that is proportional to the area between the straight edge and the curved wall. This energy (referred to as " gap energy ") is meant to compensate for the tendency for flat facets meeting a curved wall to minimize their area by lengthening some edges on the wall and shortening others, with the net effect of increasing the net gap between the edges and the wall. See tankex.fe for an example.

Level set constraints are declared in the top section of the datafile. They may be applied to vertices, edges, or facets. Constraints are usually applied to vertices and edges, as in mound.fe. Remember that you need to apply a constraint to an edge to get that constraint to apply to vertices created on that edge by refining. Sometimes one applies constraints to facets, usually to get the facet to conform to a predetermined shape. Be sure that the constraints applied to a vertex are linearly independent at the vertex.
Constraints are usually applied in the datafile vertices, edges, and faces sections, but they may also be set or removed with the set or unset commands. Example: It does not hurt to unset an element that isn't on the constraint. When a vertex is set to a constraint, the vertex coordinates are immediately projected to the constraint. Setting an edge on a constraint does not set its vertices. Likewise for facets.
Several element attributes are useful in connection with level-set constraints:

- on_constraint - Boolean attribute that tells whether the element has been put on a constraint.
- hit_constraint - Boolean vertex attribute that tells whether the constraint exactly satisfies the constraint. Meant for one-sided constraints; always 1 for exact constraints.
- value_of_constraint - Vertex attribute that is the value of the constraint formula at the vertex.
- v_constraint_list,- e_constraint_list,- f_constraint_list -- Vector attribute whose first element is the number of constraints the element is on, followed by a list of the constraint numbers (using the internal numbers for named constraints).
- constraint normal - unit vector perpendicular to the level set at a vertex.
Whether a particular level-set constraint is an equality constraint or a one-sided constraint can be queried at runtime by the expression

```text
     is_constraint[number].fixed
or   is_constraint[name].fixed


```
"number" may be an expression; "name" is the unquoted name of the constraint, if it has one. This has value 1 if the constraint is an equality constraint, else the value is zero. Example of listing all the equality constraints that vertices are on:

## One-sided constraints
If a level set constraint is declared NONNEGATIVE or NONPOSITIVE in the datafile, the vertices subject to the constraint must stay in that part of the domain of the level set function. It is usually unwise to give edge integrals to edges on one-sided constraints, or to declare them CONVEX. Whether a vertex exactly satisfies the constraint may be queried with the vertex hit_constraint attribute. The 'g' iteration step will check for a vertex wanting to leave a one-sided constraint it has hit, but hessian commands do not; therefore it is wise to intersperse 'g' with hessian or hessian_seek when there are one-sided constraints involved.
Example: Suppose one wanted to keep a bubble inside a spherical tank of radius 5. Then one would define the constraint in the datafile For purposes of evaluating nonnegativity or nonpositivity, all terms are shifted to the left side of the formula. One would then apply this constraint to all vertices, edges, and facets of the bubble surface.
If you define the real-valued vertex extra attribute one_sided_lagrange, the Lagrange multipliers for vertices hitting one-sided constraints will be recorded. one_sided_lagrange may be defined as an array. If a vertex hits more constraints than the size of one_sided_lagrange, then the first ones that fit will be recorded.
The type of a constraint can be queried at runtime as expressions

```text

     is_constraint[number].nonnegative
     is_constraint[name].nonnegative
     is_constraint[number].nonpositive
     is_constraint[name].nonpositive
     is_constraint[number].fixed
     is_constraint[name].fixed

```
which have value 1 if the constraint is of the give type, else the value is 0. "number" may be an expression; "name" is the unquoted name of the constraint, if it has one. Example:

## Parametric "boundary" curves and surfaces
Vertex locations may be given in terms of parameters on a parameterized curve or surface. Such curves or surfaces are called "boundaries" in Evolver terminology, since they are usually used as boundary curves of surfaces, for example a soap film on a wire loop could have the wire implemented as a boundary. Vertices, edges, and facets may be deemed to lie in a boundary. For a vertex, this means that the fundamental parameters of the vertex are the parameters of the boundary, and its coordinates are calculated from these. Vertices on boundaries may move during iteration, unless declared fixed. See cat.fe for an example.

Boundaries are defined in the top section of the datafile. Vertices on boundaries are listed in the datafile with their parameter values instead of their coordinates, with " boundary n " appended to each such vertex definition. Edges and faces on boundaries are defined as usual, but with " boundary n " appended to each definition. So the datafile has lines like these:

```text

boundary 1 parameters 1
x1:  cos(p1)
x2:  sin(p1)
x3:  0.75
...
Vertices
1   0.0  boundary 1
2   pi/3 boundary 1
...
Edges
1   1 2 boundary 1
...


```

Putting an edge on a boundary means that vertices created on that edge will be on the boundary. An edge on a boundary must have at least one endpoint on the boundary, for use in extrapolating the boundary parameters of any created vertices. Extrapolating instead of interpolating midpoint parameters solves the problem of wrap-arounds on a boundary such as a circle or cylinder. However if you do want interpolation, you can use the keyword INTERP_BDRY_PARAM in the top of the datafile, or use the toggle command interp_bdry_param. Interpolation requires that both endpoints of an edge be on the same boundary, which cannot happen where edges on different boundaries meet. To handle that case, it is possible to add extra boundary information to a vertex by declaring two particular vertex extra attributes, extra_boundary and extra_boundary_param:

```text

interp_bdry_param
define vertex attribute extra_boundary integer
define vertex attribute extra_boundary_param real[1]


```
Then declare attribute values on key vertices, for example If the extra_boundary attribute is not set on a vertex when wanted, Evolver will silently fall back on interpolation.
Putting a face on a boundary means that all edges and vertices created from refining the face will be on the boundary. In this case, the boundary should have two parameters (or whatever the dimension of the surface is). This is good for getting a surface to conform to a known parametric shape.
Edges on boundaries have energy and content integrals like level-set constraints edges, but they are internally implemented as. named quantities.

Whether an element is on a particular boundary can be queried with the on_boundary Boolean attribute. Elements can be removed from boundaries with the unset command, and they can be set on boundaries. A typical use of unset is to define an initial surface using a 2-parameter boundary, refine a couple of times, then unset. Examples: It does not hurt to unset an element not on the boundary.
The number of the boundary that an element is on is in the read-only attribute __v_boundary, __e_boundary, or __f_boundary. These are 0 if the element is not on a boundary. These attributes are not present if there are no boundaries defined. Note that named boundaries are internally assigned numbers, which are what show up here.
Vertex parameters can be accessed in expressions as the attribute p1 (and p2,... for further parameters). Vertex parameters can be changed with the set command. Example: It is not an error to access the parameters of a vertex not on a boundary as long as some vertex is on a boundary (so that space is allocated in the vertex structure for parameters).
A general guideline is to use constraints for two-dimensional walls and boundaries for one-dimensional wires. If you are using a boundary wire, you can probably declare the vertices and edges on the boundary to be FIXED. Then the boundary becomes just a guide for refining the boundary edges.

NOTE: A vertex on a boundary cannot also have constraints.

## Named quantity constraints
See fixed named quantities. Back to top of Surface Evolver documentation. Index.


// tankex.fe

// Equilibrium shape of liquid in flat-ended cylindrical tank.

// Tank has axis along y-axis and flat bottom in x-z plane.  This
// is so gravity acting vertically draws liquid toward wall.

// Straight edges cannot conform exactly to curved walls.  
// We need to give them an area so that area cannot shrink by straght edges 
// pulling away from the walls. The gaps are also accounted for
// in volume and gravitational energy.

SYMMETRIC_CONTENT     // for volume calculations

// Contact angles, initially for 30 degrees (seems unstable for angles > 45).
PARAMETER ENDT  = cos(30*pi/180)   /* surface tension of uncovered base   */
PARAMETER WALLT = cos(30*pi/180)   /* surface tension of uncovered side wall */

// Gravity components
PARAMETER GY = 0
PARAMETER GZ = -.3

SPRING_CONSTANT 1  // for most accurate gap areas for constraint 2

#define  TR  1.00       /* tank radius */
#define  RHO 1.00       /* fuel density */

constraint 1  // flat base
function:  y = 0
energy:               // for contact energy line integral
e1:   -ENDT*z
e2:   0
e3:   0

#define wstuff (WALLT*TR*y/(x^2 + z^2))   // common wall area term
#define vstuff (TR^2/3*y/(x^2 + z^2))     // common wall volume term
#define gstuff (GY*TR^2*y^2/4/(x^2 + z^2) + GZ*TR^3*y*z/3/(x^2+z^2)**1.5)
                                          // common gap gravity term

constraint 2  CONVEX         // cylindrical wall
function:  x^2 + z^2 = TR^2
energy:                // for contact energy and gravity
e1:  -wstuff*z  + RHO*GY*y^2*z/4 + RHO*GZ*y*z^2/3 - RHO*gstuff*z
e2:    0
e3:   wstuff*x  - RHO*GY*y^2*x/4 - RHO*GZ*y*z*x/3 + RHO*gstuff*x
content:               // so volumes calculated correctly
c1:   vstuff*z - z*y/6 + vstuff*z/2
c2:    0
c3:  -vstuff*x + x*y/6 - vstuff*x/2

// named quantity for arbitrary direction gravity on facets
quantity arb_grav energy method facet_vector_integral global
vector_integrand:
q1:  0
q2:  -RHO*GY*y^2/2 - RHO*GZ*y*z
q3:  0


// Now the specification of the initial shape

vertices
1    0.5  0.0  0.5  constraint 1
2    0.5  0.0 -0.5  constraint 1
3   -0.5  0.0 -0.5  constraint 1
4   -0.5  0.0  0.5  constraint 1
5    1.0  0.5  0.0  constraint 2
6    0.0  0.5 -1.0  constraint 2
7   -1.0  0.5  0.0  constraint 2
8    0.0  0.5  1.0  constraint 2

edges
1    2  1  constraint 1
2    1  4  constraint 1
3    4  3  constraint 1
4    3  2  constraint 1
5    5  6  constraint 2
6    6  7  constraint 2
7    7  8  constraint 2
8    8  5  constraint 2
9    1  8
10   1  5
11   2  5
12   2  6
13   3  6
14   3  7
15   4  7
16   4  8

faces
1   13   6 -14
2    3  14 -15 
3   15   7 -16
4    2  16  -9
5    9   8 -10
6    1  10 -11
7   11   5 -12
8    4  12 -13

bodies
1    1 2 3 4 5 6 7 8   volume 0.6  density 0  /* no default gravity */ 


read

// typical evolution
gogo := { r; g5; r; g 5; U; g 70; t .01; g 10; t .05; g 50; t .05;
	  r; g 20;
	}
