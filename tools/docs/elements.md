Surface Evolver geometric elements

# Surface Evolver Documentation
Back to top of Surface Evolver documentation. Index.

# Geometric elements
The surface is defined in terms of its geometric elements of each dimension. Each element has its own set of attributes. Some may be set by the user; others are set internally but may be queried by the user. It is also possible to dynamically define extra attributes for any type of element, which may be single values or vectors of values. Attribute values can be specified in the datafile, and queried with commands.
Elements:

- Vertices
- Edges
- Facets
- Bodies
- Facetedges

## Vertices
A vertex is a point in space. The coordinates of the vertices are the parameters that determine the location of the surface. It is the coordinates that are changed when the surface evolves. A vertex carries no default energy, but may have energy by being on a level set constraint in the string model, or by having a named quantity energy applied to it. The vertices of the original surface are defined in the vertices section of the datafile.
Vertex attributes (grouped somewhat relatedly):

- id
- original
- coordinates, x,y,z, __x[]
- vertex edges
- vertex facets
- valence
- bare
- fixed
- constraints
- on_constraint
- hit_constraint
- value_of_constraint
- v_constraint_list
- constraint normal
- boundary
- parameter values, p1,p2, p[]
- on_boundary
- v_boundary

- extra attributes
- named quantities
- on_quantity
- on_method_instance
- v_method_list
- vertex_normal
- dihedral
- mean_curvature
- square mean curvature
- mid_edge
- mid_facet
- axial_point
- triple_point
- tetra_point
- v_force
- v_velocity
- raw_velocity
- v_oldx

Full descriptions of vertex attributes.

## Edges
An edge is a one-dimensional geometric element. In the linear model, an edge is an oriented line segment between a tail vertex and a head vertex. In the quadratic model, an edge is defined by quadratic intepolation of two endpoints and a midpoint. In the lagrange model, an edge is defined by the appropriate order interpolation with the edge vertices. In the string model, edges carry a default surface tension energy proportional to their length. Edges may also carry energy by being on level set constraints in the soapfilm model, or by having named quantity energies applied to them. The edges of the original surface are defined in the edges section of the datafile.
Edge attributes (grouped somewhat relatedly>:

- id
- oid
- original
- length
- density or tension
- fixed
- vertices
- midv
- facets
- valence
- bare
- constraints
- on_constraint
- e_constraint_list
- boundary
- on_boundary
- e_boundary

- color
- edge_vector, x,y,z
- no_refine
- no_transform
- wrap
- wrap_list
- show
- orientation
- frontbody
- backbody
- dihedral
- noncontent
- quantities
- on_quantity
- method instances
- on_method_instance
- e_method_list
- extra attributes

## Facets
In the soapfilm model, a facet is an oriented triangle defined by a cycle of three edges. In the linear model, a facet is a flat triangle. In the quadratic model, the facet is a curved surface defined by quadratic interpolation among the three facet corner vertices and the three edge midpoints. In the Lagrange model, lagrange_order interpolation is done among (lagrange_order+1)(lagrange_order+2)/2 vertices. Although individual facets are oriented, there are no restrictions on the orientations of adjacent facets. By default, a facet carries a surface tension energy equal to its area.
In the string model, a facet is a chain of an arbitrary number of edges. The chain need not be closed. Usually a facet is defined in the string model in order to define a body, so the space dimension is 2 and the facet is planar, one facet corresponding to a body. Facets carry no energy by themselves.
In the simplex model, a facet is a simplex of dimension surface_dimension defined by surface_dimension+1 vertices. The surface_dimension may be any dimension less than or equal to the space_dimension. The simplex is oriented according to the order of the vertices. By default, a simplex carries a surface tension energy proportional to its volume.
Facets may carry additional energy by having named quantity energies applied to them.
The facets of the original surface are defined in the faces section of the datafile.
Facet attributes (grouped somewhat relatedly):

- id
- oid
- original
- density or tension
- area
- fixed
- vertices
- edges
- bodies
- frontbody
- backbody
- f_body_list
- valence
- constraints
- on_constraint
- f_constraint_list
- boundary
- on_boundary

- f_boundary
- color
- frontcolor
- backcolor
- opacity
- facet_normal, x,y,z
- no_display
- no_refine
- no_transform
- orientation
- noncontent
- phase
- quantities
- on_quantity
- method instances
- on_method_instance
- f_method_list
- extra attributes
- f_next_vfacet
- f_next_bfacet

## Bodies
A body is a full-dimensional region of space. Bodies are not triangulated. Rather, they are determined by their boundary facets (or edges in 2D). These facets are used for calculating body volume and gravitational energy. Only those facets needed for correct calculation need be given. In the string model, usually a body corresponds to one facet. Bodies of the original surface are defined in the bodies section of the datafile.
Body attributes:

- id
- original
- facets
- density
- volume
- target
- volfixed

- volconst
- actual_volume
- pressure
- phase
- centerofmass
- extra attributes

## Facetedges
A facetedge is a pairing of a facet and one of its edges, with orientation such that the edge orientation is consistent with the facet orientation. Facetedges are used internally by Evolver, and are seldom of interest to the user. They carry no energy. The ' C ' integrity-checking command will sometimes refer to facetedges if the surface is inconsistent. Facetedge can be used as an element generator.
Facetedge attributes:

- id
- edge
- facet
- nextedge
- prevedge
- nextfacet
- prevfacet
- extra attributes

# Element attributes
Below is a list of possible element attributes. The first few apply to all types of elements. Then come those applying specifically to vertices, edges, facets, and bodies. See Geometric elements for lists of attributes for each type element.

# Attributes for all types of elements

## id
Geometric element read-only integer attribute. The id of an element is a positive integer uniquely associated with that element. The Evolver will assign id's to elements read from the datafile in the order they are read, unless the -i command line option or keep_originals is in the top of the datafile, in which case the datafile element number is the id. In either case, you can access the datafile id with the original attribute. Examples:

## oid
Geometric element read-only integer attribute. The oid of an element is the "oriented id" of an element as used in an expression. It is the id number signed according to whether the use of the element is with the same or opposite orientation as the way it is stored. Example: to get an edge list for a facet as in the datafile, use oid instead of id:

## fixed
Geometric element read-write boolean attribute. For vertices, fixed means they don't move during various evolution and triangulation grooming commands. For edges and facets, fixed means vertices generated from them by refinement are fixed, although declaring a facet or edge fixed does not automatically make its vertices fixed.
For a body, fixed means its volume is constrained to be its target value. Likewise, fixed as an attribute of a named quantity means the quantity value is constrained.
Fixedness can be changed with the fix and unfix commands.

## on_constraint
Vertex, edge, or facet read-only attribute. Boolean attribute for whether an element is on a given constraint. The full syntax of the attribute is " on_constraint n " where n is the number or name of the constraint. Examples:

## on_boundary
Vertex, edge, or facet read-only boolean attribute. The status of whether an element is on a parametric boundary The full syntax of the attribute is " on_boundary n " where n is the number or name of the boundary. Examples:

## on_quantity
Vertex, edge, or facet read-only attribute. Boolean attribute for whether an element contributes to a given named quantity. Actually, it tests whether the element is on any of the method instances comprising a quantity. The full syntax of the attribute is " on_quantity quantityname ". Examples:

## on_method_instance
Vertex, edge, or facet read-only attribute. Boolean attribute for whether an element contributes to a given named method instance. The full syntax of the attribute is " on_method_instance instancename ". Examples:

## original
Geometric element read-write integer attribute. For elements read from the datafile, this is the number given to the element in the datafile, which may be overridden by an explicit original attribute value in the datafile line defining the element. The value is inherited by all elements of the same type that result from subdivision. For elements otherwise generated at run time, the original attribute value is -1. Example: to show which facets descended from face 1 in the datafile:

## Named quantity values as attributes
Named quantities and method instances can be applied to geomtric elements either in the datafile (by adding the quantity or method name to the line defining an element) or with the set command. Nonglobal quantities or methods can be unset for individual elements. The values for individual elements can be accessed using attribute syntax. Examples: Suppose there is a named quantity "xmoment" that can be evaluated for facets. Then one could give commands

## Extra attributes
Geometric element read-write attributes. If extra attributes have been defined in the datafile or with a define command, they can be accessed with attribute syntax. Extra attribute values in the datafile can be initialized for an element by adding the attribute name and value to the line defining the element. Extra attributes may also be arrays of numeric values (global arrays can be strings, but attributes cannot yet), initialized with standard nested bracket syntax. Example: The command language can use the name with the same syntax as built-in attributes, and can define extra attributes at run time:

```text

  set vertex newx x
  define edge attribute vibel real[2]
  set edge[2] vibel[1] 3; set edge[2] vibel[2] 4
  print vertex[3].newx


```
Attribute array sizes may be changed at run time by executing another definition of the attribute, but the number of dimensions must be the same. Array entry values are preserved as far as possible when sizes are changed.
The value of an extra attribute can also be calculated by user-supplied code. The attribute definition is followed by the keyword "function" and then the code in brackets. In the code, the keyword "self" is used to refer to the element the attribute is being calculated for. Example: To implement the lowest z value of a facet as an attribute:

# Vertex attributes

## Vertex id
See id for general elements.

## Vertex original
See original for general elements.

## Vertex coordinates: x,y,z, x[], __x[]
Vertex read-write real attribute. The coordinates of a vertex are its location in space. By default, these are Euclidean coordinates, but they may represent any coordinate system if the user defines appropriate length, area, volume, etc. integrals. But graphics always treat the coordinates as Euclidean. The individual coordinates may be referred to as x, y, z, w or x1, x2, x3,.., or x[1], x[2], x[3], ... or __x[1], __x[2], __x[3], .... In the vertices section of the datafile, vertices of the original surface have their coordinates given unless they are on a parametric boundary. Vertices on parametric boundaries have their coordinates calculated from their parameter values. Coordinates may be read or modified with the command language. The form __x is useful to refer to the coordinates as a vector, for example in dot products. Examples:

## Vertex edges
Vertex read-only generator attribute. Generates edges attached to a vertex, oriented so vertex is the edge tail. The edges are in no particular order. Examples: Always use ".edges " to generate vertex edges; using "edges" with an implicit element, as in " foreach vertex do list edges " will list all edges in the surface over and over again.

## Vertex facets
Vertex read-only generator attribute. Generates facets attached to a vertex, with positive facet orientation. The facets are in no particular order. Examples: Always use ".facets " to generate vertex facets; using "facets" with an implicit element, as in " foreach vertex do list facets " will list all facets in the surface over and over again.

## Vertex valence
Vertex read-only integer attribute. The valence of a vertex is defined to be the number of edges it is a member of. Example:

## Vertex bare
Vertex read-write boolean attribute. Declaring a vertex bare says that a vertex is not supposed to have any adjacent edges. Useful in avoiding warning messages. A vertex may be declared bare in the vertices section of the datafile by adding the keyword bare to the line defining the vertex. Bare is not simply a synonym for zero valence; it is a separate attribute you set to say you intend for it to have zero valence. Examples:

## Vertex fixed
Vertex read-write boolean attribute. A fixed vertex will not move during iteration (except to satisfy level set constraints) or other operations, except if coordinates are explicitly changed by a " set vertices ... " command. A vertex may be declared fixed in the datafile by putting fixed on the line defining the vertex, after the coordinates. From the command prompt, one can fix or unfix vertices with the fix and unfix commands. Examples: formula

## Vertex constraints
Vertex read-write attribute. A level-set constraint is a restriction of vertices to lie on the zero level-set of a function. A constraint declared nonnegative in the datafile forces a vertex to have a nonnegative value of the function. A nonpositive constraint forces a vertex to have a nonpositive value of the function. A constraint may be declared global, in which case it applies to all vertices. A vertex may be put on a constraint in the vertices section of the datafile by listing the constraint numbers after the keyword constraint. See mound.fe for an example. In commands, the status of a vertex can be read with the on_constraint and hit_constraint attributes. The status can be changed with the set or unset commands. Examples:
Datafile: Runtime: See the on_constraint attribute for general elements.

## Vertex hit_constraint
Vertex read-only attribute. Boolean attribute for whether a vertex exactly satisfies a given constraint. Particularly meant for vertices on one-sided constraints. The full syntax of the attribute is " hit_constraint n " where n is the number or name of the constraint. Examples:

## Vertex value_of_constraint
Vertex read-only attribute giving the value of a level-set constraint for the current position of a vertex. Particularly meant for vertices on one-sided constraints. The full syntax of the attribute is " value_of_constraint n " where n is the number or name of the constraint. Examples:

## Vertex v_constraint_list
This read-only integer array attribute gives access to the list of constraints a vertex is on. v_constraint_list[1] is the number of constraints in the list, followed by the numbers of the constraints. Note that for named constraints, the internally assigned numbers are used. Because this is the actual internal datastructure, the entries may have some high bits used as flags, so to get the plain constraint numbers you should mask out the high bits with " imod 0x100000 ". Example:

## Constraint normal
The unit normal vector of a level-set constraint at a vertex may be found with the vertex vector attribute

```text
        constraint[number].normal
or      constraint[name].normal

```
"number" may be an expression; "name" is the unquoted name of the constraint, if it has one. Example: would print the unit normal of constraint floorcon at vertex 1. And you can put on a subscript to get individual components. For example, the y component: There is no necessity for the constraint to be applied to the vertex; the vertex is just used as a source of coordinates for evaluating the gradient of the constraint formula.

## Vertex boundary
Vertex read-write attribute. A vertex may be on a parameterized boundary, in which case its position is specified by parameter values; i.e. the space coordinates are functions of the parameters. The keyword boundary is used as an attribute only in the datafile declaration of elements being on boundaries. At runtime, one uses the attributes p1, p2, .. for the parameter values, on_boundary to see if a vertex is on a particular boundary, and v_boundary to get the number of the boundary. If you want to set a vertex on a boundary at runtime (tricky, since you have to set the parameters yourself), the use the " set vertex boundary ... " command.

## Vertex parameters p1, p2, p[]
Vertex read-write real attribute. Vertices on parametric boundaries are located according to the parameter values. Parameters are referred to as p1, p2,... Usually only p1 is used, since one-parameter curves used as boundary wires are most common. There is also an array form of the name, p, which is useful in array computations such as dot product in the case of multiple parameters. Such vertices in the original surface have their parameter values given in the vertices section of the datafile instead of their coordinates. Vertex parameters may be read or modified with the command language. Example:

## Vertex on_boundary
See on_boundary for general elements.

## Vertex v_boundary
Vertex read-only integer attribute. Internal attribute containing the number of any parameterized boundary the vertex is on. Recall that named boundaries have internal id numbers, which are used here.

## Vertex extra attributes
See extra attributes for general elements.

## Vertex named quantity
See named quantities for general elements.

## Vertex on_quantity
See on_quantity for general elements.

## Vertex named method instances
See named quantities for general elements.

## Vertex on_method_instance
See on_method_instance for general elements.

## Vertex v_method_list
Vertex read-only integer array attribute. Internal name for the array holding the id numbers of the method instances to which this vertex contributes. Vertices do not directly record which quantities they are on, they only record which method instances.

## Vertex vertex_normal or vertexnormal
Vertex read-only real array attribute. One-dimensional, size is space dimension. This is an indexed attribute consisting of the components of a normal to the surface at a vertex, normalized to unit length. This is the same normal as used in hessian_normal mode. For most vertices in the soapfilm model, the normal is the number average of the unit normals of the surrounding facets. Along triple edges and such where hessian_normal has a multi-dimensional normal plane, the vertex_normal is the first basis vector of the normal plane. Example: To print the normal components of vertex 3: The vertex_normal can also be printed as an array: Vertexnormal is an old synonym for vertex_normal.

## Vertex dihedral
Vertex read-only real attribute in the string model. This is the angle in radians from straightness of two edges at a vertex. If there are less than two edges, the value is 0. If two or more edges, the value is 2*asin(F/2), where F is the magnitude of the net force on the vertex, assuming each edge has tension 1. Upper limit clamped to pi.

## Vertex mid_edge
Vertex read-only boolean attribute. True (1) if the vertex is on an edge but not an endpoint. Relevant in the quadratic model or Lagrange model. Example:

## Vertex mid_facet
Vertex read-only boolean attribute. True (1) if the vertex is an interior control point of a facet in the Lagrange model. Example:

## Vertex mean_curvature
Vertex read-only ral attribute, available in the string and soapfilm model. The mean curvature is calculated as the magnitude of the gradient of area (or length in the string model) divided by the area (or length) associated with the vertex, which is one-third the area of the facets adjacent to the vertex (or one-half of the length of adjacent edges). It is divided by 2 in the soapfilm model to account for the "mean" part of the definition. The sign of the mean curvature is relative to the orientation of the first adjacent facet (or edge) Evolver finds. This calculation can be done even if the vertex is on a triple junction or other non-planar topology, even if it doesn't interpret well as mean curvature there.

## Vertex sqcurve
Geometric element read-only real attribute. Sqcurv is the squared mean curvature at a vertex. This is only a discrete approximation, of course, The method used to calculate it is the same as the sq_mean_curvature named method, except if the normal_curvature toggle is on, in which case the calculation is as in the normal_sq_mean_curvature named method. Does not require any other square mean curvature features to be active.

## Vertex axial_point
Vertex read-write boolean attribute. Certain symmetry groups (e.g. cubocta or rotate) have axes of rotation that are invariant under some non-identity group element. A vertex on such an axis must be labeled in the datafile with the attribute axial_point, since these vertices pose special problems for the wrap algorithms. If you are only using a subgroup of the full group, then you only need to label vertices on the axes of the subgroup. The net wrap around a facet containing an axial point need not be the identity. Edges out of an axial point must have the axial point at their tail, and must have zero wrap. Facets including an axial point must have the axial point at the tail of the first edge in the facet. It is your responsibility to use constraints to guarantee the vertex remains on the axis.

## Vertex triple_point
Vertex read-write boolean attribute. For telling Evolver three films meet at this vertex. Used when effective_area is on to adjust motion of vertex by making the effective area around the vertex 1/sqrt(3) of actual.

## Vertex tetra_point
Vertex read-write booloean attribute. For telling Evolver six films meet at this vertex. Used when effective_area is on to adjust motion of vertex by making the effective area around the vertex 1/sqrt(6) of actual.

## Vertex v_force
Vertex read-only real array attribute. This is an indexed attribute giving the components of the force (negative energy gradient as projected to constraints). One-dimensional, size is space dimension. Meant for debugging use. This is not directly used for the motion; see v_velocity.

## Vertex v_velocity
Vertex read-only real array attribute. This is an indexed attribute giving the components of the vector used for vertex motion in the ' g ' command. The motion of a vertex is the scale factor times this vector. The velocity vector is calculated from the force vector by applying area normalization, mobilty, etc. Also, if a vertex is on a boundary, the velocity is projected back to parameters. One-dimensional, size is space dimension.

## Vertex raw_velocity
Vertex read-only real array attribute. Internal vertex attribute used when one-sided level-set constraints are present, so the Lagrange multipliers for said constraints can be calculated. This is the velocity before any projection to volume or level-set constraints. One-dimensional, size is space dimension. Not of interest to the ordinary user.

## Vertex v_oldx
Vertex read-only real array attribute. Internal vertex array attribute used to store old coordinates when doing an optimizing move. One-dimensional, size is space dimension.

## Vertex no_hessian_normal
Vertex read-write attribute. If you wish to run in hessian_normal mode but exempt particular vertices from the restriction, you can "set" the vertices' no_hessian_normal attribute, for example

# Edge attributes

## Edge id
See id for general elements.

## Edge oid
See oid for general elements.

## Edge original
See original for general elements.

## Edge length
Edge read-only real attribute. Length of the edge. Examples:

## Edge density or tension
Edge read-write real attribute. "Density" and "tension" are synonyms. Energy per unit length of edge. Default 1 in string model, 0 in soapfilm model. The tension may be modified in the datafile edges section by adding " tension value " to the line defining the edge. The tension may be modified with the set command. Examples:

## Fixed edge
Edge read-write attribute. For an edge to be "fixed" means that any vertex or edge created by refining the edge will inherit the "fixed" attribute. Declaring an edge fixed in the datafile will not fix vertices on the edge, and fixing an edge from the command prompt will not fix any vertices. An edge may be declared fixed in the datafile edges section by adding fixed to the line defining the edge. From the command prompt, one can fix or unfix edges with the fix and unfix commands. Examples:

## Edge vertices
Edge read-only attribute. Acts as a generator for the vertices on an edge. In the linear model, this means the tail and head vertices. In the quadratic model, it means the tail, head, and middle vertices. For the Lagrange model, it means all the vertices from tail to head in order. For the simplex model, it means the vertices in the stored order. Example:

## Edge midv
Edge read-only attribute. In the quadratic model, gives the id of the midpoint vertex of an edge. Example:

## Edge facets
Edge read-only attribute. Generates facets attached to an edge, in order around the edge when meaningful, with facet orientation agreeing with edge orientation. Examples:

## Edge valence
Edge read-only integer attribute. The valence of an edge is the number of facets adjacent to it. Examples:

## Bare edge
Edge read-write boolean attribute. Declaring an edge "bare" indicates that an edge does not have an adjacent facet (soapfilm model). Best declared in the datafile, by adding the keyword bare to the line defining an edge. Useful in avoiding warning messages. Bare edges are useful to show wires, frameworks, outlines, axes, etc. in graphics. Example:

## Edge constraints
Edge read-write attribute. An edge may be put on a level set constraint. For such an edge, any vertices and edges generated by refining the edge will inherit the constraint. An edge may be put on constraints in the edges section of the datafile by listing the constraint numbers after the keyword constraint on the line defining the edge. Putting an edge on a constraint does not put its existing vertices on the constraint. In commands, the status of an edge can be read with the " on_constraint " attribute. The status can be changed with the set or unset commands. Examples:

## Edge on_constraint
See the on_constraint attribute for general elements.

## Edge e_constraint_list
This read-only attribute gives access to the list of constraints an edge is on. e_constraint_list[1] is the number of constraints in the list, followed by the numbers of the constraints. Note that for named constraints, the internally assigned numbers are used.

## Edge boundary
Edge read-write attribute. If an edge is on a parametric boundary, then any edges and vertices generated from the edge will inherit the boundary. By default, new vertex parameter values are calculated by extrapolating from one end of the edge. This avoids wrap-around problems that would arise from interpolating parameter values. But if the interp_bdry_param toggle is on, then interpolation is used. The status of whether an edge is on a boundary can be queried with the Boolean attribute on_boundary. Edges can be unset from boundaries, and set on them (but care is needed to do this properly). Examples:

## Edge on_boundary
See on_boundary for general elements.

## Edge e_boundary
Edge read-only integer attribute. Internal edge attribute holding the id numbers of the boundary an edge is on. Recall that named boundaries have internal id numbers, which are used here.

## Edge color
Edge read-write attribute. Color for graphics. The default color is black. Color may be set in the datafile, or with the set command. In geomview, the edge color will show up only for edges satisfying the show edge condition, and then they will have to compete with the edges geomview draws, unless you turn off geomview's drawing of edges with "ae" in the geomview window. Examples:

## Edge edge_vector
Edge read-only attribute. The components of the edge vector in the linear model can be accessed as edge attributes x,y,z or x1,x2,x3,..., or x[1],x[2],x[3]. edge_vector is another way to refer to the vector as a vector; it is useful for expressions like dot products where x won't work. In a command, the vector between edge endpoints is used in quadratic model or lagrange model. But when used in an integral, the tangent is evaluated at the Gaussian integration points. Not defined in the simplex model. Example to list nearly vertical edges:

## Edge no_refine
Edge and facet read-write Boolean attribute. An edge with the "no_refine" attribute will not be refined by the r command. This is useful for avoiding needless refining of lines or planes that are used only for display. The no_refine attribute may be specified on the datafile line for an edge, or the set command may be used. Examples:

## Edge no_transform
Edge and facet read-write Boolean attribute. An edge or facet with the "no_transform" attribute will not be duplicated by the view_transform mechanism; only the original element will occur. For example, you might have edges that form a display of coordinate axes, which you would not want duplicated. Example:

## Edge wrap
Edge read-write attribute. When a symmetry group is in effect (such as the torus model) and an edge crosses the boundary of a fundamental domain, the edge is labelled with the group element that moves the edge head vertex to its proper position relative to the tail vertex. The label is internally encoded as an integer, the encoding peculiar to each symmetry group. Edge wrappings are set in the datafile. The torus model has its own peculiar wrap representation in the datafile: * for no wrap, + for positive wrap, and - for negative wrap. Wraps are maintained automatically by Evolver during surface manipulations. The numeric edge wrap values can be queried with attribute syntax. Example: Unfortunately, the torus model wraps come out rather opaquely, since one cannot print hex. The torus wrap number is the sum of numbers for the individual directions: +x = 1; -x = 31; +y = 64; -y = 1984; +z = 4096; -z = 127040. Caution: even though this attribute can be written by the user at runtime, only gurus should try it.

## Edge wrap_list
Edge read-write integer array attribute. In a torus or symmetry model, this holds the integer used to encode the wrap of an edge. Note that this is implemented as an array of length 1 rather than just a value; I forget why, maybe so it could be length 0 if not needed. Example:

## Edge show
Edge and facet read-only Boolean attribute giving the current status of an edge or facet according to the show edge or show facet criterion in effect.

## Edge orientation
Edge integer read-write attribute. Controls the sign of oriented integrals on an edge. Value +1 or -1. Useful when triangulation manipulations create an edge going the wrong way. Example:

## Edge frontbody
Edge read-only integer attribute. In the string model, this is the id number of the body attached to the front of the edge, that is, the body on the facet that has positive orientation with respect to the edge. Invalid in the soapfilm model.

## Edge backbody
Edge read-only integer attribute. In the string model, this is the id number of the body attached to the back of the edge, that is, the body on the facet that has negative orientation with respect to the edge. Invalid in the soapfilm model.

## Edge dihedral
Edge read-only real attribute. The angle in radians between the normals of two facets on an edge. Zero if there are not exactly two facets. This attribute is not stored, but recalculated each time it is used. If there are not exactly two facets on the edge, the value is 0.

## Edge noncontent
Edge read-write boolean attribute. When set, indicates this facet should not be used in volume calculations in the soapfilm model or facet area calculations in the string model. Useful, for example, if you want to have edges be part of a body boundary for display purposes, but want to use constraint integrands for greater accuracy in volume calculations. Example:

## Edge named quantity
See named quantities for general elements.

## Edge on_quantity
See on_quantity for general elements.

## Edge named method instances
See named quantities for general elements.

## Edge on_method_instance
See on_method_instance for general elements.

## Edge e_method_list
Edge read-only integer array attribute. Internal edge attribute holding the id numbers of the method instances that this edge contributes to. Size expands as needed. Read-only. Use " set edge method ... " or "unset edge method .. " to change the status of a edge.

## Edge extra attributes
See extra attributes for general elements.

# Facet attributes

## Facet id
See id for general elements.

## Facet oid
See oid for general elements.

## Facet original
See original for general elements.

## Facet tension or density
Facet read-write attribute. Energy per unit area of facet; surface tension. Default 0 in string model, 1 in soapfilm model. May be set in the datafile by adding " tension value " to the line defining the facet. The density is inherited by any facets generated by refining. "Tension" and "density" are synonyms. Examples:

## Facet area
Facet read-only attribute. The area of the facet. Example:

## Facet fixed
Facet read-write attribute. For a facet to be "fixed" means that any vertex, edge, or facet created by refining a facet will inherit the fixed attribute. Fixing a facet in the datafile or at the command prompt does not fix any edges or vertices. A face may be declared fixed in the datafile by putting fixed on the line defining the face, after the coordinates. From the command prompt, one can fix or unfix facets with the fix and unfix commands.

## Facet vertices
Facet read-only attribute. Generates vertices around a facet, oriented as the facet boundary. "vertex" and "vertices" are synonymous. In the string model, if the facet is not a closed loop of edges, the vertices will be generated in order from one end. If the given facet has negative orientation, then the vertices will be generated accordingly. Example:

## Facet edges
Facet read-only attribute. Generates edges around a facet, oriented as the facet boundary. "edge" and "edges" are synonymous. In the string model, if the edges of the facet do not make a closed loop, then the edges will be listed in order starting from one end. If the given facet has negative orientation, the edges will be listed accordingly. Example:

## Facet bodies
Facet body generator attribute. Generates the bodies adjacent to a facet, in frontbody-backbody order. Example:

## Frontbody
Facet read-write attribute. The id of the body of which the facet is on the positively oriented boundary. Useful after creating a new body with the new_body command. As a read attribute, the value is 0 if there is no such body. Examples: Frontbody also works for adding edges to a facet in the string model, but the added edge must be attach to one end of the edge arc, or close the arc.

## Backbody
Facet read-write attribute. The id of the body of which the facet is on the negatively oriented boundary. Useful after creating a new body with the new_body command. As a read attribute, the value is 0 if there is no such body. Examples: Backbody also works for adding edges to a facet in the string model, but the added edge must be attach to one end of the edge arc, or close the arc.

## f_body_list
Facet internal array attribute. Contains the frontbody and backbody ids of the facet. Not too useful directly; listed here because it shows up in list_attributes.

## Facet valence
Facet read-only attribute. The valence of a facet is the number of edges (or vertices) that it contains. Most useful in the string model. Example:

## Facet constraints

Facet read-write attribute. Putting a facet on a constraint means that every vertex, edge, or facet generated by refining the facet will inherit that constraint. Setting a facet on a constraint does not set any of its existing edges or vertices on the constraint. Facets may be put on constraints in the datafile by listing the constraint numbers after the keyword constraint on the line defining the facet, or with the set command. They may be removed with the unset command. Examples:

## Facet on_constraint
See the on_constraint attribute for general elements.

## f_constraint_list
This read-only attribute gives access to the list of constraints a facet is on. f_constraint_list[1] is the number of constraints in the list, followed by the numbers of the constraints. Note that for named constraints, the internally assigned numbers are used.

## Facet boundary
Facet read-write attribute. If a facet is on a parametric boundary, then any facets, edges, and vertices generated from the facet will inherit the boundary. By default, new vertex parameter values are calculated by extrapolating from one vertex of the facet. This avoids wrap-around problems that would arise from interpolating parameter values. But if the interp_bdry_param toggle is on, then interpolation is used. The status of whether a facet is on a boundary can be queried with the Boolean attribute on_boundary. The actual boundary number is stored in the attribute f_boundary, which can be read but should not be written directly. Facets can be unset from boundaries, and set on them (but care is needed to do this properly). Examples:

## Facet f_boundary
Facet read-only integer attribute. The number of any parameterized boundary the facet is on. Note that named boundaries have internal numbers, and those are used here.

## Facet color
Facet read-write attribute. Color of both sides of facet for graphics. Default is white. Datafile example: Command examples:

## Facet frontcolor
Facet read-write attribute. Color of positive side of facet for graphics. Default is white. Datafile example: Command examples:

## Facet backcolor
Facet read-write attribute. Color of negative side of facet for graphics. Default is white. Set also when the "color" attribute is set. Datafile example: Command examples:

## Facet opacity
Facet read-write attribute for transparency. Syntax: set facet opacity value where condition where value is between 0 (clear) and 1 (opaque). Screen graphics will show transparency, but PostScript output will not. Hitting the 'O' key in the graphics window will toggle transparency, if the opacity attribute has been assigned values. Datafile example: Command examples:

## Facet facet_normal
Facet read-only attribute. The components of the facet normal vector may be referred to as x,y,z or x1,x2,x3 or x[1],x[2],x[3] in the linear model. Length is equal to facet area. facet_normal is the internal name of the attribute, and is useful to refer to the entire vector in array expressions such as dot product. In quadratic model or lagrange model, only the three facet corner vertices are used to calculate the normal. When used in integrals, the normal is calculated at each integration points. Not defined in simplex model.

## Facet no_display
Facet read-write attribute. When set, suppresses the display of the facet in graphics. Can be set in the datafile by adding nodisplay to the line defining the facet. Can also be manipulated by the set and unset commands. No_display is a synonym provided since that's what I kept typing in. Example:

## Facet no_refine
Facet read-write Boolean attribute. Giving a facet the no_refine attribute has no effect except that edges created within the facet by refining will inherit the no_refine attribute. So to avoid refinement of a plane, all edges and facets in the plane must be given the no_refine attribute. The no_refine attribute may be specified on the datafile line for a facet, or the set command may be used. Examples:

## Facet no_transform
Edge and facet read-write Boolean attribute. An edge or facet with the "no_transform" attribute will not be duplicated by the view_transform mechanism; only the original element will occur. For example, you might have facets that form a display of outer walls which you would not want duplicated. Example:

## Facet orientation
Facet read-write attribute. Controls the sign of oriented integrals on a facet. Value +1 or -1. Useful when triangulation manipulations create a facet with an undesired orientation. Example: Also see the reverse_orientation command to physically reverse a facet's orientation.

## Facet noncontent
Facet read-write attribute. When set, indicates this facet should not be used in volume calculations. Useful, for example, if you want to have facets be part of a body boundary for display purposes, but want to use constraint integrands for greater accuracy in volume calculations. Example:

## Facet phase
Facet read-write attribute. If there is a phasefile, this attribute determines the edge tension of an edge between two facets in the string model. Example:

## Facet named quantity
See named quantities for general elements.

## Facet on_quantity
See on_quantity for general elements.

## Facet named method instances
See named quantities for general elements.

## Facet on_method_instance
See on_method_instance for general elements.

## Facet extra attributes
See extra attributes for general elements.

## Facet f_method_list
Facet array attribute. Internal name for the array holding the id numbers of the method instances to which this facet contributes. Read-only.

## Facet f_next_bfacet
Facet read-only attribute. Used internally when iterating over the facets comprising a body.

## Facet f_next_vfacet
Vertex integer attribute. Internal attribute used for the linked list that is used when iterating over the facets adjacent to a vertex. Not accessible to user since it uses internal element id type.

# Body attributes

## Body id
See id for general elements.

## Body original
See original for general elements.

## Body facets
Body read-only attribute. Generates facets bounding a body, with proper facet orientation with respect to the body. Example:

## Body density
Body read-write attribute. Density used for gravitational potential energy. It can be set in the bodies section of the datafile, or with the set command, or by assignment. Command examples:

## Body volume
Body read-only attribute. Actual volume of a body. This is the sum of three parts, in the soapfilm model:

- An integral over the facets bounding the body. This is \int z dx dy normally, but \int (x dy dz + y dz dx + z dx dy)/3 if symmetric_content is in effect.
- Any constraint content edge integrals applying to the body.
- The body's volconst attribute.
In the string model, the parts are

- An integral over the edges bounding the body's facet. This is \int -y dx.
- Any constraint content vertex integrals applying to the body.
- The body's volconst attribute.
Body volumes can be displayed with the v command, or with standard attribute syntax. Example:

## Body target
Body read-write attribute. The target volume of a volume constraint. May be set in the datafile, by the b command, or the set command. A volume constraint may be removed by the unset, or with the b command. Command examples:

## Body volfixed
Body Boolean read-only attribute. Value is 1 if the volume of the body is fixed, 0 if not.

## Body volconst
Body read-write attribute. A constant added to the calculated volume. Useful for correcting for omitted parts of body boundaries. Also used internally as a correction in the torus model, which will use the target volume to calculate volconst internally. In the torus model, the target volume should be set within 1/12 of a torus volume of the actual volume for each body, so the correct volconst can be computed. Each volconst will be adjusted proportionately when the volume of a fundamental torus domain is change by changing the period formulas. Volconst can be set in the datafile bodies section, or interactively by the set command or by assignment. Examples: It is best to avoid using volconst except in the torus model. Rather, use edge content integrals so that the proper adjustments will be made if the boundary of the surface is moved, or rebody is done.

## Body actual_volume
Body datafile attribute. Actual_volume is a number that can be specified in the datafile definition of a body in the rare circumstances where the torus model volume volconst calculation gives the wrong answer; volconst will be adjusted to give this volume of the body.

## Body pressure
Body read-write real attribute. If a body has a prescribed volume, this is a read-only attribute, which is the Lagrange multiplier for the volume constraint. If a body is given a prescribed pressure, then there is an energy term equal to pressure times volume. A body cannot have a prescribed volume and a prescribed pressure at the same time. Prescribed volume or pressure can be set in the bodies section of the datafile. If pressure is prescribed, then the value can be changed interactively with the b command, the set command, or by assignment. Examples:

## Body phase
Body read-write attribute. If there is a phasefile, this attribute determines the facet tension of an edge between two bodies in the soapfilm model. Example:

## Body centerofmass
Body read-write boolean attribute. Boolean body attribute. Applies to the "connected" bodies mode of graphical display in the torus model. When this is set for a body, the center of mass of the body as displayed is remembered, and the next time a body is graphed, its wrap is such that its new center of mass is near its previous center of mass. This prevents bodies near the boundaries of the fundamental region from jumping back and forth as they shift slightly during evolution. Default on. Example:

## Body quantities
There are no named methods currently implemented for bodies, so named quantities and methods do not apply.

# Facetedge attributes

## Facetedge id
See id for general elements.

## Facetedge oid
See oid for general elements.

## Facetedge edge
Facetedge read-only attribute. Generates the single edge of the facetedge. Example:

## Facetedge facet
Facetedge read-only attribute. Generates the single facet of the facetedge. Example:

## Facetedge nextedge
Facetedge internal attribute. Oriented id number of the next facetedge in the facet edge loop. May be 0 in the string model for the last edge of a facet. Not available to users except in the output of a "list facetedges ... " command.

## Facetedge prevedge
Facetedge internal attribute. Oriented id number of the previous facetedge in the facet edge loop. May be 0 in the string model for the first edge of a facet. Not available to users except in the output of a "list facetedges ... " command.

## Facetedge nextfacet
Facetedge internal attribute. Oriented id number of the next facetedge in the loop of facets around the edge. Not available to users except in the output of a "list facetedges ... " command.

## Facetedge prevfacet
Facetedge internal attribute. Oriented id number of the previous facetedge in the loop of facets around an edge. Not available to users except in the output of a "list facetedges ... " command. Back to top of Surface Evolver documentation. Index.
