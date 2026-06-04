Surface Evolver Documentation - Datafile format

# Surface Evolver Documentation
Back to top of Surface Evolver documentation. Index.

# Evolver datafile format
The initial configuration of the surface is read from an ASCII datafile. See the cube or mound examples for samples. The datafile is organized into six parts:

- Definitions and options
- Vertices
- Edges
- Faces
- Bodies
- Initial commands
General datafile topics:

- General syntax (for datafiles and commands)
- Include files
- Macros
In the syntax descriptions below, keywords will be in upper case. constexpr means a constant expression, and expr means any expression. n or k means an integer, which may be signed if it is being used as an oriented element label. Square brackets denote optional items. '|' means 'or'.
NOTE: Usually a formula can occur anyplace a number is legal (except element numbers, constraint numbers, etc). Some formulas are stored as formulas and re-evaluated at each use; examples include constraint, boundary, and quantity formulas. Others, such as vertex coordinates, are evaluated when the datafile is read, and only the numeric value stored. Thus if a user defines a vertex coordinate as 3*width, then changing the value of the variable width at runtime will not affect the vertex. If you are not clear on which interpretation applies in a certain spot, dump the datafile and look at the spot to see if a formula or number was dumped.

## Include files
The standard C language method of including other files is available. The file name must be in double quotes. If the file is not in the current directory, EVOLVERPATH will be searched. Includes may be nested to 10 deep. Example:

## Macros
Macros are text substitutions done by replacing an identifier by a string of characters before parsing. Macros are only defined in the datafile, and do not work from the command prompt. Simple macros (no parameters) may be defined as in C:

```text
         #DEFINE  identifier  string


```
identifier must be an identifier without other special meaning to the parser. string is the rest of the logical line, not including comments. It will be substituted for identifier whenever identifier occurs as a token subsequently. Substitutions are re-scanned. No checks for recursiveness are made. There is a maximum length (currently 500 characters) on a macro definition. Note: macro identifiers are separate tokens, so if "-M" translates into "-2", this will be read as two tokens, not a signed number. The keyword keep_macros in the datafile will keep macro definitions active during runtime, until the next datafile is loaded.

## Datafile top section
The datafile begins with optional definitions and specifications. These are definitions that need to be made before the geometric elements are defined, or for which command syntax is lacking or awkward. Other initializations can be made at the end of the datafile in the read section using the command language. Each line starts with a keyword. The order is immaterial, except for the usual rule that items must be defined before use. None of these are required if you are willing to accept various defaults. They are listed here in rough order of frequency of use; those in the first column you should know, those in the second column you might never use in a lifetime.

- Variables
- Level set constraints
- Parametric boundaries
- Named quantities
- Named method instances
- Surface dimension
- Space dimension
- Extra attributes
- Quadratic model
- Gravity constant
- Torus model
- Torus_filled
- Torus periods
- Viewing matrix
- View transforms
- View transform generators
- Scale_limit
- Functions and procedures
- Optimizing Parameters
- Gap constant
- Symmetric content
- Keep original ids

- Squared mean curvature
- Constraint tolerance
- Version
- Metric
- Simplex model
- Symmetry group
- Length method
- Area method
- Volume method
- Hessian special normal vector
- Crystalline integrands
- Diffusion
- Phase file
- Ideal gas model
- Interpolation of boundary parameters
- Mobility
- Merit factor
- Squared Gaussian curvature
- Zoom_vertex
- Zoom_radius
- Dynamic load library
- Suppressing warnings
- vertices_predicted
- edges_predicted
- facets_predicted
- facetedges_predicted
- bodies_predicted
- quantities_predicted
- method_instances_predicted

## Definitions of variables
Variables may be defined in the datafile top section with this syntax:

```text

      PARAMETER identifier = constexpr


```
This declares identifier to be a variable with the given initial value. The value may be changed at runtime with the A command, or by assignment. Variables may be used in any subsequent expression or constant expression. Changing variables defined here results in automatic recalculation of the surface when autorecalc is been toggled on. Hence only variables needed in other top section declarations should be defined here.
A procedure may be designated to be called whenever the value of the variable is changed. The syntax in the top of the datafile is

```text

      PARAMETER identifier = constexpr ON_ASSIGN_CALL procedure_name


```
The purpose of this feature is to permit side-effects of changing a variable value. The value is a procedure without arguments, and can only be assigned in the top of the datafile. However, the procedure itself may be redefined at will. Example (in the top of the datafile): Note that there is a declaration of "tester" first, so Evolver recognizes "tester" as a procedure name during the declaration of "bbb". But the full declaration of "tester" may be in the top of the datafile or in the "read" section of the datafile.

## Level set constraint declarations
The format for declaring a level set constraint in the top section of the datafile is

```text

CONSTRAINT n [GLOBAL] [CONVEX] [NONNEGATIVE] [NONPOSITIVE] [NONWALL] [CONTENT_RANK n]
FORMULA FUNCTION  expr
[ENERGY:
 E1: expr
 E2: expr
 E3: expr]
[CONTENT:
 C1: expr
 C2: expr
 C3: expr]


```
You may use EQUATION or FUNCTION as synonyms for FORMULA. This defines constraint number n, where n is a positive integer. The optional keyword GLOBAL means the constraint automatically applies to all vertices (but not automatically to edges or faces). GLOBAL constraints count in the number limit. If CONVEX is given, then an additional gap energy is attributed to edges on the constraint to prevent them from trying to short-circuit a convex boundary. NONWALL indicates this constraint is to be ignored in vertex and edge popping, and the various ``star'' squared mean curvature methods will not regard this constraint as a mirror plane. If NONNEGATIVE or NONPOSITIVE is given, then this is a one-sided constraint, and all vertices will be forced to conform appropriately to the constraint at each iteration. The FORMULA expression defines the zero level set which is the actual constraint. It may be written as an equation, since '=' is parsed as a low-precedence minus sign. The formula may include any expressions whose values are known to the Evolver, given the particular vertex. Most commonly one just uses the coordinates (x,y,z) of the vertex, but one can use variables, quantity values, or vertex extra attributes. Using a vertex extra attribute is a good way to customize one formula to individual vertices. For example, if there were a vertex extra attribute called zfix, one could force vertices to individual z values with one constraint with the formula z = zfix, after of course assigning proper values to zfix for each vertex (be sure to fix up zfix after refining or otherwise creating vertices). Do not use '>' or '<' to indicate inequalities; use NONNEGATIVE or NONPOSITIVE. Conditional expressions, as in C language, are useful for defining constraints composed of several surfaces joined smoothly, such as a cylinder with hemispherical caps. Assignments to variables may be made at the start of expressions, mainly for the purpose of evaluating common subexpressions only once in the integrands. The syntax for such a compound expression is

```text

    variable :=  expr, expr


```
The value of the expression is the value of the second expression.
The optional ENERGY section signifies that vertices or edges on the constraint are deemed to have an energy. In the soapfilm model, the next lines give components of a vectorfield that will be integrated along each edge on the constraint. In the string model, just one component is needed, which is evaluated at each vertex on the constraint. The main purpose of this is to permit facets entirely on the constraint to be omitted. Any energy they would have had should be included here. One use is to get prescribed contact angles at a constraint. This energy should also include gravitational potential energy due to omitted facets. Integrals are now also evaluated on fixed edges, which is a change from earlier versions of Evolver.
The optional CONTENT section signifies that vertices ( string model) or edges ( soapfilm model) on the constraint contribute to the area or volume of bodies. If the part of a body boundary that is on a constraint is not defined by facets, then the body volume must get a contribution from a content integral. It is important to understand how the content is added to the body in order to get the signs right. The integral is evaluated along the positive direction of the edge. If the edge is positively oriented on a facet, and the facet is positively oriented on a body, then the integral is added to the body. This may wind up giving the opposite sign to the integrand from what you think may be natural. Always check a new datafile when you load it to be sure the integrals come out right. The constraint attribute content_rank is used in conjunction with content integrals. If a vertex (string model) or an edge (soapfilm model) is on multiple constraints with content integrals (say where walls meet) then if content ranks are present, the content integral with the least rank will contribute to the content on the negative side body and the highest rank content will contribute to the content of the positive side body.

## Parameterized boundary declaration
A parameterized boundary may be declared in the top section of the datafile with the syntax

```text

BOUNDARY n PARAMETERS k [CONVEX]
X1: expr
X2: expr
X3: expr


```
This defines boundary number n, where n is a positive integer and k is the number of parameters. If CONVEX is given, then an additional gap energy is attributed to edges on the boundary to prevent them from trying to short-circuit a convex boundary. The following lines have the functions for the coordinates in terms of the parameters P1 and maybe P2, P3,.... See the catenoid example. Energy and content integrals for boundaries are implemented, with the same syntax as for level set constraints.

## Named quantities
The syntax for defining a named quantity in the data file is:

```text
 QUANTITY name   ENERGY|FIXED=value|CONSERVED|INFO_ONLY [LAGRANGE_MULTIPLIER constexpr]
[TOLERANCE constexpr]  [MODULUS constexpr] methodlist | FUNCTION methodexpr


```

Here name is an identifier assigned by the user in order to refer to the quantity. Any quantities must be declared to be one of three types:

- ENERGY quantities are added to the overall energy of the surface;
- FIXED quantities that are constrained to a fixed target value;
- CONSERVED quantities are like FIXED in that the motion is projected to conserve the quantity, but the actual value is not projected to a given value.
- INFO_ONLY quantities whose values are merely reported to the user.
For fixed quantities, the optional Lagrange multiplier value supplies the initial value of the Lagrange multiplier (the "pressure" attribute of the quantity). It is meant for dump files, so on reloading no iteration need be done to have a valid Lagrange multiplier.
For fixed quantities, the tolerance attribute is used to judge convergence. A surface is deemed converged when the sum of all ratios of quantity discrepancies to tolerances is less than 1. This sum also includes bodies of fixed volume. If the tolerance is not set or is negative, the value of the variable target_tolerance is used, which has a default value of 0.0001.
Each quantity has a modulus, which is just a scalar multiplier of the whole quantity. A modulus of 0 will turn off an energy quantity. The default modulus is 1. The methodlist version of the quantity definition may contain one or more method instances. To incorporate a previously explicitly defined instance, include METHOD instancename. GLOBAL_METHOD may be used instead of METHOD to indicate the method applies to all elements of the appropriate type; it is equivalent to using GLOBAL in the method definition. To instantiate a method in the quantity definition, you essentially incorporate the instance definition, but without an instance name. Example of a quantity with one predefined method instance and one implicitly defined instance:
Usually the second, implicit definition will be more convenient. Several method instances may be included in one methodlist (up to a current limit of 50), and their values are added together and multiplied by the quantity modulus to get the quantity value. The FUNCTION methodexpr variant defines the quantity as a function of previously defined method instances. Example:
Non-global quantities may be applied to elements individually by adding the quantity name to the datafile line defining an element. They may also be applied or unapplied at runtime with the set and unset commands. Orientable methods can be applied with negative orientation in the datafile by following the method name with a dash. The orientation in a "set" command follows the orientation the element is generated with.
Methods applying to different types of elements may be combined in one quantity. If such a quantity is applied to an element, then all method instances of that quantity of the appropriate type are applied to the element. Original attachments of quantities are remembered, soIf an edge method is applied to a facet, then edges created from refining that facet will inherit the edge method.

## Named method instances declaration
Method instances are usually defined as part of the definition of a named quantity, but there are circumstances where a quantity is composed of several method instances and the method instances need to be referred to individually; perhaps the user wants to know the values of the individual instances. The general syntax for defining an instance of a named method in a datafile is:

```text
  METHOD_INSTANCE name METHOD methodname [MODULUS constexpr]
   [ELEMENT_MODULUS attrname]  [GLOBAL] [parameters]


```
Here, name is a user-assigned name for referring to this particular instance. methodname is one of the pre-defined methods in Evolver. The modulus value multiplies the method value to give the instance value. The default modulus is 1. Individual elements may be given multipliers by specifying an extra attribute attrname for the type of element; the attribute must have been defined earlier. GLOBAL makes the method apply to all elements of the appropriate type. Non-global instances may be applied to elements individually by adding the instance name to the datafile line defining an element. They may also be applied or unapplied at runtime with the set and unset commands. Orientable methods can be applied with negative orientation in the datafile by following the name with a dash. The orientation of individual elements may be set at runtime with the "set" command, for example
Each method may have various parameters to specialize it to an instance. Currently the only parameters specified are:

SCALAR_INTEGRAND: expr

where expr is a scalar function of coordinates (and of tangent or normal vector components in edge_general_integral or facet_general_integral). Element attributes of the appropriate type element may also be used.

VECTOR_INTEGRAND:
Q1: expr
Q2: expr
Q3: expr

where the expressions are functions of the coordinates. Element attributes of the appropriate type element may also be used.

FORM_INTEGRAND:
Q1: expr
Q2: expr
Q3: expr
...

where the expressions are functions of the coordinates. Element attributes of the appropriate type element may also be used. When used in the facet_2form_integral method. The form components are listed in lexicographic order, i.e. in 4D the six components 12,13,14,23,24,34 would be listed as Q1 through Q6.

PARAMETER_1 constexpr

For specifying miscellaneous numeric parameters to certain methods.

K_FORM_ORDER constexpr

For methods that use differential k-forms, this specifies the value of k. Should occur before FORM_INTEGRAND when needed.

## Surface dimension
The default dimension of the surface is 2. If not, it must be declared in the top section of the datafile. For a 1-dimensional surface (the string model), simply include the line

```text
 STRING


```
The default dimension 2 soapfilm model is equivalent to using

```text
 SOAPFILM


```
In general, the line

```text
 SURFACE_DIMENSION n


```
defines the surface to have dimension n. Dimension over 2 is valid only in the simplex model. The surface dimension may be accessed at runtime through the read-only variable surface_dimension.

## Space dimension
The default dimension of space is 3. Otherwise it must be declared in the top section of the datafile, with syntax

```text
SPACE_DIMENSION n


```
The dimension must be at most the value of MAXCOORD in model.h, which is 4 in the distributed version. The space dimension may be accessed at runtime through the read-only variable space_dimension.

## Extra attribute declarations
It is possible for the user to define extra attributes for elements, which may be single values or up to eight-dimensional arrays. If these attributes are to be included in the datafile, then the top section of the datafile must contain appropriate definitions. The definition syntax is the same as used by the define runtime command:

```text
 DEFINE elementtype ATTRIBUTE name type [dim]...


```
where elementtype is vertex, edge, facet, or body, name is an identifier of your choice, type is REAL or INTEGER (internally, there is also a ULONG unsigned long type also), and dim is an optional expression for the vector dimension. There is no practical distinction between real and integer types at the moment, since everything is stored internally as reals. But there may be more datatypes added in the future. Extra attributes are inherited by elements of the same type generated by subdivision. The type may be followed by FUNCTION followed by a procedure in brackets to be evaluated whenever the value of the attribute is read; in the formula, self may be used to refer to the element in question to use its attributes, in particular to at some point assign a value to the attribute. The print command may be used to print attribute arrays or array slices in bracketed form. Examples: WARNING: there is a syntax ambiguity if you mean to define a stand-alone function in the top of the datafile and put it after an attribute declaration. You should define stand-alone functions before attributes, or separate them with some other kind of declaration.

## Quadratic declaration
To declare that the datafile lists a surface in the quadratic model, the top section of the datafile should contain the line

```text

QUADRATIC


```
The only effect on datafile syntax is that the edge section may list edge midpoint vertices.

## Gravity constant declaration
The initial value of the gravitational constant may be set in the datafile with the syntax

```text
  GRAVITY_CONSTANT value

```
The default value is 1.

## Torus model declaration
To declare periodic boundary conditions (i.e. make the domain a flat torus), include in the top section of the datafile the line

```text

TORUS


```
All space dimensions will be periodic, with the period vectors given in the periods declaration. If the domain is completely filled by bodies with prescribed volumes, then the line

```text

TORUS_FILLED


```
should be used instead to prevent degenerate volume constraints.

## Torus periods
If periodic boundary conditions are used (the torus model) , the period vectors of the fundamental unit cell parallelpiped may be defined in the top section of the datafile. Default is the unit cube. The syntax is the keyword PERIODS followed by expressions for the components of each period vector:

```text
PERIODS
expr expr expr
expr expr expr
expr expr expr


```
The size of this matrix depends on the space dimension. Variables may be used in the expressions, so the fundamental domain may be changed interactively by assigning new values to the variables. Be sure to give a recalc command whenever you change such a variable, in order to get the period matrix re-evaluated.

## Viewing matrix
The top section of the datafile may contain an initial viewing matrix:

```text

VIEW_MATRIX
  constexpr constexpr constexpr constexpr
  constexpr constexpr constexpr constexpr
  constexpr constexpr constexpr constexpr
  constexpr constexpr constexpr constexpr


```
The matrix is in homogeneous coordinates with translations in the last column. The size of the matrix is one more than the space dimension. This matrix will be part of all dump files, so the view can be saved between sessions. This matrix is used and set by native screen graphics ('s' command) and only applies to internal graphics (Postscript, Xwindows, etc.) but not external graphics (geomview). The elements may be read or set at runtime by view_matrix[i][j], where the indices start at 1. In particular, one can write command scripts to save and reload particular view matrices; see saveview.cmd in the distribution package.

## View transforms
For the display of several transformations of the surface simultaneously, a number of viewing transformation matrices may be given in the top section of the datafile:

```text

VIEW_TRANSFORMS n
COLOR color
SWAP_COLORS
  constexpr constexpr constexpr constexpr
  constexpr constexpr constexpr constexpr
  constexpr constexpr constexpr constexpr
  constexpr constexpr constexpr constexpr
    ...


```
The transforms apply to all graphics, internal and external, and are prior to the viewing matrix for internal graphics. The identity transform is always done, so it does not need to be specified. The number of matrices follows the keyword VIEW_TRANSFORMS. Each matrix is in homogeneous coordinates, with translation in the last column. The size of each matrix is one more than the space dimension. Individual matrices need no special separation; Evolver just goes on an expression reading frenzy until it has all the numbers it wants. Each matrix may be preceded by an optional color that applies to facets transformed by that matrix. The color applies to one transform only; it does not continue until the next color specification. If SWAP_COLORS is present instead, facet frontcolor and backcolor will be swapped when this matrix is applied. Transforms may be activated or deactivated interactively with the transforms toggle. The internal variable transform_count records the number of transforms, and the transform matrices are accessible at runtime as a three-dimensional matrix view_transforms[][][]. View transform generators are a more sophisticated way to control view transforms.

## View transform generators
Listing all the view transforms is tedious and inflexible. An alternative is to list just a few matrices that can generate transforms. See the transform_expr command for instructions on entering the expression that generates the actual transforms. Special Note: in the torus model, the period translations are automatically added to the end of the list. So in the torus model, these are always available, even if you don't have view_transform_generators in the datafile. Syntax in the top of the datafile:

```text

VIEW_TRANSFORM_GENERATORS n
SWAP_COLORS
  constexpr constexpr constexpr constexpr
  constexpr constexpr constexpr constexpr
  constexpr constexpr constexpr constexpr
  constexpr constexpr constexpr constexpr
    ...


```
The number of matrices follows the keyword VIEW_TRANSFORM_GENERATORS. Each matrix is in homogeneous coordinates, with translation in the last column. The size of each matrix is one more than the space dimension. Individual matrices need no special separation; Evolver just goes on an expression reading frenzy until it has all the numbers it wants. If SWAP_COLORS is present, facet frontcolor and backcolor will be swapped when this matrix is applied. The internal variable transform_count records the number of transforms, and the transform matrices are accessible at runtime as a three-dimensional matrix view_transforms[][][].

## Scale limit
To set an upper bound of value on the gradient descent scale factor, include the line

```text

   SCALE_LIMIT value


```
in the top section of the datafile. The upper bound can be changed at runtime with the m command, or by setting the scale_limit variable. If surface tension is the main energy, the scale_limit should be set to the inverse of the surface tension.

## Functions and procedures
Usually stand-alone user-defined functions and procedures are defined in the read section of the datafile, but sometimes it is necessary to define them in the top section of the datafile so they may be used in other top section declarations. It is possible to define them in the top section with the same syntax as in the read section. Note this applies to the parameter-passing variety of functions and procedures, denoted by the leading keyword "function" or "procedure", and not command definitions like "gg := {...}". WARNING: there is a syntax ambiguity if you mean to define a stand-alone function in the top of the datafile and put it after an attribute declaration. You should define stand-alone functions before attributes, or separate them with some other kind of declaration.

## Optimizing parameter
A variable may be made subject to optimization during iteration or hessian commands with the datafile declaration

```text

      OPTIMIZING_PARAMETER identifier = constexpr PDELTA = constexpr PSCALE = constexpr


```
Such a variable joins the vertex coordinates as an independent variable during optimization. However, it differs from a coordinate in that gradients with respect to it are calculated numerically, rather than analytically. Thus it may be used anywhere a variable is permitted. Hessians with optimizing parameters are implemented. The optional pdelta value is the parameter difference to use in finite differences; the default value is 0.0001. The optional pscale value is a multiplier for the parameter's motion, to do "impedance matching" of the parameter to the surface energy. These attributes may be set on any parameter, for potential use as an optimizing parameter. At runtime, a parameter may be toggled to be optimizing or not with the FIX and UNFIX commands. That is, fix radius would make the radius variable non-optimizing (fixed value). Also, the pdelta and pscale attributes may be accessed at runtime, as in

```text

height.pscale := 2*height.pscale


```
At runtime, one may use the p_force attribute of the variable to find the rate of change of energy with respect to the variable before constraint corrections, and the p_velocity attribute to find the rate of change of the variable with respect to the scale factor of the 'g' command. Example:
"Optimising_parameter" is a synonym.

## Gap constant declaration
The initial value of the gap constant for gap energy may be set in the datafile with the syntax

```text
  GAP_CONSTANT value

```
The default value is 1. Synonym: spring_constant.

## Symmetric content
The datafile keyword SYMMETRIC_CONTENT triggers the use of an alternate surface integral for calculating body volumes, namely the vectorfield (x,y,z)/3. It is useful if unmodelled sides of a body are radial from the origin, or if constraint content integrals (which is evaluated by an approximation) lead to asymmetric results on what should be a symmetric surface.

## Keep original ids
The presence of the keyword

```text

keep_originals


```
in the top of the datafile has the same effect as the -i command line option, which is to keep the id numbers internally the same as in the datafile, instead of renumbering them in the order they are read in.

## Version
If a datafile contains features present only after a certain version of the Evolver, the datafile can contain a line of the form
evolver_version "2.10"
This will generate a version error message if the current version is earlier, or just a syntax error if run on an Evolver version earlier than 2.10.

## Constraint tolerance
This is datafile declaration of the tolerance within which a vertex is deemed to satisfy a level-set constraint. Default is 1e-12. Syntax:

```text
  CONSTRAINT_TOLERANCE const_expr

```
Sets the value of the internal variable constraint_tolerance.

## Symmetry group declaration
To declare that the domain is the quotient space of a symmetry group, the top section of the datafile must contain a line of the form

```text

SYMMETRY_GROUP "name"


```
" name " is a double-quoted name that is matched against the list of defined symmetry groups.

## Length method
This item, length_method_name, specifies the name of the pre-defined method to use as the method to compute edge length in place of the default edge_length method. It is optional. Developed so circular arcs can be used in two-dimensional foams. Current reasonable methods are circular_arc_length and spherical_arc_length. Usage implies converting to everything_quantities mode. Syntax:

```text

length_method_name quoted_method_name


```
For example,

## Area method
This item, area_method_name, specifies the name of the pre-defined method to use as the method to compute facet areas in place of the default edge_area method in the string model or facet_area method in the soapfilm model. It is optional. Developed so circular arcs can be used in two-dimensional foams. Current reasonable methods are circular_arc_area and spherical_arc_area. Synonymous with volume_method_name in the string model. Usage implies converting to everything_quantities mode. Syntax:

```text

area_method_name quoted_method_name


```
For example,

## Volume method
This item, volume_method_name, specifies the name of the pre-defined method to use as the method to compute body volumes in place of the default edge_area method in the string model or facet_volume method in the soapfilm model. It is optional. Developed so circular arcs can be used in two-dimensional foams. Synonymous with area_method_name in the string model. Usage implies converting to everything_quantities mode. Syntax:

```text

volume_method_name quoted_method_name


```
For example,

## Hessian special normal vector
When hessian_special_normal is on, hessian commands use a special vectorfield for the direction of the perturbation, rather than the usual surface normal. The vectorfield is specified in the format

```text

HESSIAN_SPECIAL_NORMAL_VECTOR
c1: expr
c2: expr
c3: expr


```
One can use vertex attributes in the expressions. Beware that hessian_special_normal also applies to the normal calculated by the vertex_normal attribute and the normal used by regular vertex averaging.

## Simplex model declaration
To declare that the datafile lists a surface in the simplex model, the top section ot the datafile should contain the line

```text

SIMPLEX_REPRESENTATION


```
The main effect on the datafile is that faces are defined by oriented vertex lists rather than edge lists.

## Diffusion
The Evolver can simulate the real-life phenomenon of gas diffusion between neighboring bubbles. This diffusion is driven by the pressure difference across a surface. This is invoked by the keyword DIFFUSION in the first part of the datafile, followed by the value of the diffusion constant, which is the internal variable diffusion_coeff.

```text

    DIFFUSION 0.1


```
The amount diffused across a facet during an iteration is calculated as scale*diffusion_coeff*facet_area*pressure_difference. The scale factor is included as the time step of an iteration. The amount is added to or subtracted from the prescribed volumes of the bodies on either side of the facet.
If you want finer control over the rate of diffusion across various surfaces, you can define the edge_diffusion edge attribute in the string model or the facet_diffusion facet attribute in the soapfilm model and give individual values for edges or facets as you desire. If the attribute is defined, then its value is used instead of the global diffusion constant.
Diffusion can be toggled at runtime with the "diffusion" toggle command.

## Dynamic load library
To load a dynamic library of compiled functions, the syntax is

```text

 LOAD_LIBRARY "filename"


```
where the double-quoted filename is the library. The current directory and the EVOLVERPATH will be searched for the library.

## Crystalline integrands
To declare that surface area energy should be calculated with a crystalline integrand, the top section of the datafile should contain a line of the form

```text

 WULFF "filename"


```
The double-quoted filename (with path) refers to a file giving the Wulff vectors of the integrand. The format of the file is one Wulff vector per line with its components in ASCII decimal format separated by spaces. The first blank line ends the specification. Some special integrands can be used by giving a special name in place of the file name. Currently, these are "hemisphere" for a Wulff shape that is an upper unit hemisphere, and "lens" for two unit spherical caps of thickness 1/2 glued together on a horizontal plane. These two don't need separate files.

## Phase file declaration
To declare that the surface tension of an edge or facet depends on the phases of its adjacent facets or bodies, the top section of the datafile should contain a line of the form

```text

 PHASEFILE "filename"


```
The information is read from an ASCII file, whose name is given in a double-quoted string. The first line of the file has the number of different phases. Each line after consists of two phase numbers and the surface tension between them. Lines not starting with a pair of numbers are taken to be comments. If a pair of phases is not mentioned, the surface tension between them is taken to be 1.0. Facets in the string model or bodies in the soapfilm model can be labelled with phases with the PHASE n phrase in the datafile.

## Ideal gas model
A line in the top section of the datafile of the form

```text

PRESSURE constexpr


```
specifies that bodies are compressible and the ambient pressure is the value of constexpr. The default is that bodies with given volume are not compressible.

## Interpolation of parameters
To use interpolation instead of extrapolation in calculating the parameters of edge midpoints during refining, use the keyword

```text
   INTERP_BDRY_PARAM


```
This should be done only if there are no periodic parameters.

## Everything_quantities
Keyword in top section of the datafile. Causes all areas, volumes, etc. to be converted to named quantities and methods. Equivalent to the command line option -q, or the convert_to_quantities command.

## Mobility declaration
A mobility matrix may be defined in the top section of the datafile by the syntax

```text

MOBILITY_TENSOR
expr expr expr
expr expr expr
expr expr expr


```
or

```text

MOBILITY expr


```
The first form gives the full mobility matrix, and the second form gives the matrix as a scalar multiple of the identity matrix. The formulas are evaluated at each vertex at each iteration, and so formulas may depend on vertex position and any vertex attributes.

## Metric declaration
A Riemannian metric on the ambient space may be declared in the top section of the datafile with the syntax

```text
METRIC
expr expr expr
expr expr expr
expr expr expr


```
or

```text

CONFORMAL_METRIC expr


```
or

```text

KLEIN_METRIC


```
The keyword METRIC is followed by the N^2 components of the metric tensor, where N is the dimension of space. The components do not have to obey any particular line layout; they may be all on one line, or each on its own line, or any combination. It is up to the user to maintain symmetry. A conformal metric is a scalar multiple of the identity matrix, and only the multiple need be given. A conformal metric will run about twice as fast. The Klein metric is a built-in metric for hyperbolic n-space modelled on the unit disk or ball.

## Merit factor
If the keyword MERIT_FACTOR is present, then the i command will print the ratio total_area^3/total_volume^2, which measures the efficiency of area enclosing volume. A holdover from the early days of trying to beat Kelvin's partition of space.

## Squared mean curvature
To add an energy of squared mean curvature, include a line in the top of the datafile

```text
  SQUARED_CURVATURE modulus


```
The modulus is a multiplier for the energy, and is available at runtime in the read-write variable sq_curvature_modulus. This is the original squared mean curvature energy; later versions are in the squared curvature named methods.
In the string model, the power of the curvature is controlled by the internal read-write variable curvature_power.

## Squared Gaussian curvature
To add an energy of squared Gaussian curvature, include a line in the top of the datafile

```text
  SQUARED_GAUSSIAN_CURVATURE modulus


```
The modulus is a multiplier for the energy, and is available at runtime in the read-write variable square_gauss_modulus. Synonyms: Synonyms: square_gaussian_curvature, sqgauss

## Zoom_vertex
Datafile keyword setting the current zoom vertex. Used in dump files after a zoom command has been given.

## Zoom_radius
Datafile keyword setting the current zoom radius. Used in dump files after a zoom command has been given.

## Suppress_warning
Datafile keyword instructing Evolver not to print a certain warning. Syntax:

```text

  SUPPRESS_WARNING number


```
where number is the number of the warning. Meant to suppress irritating warning messages that you know are irrelevant. Warnings can be restored with the syntax

```text

  UNSUPPRESS_WARNING number


```

## Vertices_predicted
Datafile keyword in the top section of the datafile that specifies the initial allocation of vertex structures. Optional. The purpose is to prevent repeated reallocation of memory as the vertex list grows or as the surface evolves. Should be faster, and prevents memory fragmentation. Automatically put in dump files by the d or dump commands, based on the current number of vertices. Example:

## Edges_predicted
Datafile keyword in the top section of the datafile that specifies the initial allocation of edge structures. Optional. The purpose is to prevent repeated reallocation of memory as the edge list grows or as the surface evolves. Should be faster, and prevents memory fragmentation. Automatically put in dump files by the d or dump commands, based on the current number of edges. Example:

## Facets_predicted
Datafile keyword in the top section of the datafile that specifies the initial allocation of facet structures. Optional. The purpose is to prevent repeated reallocation of memory as the facet list grows or as the surface evolves. Should be faster, and prevents memory fragmentation. Automatically put in dump files by the d or dump commands, based on the current number of facets. Example:

## Bodies_predicted
Datafile keyword in the top section of the datafile that specifies the initial allocation of body structures. Optional. The purpose is to prevent repeated reallocation of memory as the facet list grows or as the surface evolves. Should be faster, and prevents memory fragmentation. Automatically put in dump files by the d or dump commands, based on the current number of bodies. Example:

## Facetedges_predicted
Datafile keyword in the top section of the datafile that specifies the initial allocation of facetedge structures. Optional. The purpose is to prevent repeated reallocation of memory as the facetedge list grows or as the surface evolves. Should be faster, and prevents memory fragmentation. Automatically put in dump files by the d or dump commands, based on the current number of facetedges. Example:

## Quantities_predicted
Datafile keyword in the top section of the datafile that specifies the initial allocation of named quantity structures. Optional. The purpose is to prevent repeated reallocation of memory as the quantity list grows. Not significant if there are only a few quantities, but there are times when there can be thousands of quantities, such as when "everything_quantities" is used with a large foam. Automatically put in dump files by the "d" or "dump" commands, based on the current number of quantities. This declaration obviously should come before any quantities are defined. Example:

## Method_instances_predicted
Datafile keyword in the top section of the datafile that specifies the initial allocation of method instance structures. Optional. The purpose is to prevent repeated reallocation of memory as the instance list grows. Not significant if there are only a few method instances, but there are times when there can be thousands of instances, such as when "everything_quantities" is used with a large foam. Automatically put in dump files by the "d" or "dump" commands, based on the current number of method instances. This declaration obviously should come before any quantities are defined. Example:

## Element lists
The lists of geometric elements follow a general format. Each element is defined on one line. The first entry on a line is the element number. Numbering need not be consecutive, and may omit numbers, but be aware that internally elements will be renumbered in order. The original number in the datafile is accessible as the original attribute of an element. After the element number comes the basic defining data, followed by optional attributes in arbitrary order. Besides the particular attributes for each element type listed below, one may specify values for any extra attributes defined earlier. The syntax is attribute name followed by the appropriate number of values. Also an arbitrary number of named quantities or method instances may be listed. These add method values for this element to the named quantity. The named quantity or instance must have been declared in the top section of the datafile.

## Vertex list
The datafile vertex list is started by the keyword VERTICES at the start of a line. It is followed by lines with one vertex specification per line. If the vertex is not on a parametric boundary, the syntax is

```text

k   x y ... [FIXED] [CONSTRAINT c1 c2 ...]  [BARE]
            [quantityname ...] [methodname ...]


```
The syntax for a vertex on a parametric boundary is

```text

k p1 [p2 ...]  BOUNDARY b [FIXED] [BARE] [quantityname ...]
   [methodname ...]


```
Here k is the vertex number, a positive integer. Vertices do not need to be listed in order, and there may be gaps in the numbering. However, if they are not in consecutive order, then the numbering in dump files will be different. x y ... are constant expressions for coordinates. In the parametric boundary format, the boundary parameter values are given instead of the coordinates. If FIXED is given, then the vertex never moves, except possibly for an initial projection to constraints. If CONSTRAINT is given, then one or more constraint numbers must follow. You can list as many constraints as you want, as long as those that apply exactly at any time are consistent and independent. The given coordinates need not lie exactly on the constraints; they will be projected onto them. A vertex on a parametric boundary cannot also be on a constraint.
The BARE attribute is just an instruction to the checking routines that this vertex is not supposed to have an adjacent facet in the soapfilm model, so spurious warnings will not be generated. This is useful when you want to show bare wires or outline fundamental domains.
An arbitrary number of named quantities or method instances may be listed. These add method values for this element to the named quantity. The named quantity or instance must have been declared in the top section of the datafile.
The list vertices command prints the datafile format listing of vertices.

## Edge list
The datafile edge list follows the vertex list, and is started by the keyword EDGES at the start of a line. It is followed by lines with one edge specification per line in this format (linespliced here):

```text

k v1 v2 [midv] [s1 s2 s3] [WRAP w] [FIXED] [BOUNDARY b] \
   [CONSTRAINTS c1 [c2 ...]] [TENSION constexpr] [COLOR n] \
     [BARE]  [quantityname ...] [methodname ...]


```
Here k is the edge number, with numbering following the same rules as for vertices. v1 and v2 are the numbers of the tail and head vertices of the edge. In the quadratic model, the edge midpoint may be listed as a third vertex midv (otherwise a midpoint vertex will be created). In the torus model, there must follow signs s1 s2 s3 indicating how the edge wraps around each unit cell direction: + for once positive, * for none, and - for once negative. In non-torus symmetry groups, each edge should have a WRAP symmetry group element encoded as an integer. FIXED means that all vertices and edges resulting from subdividing this edge will have the FIXED attribute; it does not mean that the endpoints will be automatically fixed. Likewise the BOUNDARY and CONSTRAINT attributes will be inherited by all edges and vertices derived from this edge. If a constraint has energy or content integrands, these will be done for this edge. IMPORTANT: If a constraint number is given as negative, the edge energy and content integrals will be done in the opposite orientation. In the string model, the default tension is 1, and in the soapfilm model, the default tension is 0. However, edges may be given nonzero tension in the soapfilm model, and they will contribute to the energy.
If the simplex model is in effect, edges are one less dimension than facets and given by an ordered list of vertices. Only edges on constraints with integrals need be listed.
The BARE attribute is just an instruction to the checking routines that this ede is not supposed to have an adjacent facet in the soapfilm model, so spurious warnings will not be generated. This is useful when you want to show bare wires or outline fundamental domains.
An arbitrary number of named quantities or method instances may be listed. These add method values for this element to the must have been declared in the top section of the datafile. If the quantity or instance has orientation-dependent methods, the name may be followed by a dash to reverse the applied orientation.
The list edges command prints the datafile format listing of edges.

## Face list
The datafile face list follows the edge list, and is started by the keyword FACES at the start of a line. It is followed by lines with one facets specification per line in this format:

```text

  k   e1 e2 ...  [FIXED] [TENSION constexpr] [BOUNDARY b] \
  [CONSTRAINTS c1 [c2 ...]]     [NODISPLAY]   \
   [COLOR n]} [FRONTCOLOR n] [BACKCOLOR n] \
   [PHASE n] [quantityname ...] [methodname ...]


```
Here k is the face number, with numbering following the same rules as for vertices. There follows a list of oriented edge numbers in counterclockwise order around the face. A negative edge number means the opposite orientation of the edge from that defined in the edge list. The head of the last edge must be the tail of the first edge (except if you're being tricky in the string model). There is no limit on the number of edges. The face will be automatically subdivided into triangles if it has more than three edges in the soapfilm model. The TENSION (synonym: DENSITY) value is the energy per unit area (the surface tension) of the facet; the default is 1. Density 0 facets exert no force, and can be useful to define volumes or in displays. Fractional density is useful for prescribed contact angles. NODISPLAY prevents the facet from being displayed. The COLOR attribute applies to both sides of a facet; FRONTCOLOR applies to the positive side (edges going counterclockwise) and BACKCOLOR to the negative side. The PHASE number is used in the string model to determine the surface tension of edges between facets of different phases, if phases are used.
If the simplex model is in effect, the edge list should be replaced by an oriented list of vertex numbers.
An arbitrary number of named quantities or method instances may be listed. These add method values for this element to the must have been declared in the top section of the datafile. If the quantity or instance has orientation-dependent methods, the name may be followed by a dash to reverse the applied orientation.
The faces section is optional in the string model.
The list facets command prints the datafile format listing of facets.

## Body list
The datafile body list follows the face list, and is started by the keyword BODIES at the start of a line. It is followed by lines with one body specification per line in this format:

```text

k  f1 f2 f3 .... [VOLUME constexpr] [VOLCONST constexpr] [ACTUAL_VOLUME constexpr] \
[PRESSURE p] [DENSITY constexpr] [PHASE ]


```
Here k is the body number, and f1 f2 f3 ... is an unordered list of signed facet numbers. Positive sign indicates that the facet normal (as given by the right-hand rule from the edge order in the facet list) is outward from the body and negative means the normal is inward. Giving a VOLUME value constexpr means the body has a volume constraint, unless the ideal gas model is in effect, in which case constexpr is the volume at the ambient pressure. VOLCONST is a value added to the volume; it is useful when the volume calculation from facet and edge integrals differs from the true volume by a constant amount, as may happen in the torus model. ACTUAL_VOLUME is a number that can be specified in the rare circumstances where the torus volume volconst calculation gives the wrong answer; volconst will be adjusted to give this volume of the body. Giving a PRESSURE value means that the body is deemed to have a constant internal pressure; this is useful for prescribed mean curvature problems. It is incompatible with prescribed volume. Giving a DENSITY value means that gravitational potential energy will be included.
To endow a facet with VOLUME, PRESSURE, or DENSITY attributes in the string model, define a body with just the one facet.
The PHASE number is used in the soapfilm model to determine the surface tension of facets between bodies of different phases, if phases are used.
The BODIES section is optional.
The list bodies command prints the datafile format listing of bodies.

## READ section
The final section of the datafile may contain commands. These commands are read and executed immediately, just as if they had been entered at the command prompt. Encountering the keyword READ in the datafile causes the Evolver to switch from datafile mode to command mode and read the rest of the datafile as command input. This feature is useful for automatic initialization of the surface with refining, iteration, defining your own commands, etc. The READ section is optional. Example: The list bottominfo command prints the READ section that would be printed in a dump file. Back to top of Surface Evolver documentation. Index.
An example file is below:
```text
// 3.fe   Evolver initial data for 3 bubbles around two.
// Main problem in evolving is that inner film between the
// axial bubbles shrinks to a point, and the resulting vertex
// needs to be popped.  See the gogo command below.

vertices //     coordinates
  1      0.877383  0.000000  1.000000
  2      0.877383  0.000000  0.000000
  3      0.877383  0.000000  -1.000000
  4      2.057645  0.000000  -1.000000
  5      2.057645  0.000000  1.000000
  6      -0.438691  -0.759836  1.000000
  7      -0.438691  -0.759836  0.000000
  8      -0.438691  -0.759836  -1.000000
  9      -1.028822  -1.781973  -1.000000
 10      -1.028822  -1.781973  1.000000
 11      -0.438691  0.759836  1.000000
 12      -0.438691  0.759836  0.000000
 13      -0.438691  0.759836  -1.000000
 14      -1.028822  1.781973  -1.000000
 15      -1.028822  1.781973  1.000000

edges  // endpoints
  1       1    2
  2       2    3
  3       3    4
  4       4    5
  5       5    1
  6       1    6
  7       2    7
  8       3    8
  9       4    9
 10       5   10
 11       6    7
 12       7    8
 13       8    9
 14       9   10
 15      10    6
 16       6   11
 17       7   12
 18       8   13
 19       9   14
 20      10   15
 21      11   12
 22      12   13
 23      13   14
 24      14   15
 25      15   11
 26      11    1
 27      12    2
 28      13    3
 29      14    4
 30      15    5

faces //   edges    
  1      1   2   3   4   5 
  2      6  11  -7  -1 
  3      7  12  -8  -2 
  4      8  13  -9  -3 
  5     10 -14  -9   4 
  6      6 -15 -10   5 
  7     11  12  13  14  15 
  8     16  21 -17 -11 
  9     17  22 -18 -12 
 10     18  23 -19 -13 
 11     20 -24 -19  14 
 12     16 -25 -20  15 
 13     21  22  23  24  25 
 14     26   1 -27 -21 
 15     27   2 -28 -22 
 16     28   3 -29 -23 
 17     30  -4 -29  24 
 18     26  -5 -30  25 
 19    -26  -16   -6  
 20    -27  -17   -7  
 21    -28  -18   -8  

bodies    //     facets 
  1     -1   -2   -3   -4    5    6    7     volume  3.000000  
  2     -7   -8   -9  -10   11   12   13     volume  3.000000  
  3    -13  -14  -15  -16   17   18    1     volume  3.000000  
  4     19    2    8   14  -20     volume  1.000000
  5     20    3    9   15  -21     volume  1.000000

read

hessian_normal  // makes hessian work better

// prettify things, run once after loading
pretty := {
l 3;
refine edge where id==6 or id==16 or id==26 or id==8 or id==18 or id==28
  or id==7 or id==17 or id==27;  // around inner bubbles
u; // symmetrizes things
}

// a quick way to color the bodies 
colorbodies := { set facet ff color max(ff.body,id); }

// to see inner surfaces
showinner := { show facets ff where sum(ff.body,1) == 2; }

// an evolution, as run after loading 
gogo := { pretty; // improve the mesh
          g 5;   // just to get things started
          t 0.2; // get rid of some shrinking edges
	  showinner;  // where the action is
	  V; V;  // even out vertices
          g 10;
	  V; V; g 3;  // a couple of g's before hessian_seek
	  hessian_seek; hessian_seek;
          r;
          g 12;
          V; V; V; // scale was down; even out the vertices
          g 5;  // scale good again
          U; g 20; t .02; g 10; t .02; g 10; t .02; // collapse at center
	  o;   // pop center vertex
	  U;  // conj grad off
	  g 10; V 2;u;V;u;V;u; g 12; t .01;
	  refine edge[22]; refine edge[162]; // from picking
	  t .02; g 10 ; t .02; U; g 10 ; V 2; g 10;
	  hessian_seek; hessian_seek; t .02; t .03; t .04; t .05;
	  w .003; g 5; w .003; t .111; // now looking pretty good
	  g 10; hessian_seek; hessian_seek; // converged
	  r; g 10; hessian_seek; hessian_seek;  // converged

}        
```