Surface Evolver Documentation: named quantities

# Surface Evolver Documentation
Back to top of Surface Evolver documentation. Index.

## Named quantities and methods
This is the systematic scheme of calculating global quantities such as area, volume, and surface integrals that replaces the original ad hoc scheme in the Evolver. Briefly, methods are built-in functions, and named quantities are combinations of instances of methods. See the ringblob datafile for an example. The original ad hoc calculations are still the default where they exist, but all new quantities are being added in the named quantity scheme. Some new features will work only with named quantities. To convert everything to named quantities, start Evolver with the -q option or use the convert_to_quantities command. This has not been made the default since named quantities can be slower than the originals.
The sample datafiles qcube.fe, qmound.fe, and ringblob.fe contains some examples of named quantities and instances. The first two are quantity versions of cube.fe and mound.fe. These illustrate the most general and useful methods, namely facet_vector_integral, facet_scalar_integral, and edge_vector_integral, rather than the faster but more specialized methods such as facet_area. My advice is that the user stick to the old implicit methods for area, volume, and gravitational energy, and use named quantities only for specialized circumstances.

### Chapter contents:

- Named methods
- Method instances
- Named quantities
- Implemented methods

## Named methods
A "method" is a way of calculating a scalar value from some particular type of element (vertex, edge, facet, body). Each method is implemented internally as a set of functions for calculating the value and its gradient as a function of vertex positions. The most common methods also have Hessian functions. Methods are referred to by their names.
See Implemented methods for a list of available methods. Adding a new method involves writing C routines to calculate the value and the gradient (and maybe the Hessian) as functions of vertex coordinates, adding the function declarations to quantity.h, and adding a structure to the method declaration array in quantity.c. All the other syntax for invoking it from the datafile is already in place.

## Method instances
A "method instance" is the sum of a particular method applied to a particular set of geometric elements. Some methods (like facet_area) are completely self-contained. Others (like facet_vector_integral) require the user to specify some further information. For these, each instance has a specification of this further information. Method instances are defined in the datafile, and may either be unnamed parts of named quantity definitions or separate named method instances for inclusion in named quantities. The separate named version is useful if you want to inspect instance values for the whole surface or individual elements. An instance total value can be printed with the A commands, or may be referred to as "instancename.value" in commands. The instance name itself may be used as an element attribute. For example, supposing there is an instance named moment, which applies to facets. Then typical commands would be Modulus. Every method instance has a "modulus", which is multiplied times the basic method value to give the instance value. A modulus of 0 causes the entire instance calculation to be omitted whenever quantities are calculated. The modulus may be set in the datafile or with the A command or by assignment. Example commands: A method instance may be declared to use a different modulus for each element by specifying an element extra attribute to use for that purpose. The extra attribute has to have already been declared. Example: Of course, it is up to the user to properly initialize the values of the extra attribute.
Orientation. Some methods, those that logically depend on the orientation of the element, can be applied with a relative orientation. When applied to individual elements in the datafile, a negative orientation is indicated by a '-' after the instance name. When applied at runtime with the set command, the orientation will be negative if the element is generated with negative orientation, i.e. set body[1].facet method_instance qqq. The methods currently implementing this feature are: edge_vector_integral, string_gravity, facet_vector_integral, facet_2form_integral, facet_volume, facet_torus_volume, simplex_vector_integral, simplex_k_vector_integral, edge_k_vector_integral, gravity_method, and full_gravity_method.

## Named quantities
A "named quantity" is the sum total of various method instances, although usually just one instance is involved. The instances need not apply to the same type of element; for example, both facet and edge integrals may be needed to define a volume quantity. Each named quantity is one of four types:

- "energy" quantities which are added to the total energy of the surface;
- "fixed" quantities that are constrained to a fixed target value (by Newton steps at each iteration); and
- "conserved" quantities are like fixed, but the value is irrelevant. The quantity gradient is used to eliminate a degree of freedom in motion. Rarely used, but useful to eliminate rotational degree of freedom, for example. Will not work with optimizing parameters, since they do gradients by differences.
- "info_only" quantities whose values are merely reported to the user.
This type is initially set in a quantity's datafile declaration. A quantity can be toggled between fixed and info_only with the " fix quantityname " and " unfix quantityname " commands.
The value of a quantity may be displayed with the A or v commands, or as an expression "quantityname.value". Furthermore, using the quantity name as an element attribute evaluates to the sum of all the applicable component instance values on that element. For example, supposing there is a quantity named vol, one could do
Modulus. Each quantity has a "modulus", which is just a scalar multiplier for the sum of all instance values. A modulus of 0 will turn off calculation of all the instances. The modulus can be set in the datafile declaration, with the A command, or by assignment:

```text
 quantityname.modulus := 1.2

```

Target value. Each fixed quantity has a target value, to which the Evolver attempts to constraint the quantity value. Each time an iteration is done ( g command or the various Hessian commands), Newton's Method is used to project the surface to the constrained values. The target value can be displayed with the A or v commands, or as "quantityname.target". It can be changed with the A command or by assignment. Example:
Volconst. A quantity can have a constant value added to it, similar to the body attribute volconst. This quantity attribute is also called volconst. It is useful for adding in known values of say integrals that are omitted from the actual calculation. It can be set in the quantity's datafile definition, or by an assignment command.
Pressure. Each fixed quantity has a Lagrange multiplier associated to it. The Lagrange multiplier of a constraint is the rate of energy change with respect to the constraint target value. For a volume constraint, the Lagrange multiplier is just the pressure. Lagrange multipliers are calculated whenever an iteration step is done. They may be displayed with the v command in the " pressure " column, or as an expression "quantityname.pressure".
Tolerance. A fixed quantity can have a tolerance attribute, which is used to judge convergence. A surface is deemed converged when the sum of all ratios of quantity discrepancies to tolerances is less than 1. This sum also includes bodies of fixed volume. If the tolerance is not set or is negative, the value of the variable target_tolerance is used, which has a default value of 0.0001.
Function quantities. Instead of being a simple sum of methods, a named quantity can be an arbitrary function of named method values. The datafile syntax has "function expression" instead of a method list. For example: Note the method name is used with a "value" suffix. Also note that the method values used are global values, not element-wise. Quantity functions can do Hessian operations, if the component methods have Hessians. Such hessians can become quite memory consuming in default dense matrix form; there is a toggle command function_quantity_sparse that will cause sparse matrices to be used.
Example. The sample datafile column.fe contains some examples of named quantities and instances.
Future. It is planned that eventually all energies and global constraints will be converted to named quantity system. However, existing syntax will remain valid wherever possible. Starting Evolver with the -q option will do this conversion now.

## Implemented methods
The currently implemented methods are listed here, grouped somewhat by nature.

#### 0-dimensional

- vertex_scalar_integral

#### 1-dimensional

- circular_arc_length
- circular_arc_area
- density_edge_length
- dihedral_hooke
- edge_area
- edge_general_integral
- edge_length, edge_tension
- edge_scalar_integral
- edge_torus_area
- edge_vector_integral
- hooke_energy
- hooke2_energy
- hooke3_energy
- klein_length
- laplacian_mean_curvature
- local_hooke_energy
- metric_edge_length
- neo_hookean
- null_length
- spherical_arc_length
- spherical_arc_area_n
- spherical_arc_area_s
- sqcurve_string
- sqcurve2_string
- sqcurve3_string
- sqcurve_string_marked
- sq_gaussian_curv_cyl
- sq_mean_curv_cyl
- sq_torsion
- string_gravity

#### 2-dimensional

- circle_willmore
- dirichlet_area
- density_facet_area
- density_facet_area_u
- facet_2form_integral
- facet_2form_sq_integral
- facet_area, facet_tension
- facet_area_u
- facet_general_integral
- facet_general_hi_d_integral
- facet_scalar_integral
- facet_torus_volume
- facet_vector_integral
- facet_volume
- full_gravity_method
- gap_energy
- gravity_method
- klein_area
- laplacian_mean_curvature
- metric_facet_area
- null_area
- pos_area_hess
- sobolev_area
- spherical_area
- stokes2d
- stokes2d_laplacian

#### 2-D Curvatures

- mean_curvature_integral
- mean_curvature_integral_a
- sq_mean_curvature
- eff_area_sq_mean_curvature
- normal_sq_mean_curvature
- mix_sq_mean_curvature
- star_sq_mean_curvature
- star_eff_area_sq_mean_curvature
- star_normal_sq_mean_curvature
- star_perp_sq_mean_curvature
- gauss_curvature_integral
- star_gauss_curvature
- sq_gauss_curvature

#### General dimensions

- simplex_vector_integral
- simplex_k_vector_integral
- edge_k_vector_integral

#### Knot energies

- knot_energy
- uniform_knot_energy
- uniform_knot_energy_normalizer
- uniform_knot_normalizer1
- uniform_knot_normalizer2
- edge_edge_knot_energy, edge_knot_energy
- edge_knot_energy_normalizer
- simon_knot_energy_normalizer
- facet_knot_energy
- facet_knot_energy_fix
- bi_surface
- buck_knot_energy
- proj_knot_energy
- circle_knot_energy
- sphere_knot_energy
- sin_knot_energy
- curvature_binormal
- ddd_gamma_sq
- edge_min_knot_energy
- true_average_crossings
- true_writhe
- twist
- writhe
- curvature_function
- knot_thickness
- knot_thickness_0
- knot_thickness_p
- knot_thickness_p2
- knot_thickness2
- knot_local_thickness

#### Elastic stretching energies

- dirichlet_elastic
- linear_elastic
- general_linear_elastic
- linear_elastic_B
- relaxed_elastic_A
- relaxed_elastic1_A
- relaxed_elastic2_A
- relaxed_elastic
- relaxed_elastic1
- relaxed_elastic2
- SVK_elastic

#### Weird and miscellaneous

- wulff_energy
- area_square
- stress_integral
- carter_energy
- charge_gradient
- johndust
- ackerman

## Method descriptions
The descriptions below of the individual methods give a mathematical definition of the method, what type of element it applies to, definition parameters, which types of models it applies to, any restrictions on the dimension of ambient space, and whether the method has a Hessian implemented. Unless specifically noted, a method has the gradient implemented, and hence may be used for an energy or a constraint. The definition parameters are usually scalar or vector integrands (see the datafile declaration for full syntax). Some methods also depend on global variables as noted. The sample datafile declarations given are for simple cases; full syntax is given elsewhere. Remember in the samples that for quantities not declared global, the quantity has to be individually applied to the desired elements.

## 0-dimensional

### vertex_scalar_integral
Named method. Description: Function value at a vertex. This actually produces a sum over vertices, but as a mathematician, I think of a sum over vertices as a point-weighted integral.
Element: vertex.
Parameters: scalar_integrand.
Models: linear, quadratic, Lagrange, simplex.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

## 1-dimensional

### edge_tension or edge_length
Named method. Description: Length of edge. Quadratic model uses Gaussian quadrature of order integral_order_1D.
Element: edge.
Parameters: none.
Models: linear, quadratic, Lagrange.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### density_edge_length
Named method. Description: Length of edge, multiplied by the edge density. Quadratic model uses Gaussian quadrature of order integral_order_1D.
Element: edge.
Parameters: none.
Models: linear, quadratic, Lagrange.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### edge_scalar_integral
Named method. Description: Integral of a scalar function over arclength. Uses Gaussian quadrature of order integral_order_1D.
Element: edge.
Parameters: scalar_integrand.
Models: linear, quadratic, Lagrange.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### edge_vector_integral
Named method. Description: Integral of a vectorfield over an oriented edge. Uses Gaussian quadrature of order integral_order_1D.
Element: edge.
Parameters: vector_integrand.
Models: linear, quadratic, Lagrange.
Ambient dimension: any.
Hessian: yes.
Orientable: yes.
Example datafile declaration:

### edge_general_integral
Named method. Description: Integral of a scalar function of position and tangent over an edge. The components of the tangent vector are represented by continuing the coordinate indices. That is, in 3D the position coordinates are x1,x2,x3 and the tangent components are x4,x5,x6. For proper behavior, the integrand should be homogeneous of degree 1 in the tangent components. Uses Gaussian quadrature of order integral_order_1D.
Element: edge.
Parameters: scalar_integrand.
Models: linear, quadratic, Lagrange.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration: the edge length in 3D could be calculated with this quantity:

### edge_area
Named method. Description: For calculating the area of a body in the string model. Implemented as the exact integral of -y dx over the edge. Valid for torus model, but not general symmetry groups. You may have to set the quantity volconst attribute in the torus model, since the area calculation is ambiguous up to one torus area.
Element: edge.
Parameters: none.
Models: linear, quadratic, Lagrange.
Ambient dimension: 2.
Hessian: yes.
Example datafile declaration:

### edge_torus_area
Named method. Description: For 2D torus string model body area calculations. Contains adjustments for torus wraps. You may have to set the quantity volconst attribute in the torus model, since the area calculation is ambiguous up to one torus area.
Element: edge.
Parameters: none.
Models: torus; string; linear,quadratic,Lagrange.
Ambient dimension: 2.
Hessian: yes.
Example datafile declaration:

### string_gravity
Named method. Description: To calculate the gravitational potential energy of a body in the string model. Uses differences in body densities. Does not use gravitational constant G as modulus (unless invoked as internal quantity by convert_to_quantities).
Element: edge.
Parameters: none.
Models: string linear, quadratic, lagrange.
Ambient dimension: 2.
Hessian: yes.
Orientable: yes.
Example datafile declaration:

### hooke_energy
Named method. Description: One would often like to require edges to have fixed length. The total length of some set of edges may be constrained by defining a fixed quantity. This is used to fix the total length of an evolving knot, for example. But to have one constraint for each edge would be impractical, since projecting to n constraints requires inverting an n x n matrix. Instead there is a Hooke's Law energy available to encourage edges to have equal length. Its form per edge is

```text

   E =  | L - L_0| ^p


```
where L is the edge length, L_0 is the equilibrium length, embodied as an adjustable parameter `hooke_length', and the power p is an adjustable parameter `hooke_power'. The default power is p = 2, and the default equilibrium length is the average edge length in the initial datafile. You will want to adjust this, especially if you have a total length constaint. A high modulus will decrease the hooke component of the total energy, since the restoring force is linear in displacement and the energy is quadratic (when p=2). As an extra added bonus, a `hooke_power' of 0 will give

```text
   E = -\log|L-L_0|.

```
See hooke2_energy for individual edge equilibrium lengths.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### hooke2_energy
Named method. Description: Same as hooke_energy, but each edge has an equilibrium length extra attribute `hooke_size' (which the user need not declare). If the user does not set hooke_size by the time the method is first called, the value will default to the current length. Hooke_size is not automatically adjusted by refining. It is the responsibility of the user to reset hooke_size after refining; you could re-define the 'r' command

```text

   r :::= { 'r'; set vertex hooke_size hooke_size/2 }


```
to take care of it automatically. The power of displacement used is given by the internal read-write variable hooke2_power, which has default value 2.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### hooke3_energy
Named method. Description: Same as hooke2_energy, but uses an elastic model instead of a spring. The energy is

```text
energy = 0.5*(length-hooke_size)^2/hooke_size.

```
The exponent can be altered from 2 by setting the parameter hooke3_power. If the internal variable frickenhaus_flag is nonzero, then the energy is taken to be 0 if the length is less than the equilibrium length.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### local_hooke_energy
Named method. Description: Energy of edges as springs with equilibrium length being average of lengths of neighbor edges. Actually, the energy is calculated per vertex,

```text
 E = ({L_1 - L_2 \over L_1 + L_2})^2


```
where L_1 and L_2 are the lengths of the edges adjacent to the vertex. Meant for loops of string. (by John Sullivan) If you set the variable local_hooke_flag} nonzero then local_hooke_energy will not be evaluated at vertices with valence not equal to 2.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### dihedral_hooke
Named method. Description: Energy of an edge is edge length times square of angle between normals of adjacent facets. Actually, e = (1 - cos(angle))*length.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### sqcurve_string
Named method. Description: Integral of squared curvature in string model. Assumes two edges per vertex, so it just uses the first two edges it finds at a vertex; see sqcurve_string_marked for more complicated topologies. Value zero at endpoint of curve. Value is calculated as if the exterior angle at the vertex is evenly spread over the adjacent half-edges. More precisely, if s1 and s2 are the adjacent edge lengths and t is the exterior angle, value = 4*(1 - cos(t))/(s1+s2). Other powers of the curvature can be specified by using the parameter parameter_1 in the instance definition. If parameter_1 is not present, then the internal read-write variable curvature_power is used, which defaults to 2. Also see sqcurve2_string for a version with intrinsic curvature, and sqcurve3_string for a version that uses a slightly different formula to encourage equal length edges.
Element: vertex.
Parameters: parameter_1.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### sqcurve2_string
Named method. Description: Integral of squared curvature in string model, but with an intrinsic curvature. The value zero at endpoint of curve. The value is calculated as if the exterior angle at the vertex is evenly spread over the adjacent half-edges. More precisely, if s1 and s2 are the adjacent edge lengths, h0 is the intrinsic curvature, and t is the exterior angle, then value = (sin(t)/((s1+s2)/2)-h0) 2. The intrinsic curvature h0 may be specified either with a global variable h_zero or a real-valued vertex extra attribute h_zero.
Element: vertex.
Models: linear.
Ambient dimension: 2
Hessian: no.
Example datafile declaration:

### sqcurve3_string
Named method. Description: Same as sqcurve_string, but uses a slightly different formula to encourage equal length edges The value zero at endpoint of curve. The value is calculated as if the exterior angle at the vertex is evenly spread over the adjacent half-edges. More precisely, if s1 and s2 are the adjacent edge lengths, h0 is the intrinsic curvature, and t is the exterior angle, value = 2*(1 - cos(t))*(1/s1+1/s2).
Element: vertex.
Models: linear.
Ambient dimension: any
Hessian: yes.
Example datafile declaration:

### sqcurve_string_marked
Named method. Description: Integral of squared curvature in string model. Same as sqcurve_string, but only "marked" edges are used, so the topology of edges can be more complicated than a loop or curve. The marking is done by declaring an integer-valued edge attribute named sqcurve_string_mark and setting it to some nonzero value for those edges you want to be involved, usually two at each vertex to which this method is applied. Value zero at vertex with only one marked edge. Value is calculated as if the exterior angle at the vertex is evenly spread over the adjacent half-edges. More precisely, if s1 and s2 are the adjacent edge lengths and t is the exterior angle, value = 4*(1 - cos(t))/(s1+s2). Other powers of the curvature can be specified by using the parameter parameter_1 in the instance definition.
Element: vertex.
Parameters: parameter_1.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### sq_gaussian_curv_cyl
Named method. Description: Integral of the squared gaussian curvature of a surface of revolution. The generating curve is set up in the string model, and this method applied to its vertices. The axis of rotation is the x-axis.
Element: vertex.
Models: linear string.
Ambient dimension: 2
Hessian: yes.
Example datafile declaration:

### sq_mean_curv_cyl
Named method. Description: Integral of the squared mean curvature of a surface of revolution. The generating curve is set up in the string model, and this method applied to its vertices. The axis of rotation is the x-axis. This method will do intrinsic curvature by means either of a global variable h_zero or a real-valued vertex attribute h_zero.
Element: vertex.
Models: linear string.
Ambient dimension: 2
Hessian: yes.
Example datafile declaration:

### sq_torsion
Named method. Integral of squared torsion for curves. The torsion is approximated by looking at triples of adjacent edges; if A,B,C are the edge vectors, then the sin of the angle the osculating plane twists by (from AxB to BxC) is

```text

       [A,B,C] |B|
  S =  -----------
       |AxB| |BxC|


```
(This is analogous to t = [T,T',T'']/k^2 for tangent vector T and curvature k. I'm using [A,B,C] as notation for triple product.) Then the torsion is

```text

   t = arcsin(S)/|B|


```
and the integral of the square of the torsion is

```text

   t^2 |B| = arcsin(S)^2/|B|


```
This function assumes the edges in each component are consistently oriented. Since this method is meant to be used on boundary wires of surfaces, it uses a "sq_torsion_mark" attribute on edges to tell which edges are to be included. Example top of datafile declaration: Then mark the edges you want included, for example using quad.fe
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.

### metric_edge_length
Named method. Description: In the string model with a Riemannian metric, this is the length of an edge.
Element: edge.
Parameters: none.
Models: linear,quadratic,simplex.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### klein_length
Named method. Description: Edge length in Klein hyperbolic plane model. Does not depend on klein_metric being declared. Vertices should be inside unit sphere.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 2.
Hessian: no.
Example datafile declaration:

### circular_arc_length
Named method. Description: Edge length, modelling the edge as a circular arc through three points, hence useful only in the quadratic model. If not in the quadratic model, it evaluates as the edge_length method. The presence of this quantity has the side effect of automatically toggling circular_arc_draw, causing edges to display as circular arcs in the quadratic model.
Element: edge.
Parameters: none.
Models: quadratic; string.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration: More commonly used with the area_method_name declaration in the top of the datafile.

### circular_arc_area
Named method. Description: Area between an edge and the y axis, with the edge modelled as a circular arc through three points. Useful in the quadratic model; in other models it is the same as edge_area.
Element: edge.
Parameters: none.
Models: quadratic.
Ambient dimension: 2.
Orientable: yes.
Hessian: yes.
Example datafile declaration: More commonly used with the area_method_name declaration in the top of the datafile.

### spherical_arc_length
Named method. Description: Edge length, modelling the edge as a spherical great circle arc between its two endpoints, which are assumed to lie on an arbitrary radius sphere centered at the origin. This method is meant for modelling string networks on spheres, and is suitable for use with the length_method_name feature for substituting the default edge length calculation method. Note that this method is an exact spherical calculation in the linear model, so there is no need to refine edges or use higher order models for accuracy. Edges are graphed as spherical arcs (actually, lots of segments).
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: yes.
Example datafile declaration:

### spherical_arc_area_n, spherical_arc_area_s
Named method. Description: Area on a sphere between an edge (considered as a great circle arc) and the north (or south) pole. This is an exact calculation in the linear model. Meant for calculating the areas of facets in the string model with the string network confined to a sphere of arbitrary radius centered at the origin. There are two versions of this method, since calculation of facet areas by means of edges necessarily has a singularity somewhere on the sphere. Spherical_arc_area_n has its singularity at the south pole, and spherical_arc_area_s has its singularity at the north pole. Thus spherical_arc_area_s will work accurately for facets not including the north pole in there interiors; a facet including the north pole will have its area calculated as the negative complement of its true area, so a body defined using it could get the correct area by using a volconst of a whole sphere area. If the singular pole falls on an edge or vertex, then results are unpredictable. With these caveats, these methods are suitable for use with the area_method_name feature for substituting the default edge area method. If you do a facet as an explicit quantity, you are responsible for applying or unapplying the quantity after topology changes!!
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Orientable: yes.
Hessian: yes.
Example datafile declaration:

## 2-dimensional

### facet_tension, facet_area
Named method. Description: Area of facet. Does not multiply by facet density; density_facet_area does that. Quadratic model uses Gaussian cubature of order integral_order_2D. Beware that this is an approximation to the area, and if the facets in the quadratic or Lagrange model get too distorted, it can be a bad approximation. Furthermore, facets can distort themselves in seeking the lowest numerical area. By default, changing the model to quadratic or Lagrange will set an appropriate integral_order_2D.
Element: facet.
Parameters: none.
Models: linear, quadratic, Lagrange; soapfilm, simplex.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### density_facet_area
Named method. Description: Area of facet, multiplied by its density. Otherwise same as facet_area.
Element:
Parameters:
Models: linear, quadratic, Lagrange, simplex.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### facet_volume
Named method. Description: Integral of z dx dy over an oriented facet. Valid in the torus domain. Not valid for other symmetry groups. You may have to set the quantity volconst attribute in the torus model, since the volume calculation is ambiguous up to one torus volume.
Element: facet.
Parameters: none.
Models: linear, quadratic, Lagrange.
Ambient dimension: 3.
Hessian: yes.
Orientable: yes.
Example datafile declaration:

### facet_scalar_integral
Named method. Description: Integral of a scalar function over facet area. Uses Gaussian cubature of order integral_order_2D.
Element: facet.
Parameters: scalar_integrand.
Models: linear, quadratic, Lagrange.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### facet_vector_integral
Named method. Description: Integral of a vectorfield inner product with the surface normal over a facet. The normal is the right-hand rule normal of the facet as defined in the datafile. Uses Gaussian cubature of order integral_order_2D.
Element: facet.
Parameters: vector_integrand.
Models: linear, quadratic, Lagrange, simplex.
Ambient dimension: any.
Hessian: yes.
Orientable: yes. Example datafile declaration, for volume equivalent:

### facet_2form_integral
Named method. Description: Integral of a 2-form over a facet. Meant for ambient dimensions higher than 3. Uses Gaussian cubature of order integral_order_2D.
Element: facet.
Parameters: form_integrand (components in lexicographic order).
Models: linear, Lagrange, simplex.
Ambient dimension: any.
Hessian: yes.
Orientable: yes. Example datafile declaration in 4D:

### facet_2form_sq_integral
Named method. Description: Integral of the square of a 2-form over a facet. Meant for ambient dimensions higher than 3. Uses Gaussian cubature of order integral_order_2D.
Element: facet.
Parameters: form_integrand (components in lexicographic order).
Models: linear.
Ambient dimension: any.
Hessian: no.
Orientable: no. Example datafile declaration in 4D:

### facet_general_integral
Named method. Description: Integral of a scalar function of position and normal vector over a facet. Uses Gaussian cubature of order integral_order_2D. The components of the normal vector are represented by continuing the coordinate indices. That is, in 3D the position coordinates are x1,x2,x3 and the normal components are x4,x5,x6. For proper behavior, the integrand should be homogeneous of degree 1 in the normal components.
Element: facet.
Parameters: scalar_integrand.
Models: linear, quadratic, Lagrange.
Ambient dimension: 3.
Hessian: yes. Example: The facet area could be calculated with this quantity:

### facet_general_hi_d_integral
Named method. Named method. Description: Integral of a scalar function of position and normal vector over a 2D facet in any ambient dimension space. Uses Gaussian cubature of order integral_order_2D. The 2D facet is represented by a 2-vector. The components of the 2-vector are named as xn, where the number n ranges from N+1 to N+N*(N+1)/2, continuing the coordinate indices. That is, in 4D the position coordinates are x1,x2,x3,x4 and the 2-vector components are x5 = x1 ∧ x2, x6 = x1 ∧ x3, x7 = x1 ∧ x4, x8 = x2 ∧ x3, x9 = x2 ∧ x4, and x10 = x3 ∧ x4. For proper behavior, the integrand should be homogeneous of degree 1 in the 2-form components.
Element: facet.
Parameters: scalar_integrand.
Models: linear, quadratic, Lagrange.
Ambient dimension: any.
Hessian: yes. Example: The facet area could be calculated with this quantity:

### facet_torus_volume
Named method. Description: For 3D soapfilm model, calculates body volume integral for a facet, with corrections for edge wraps. You may have to set the quantity volconst attribute in the torus model, since the volume calculation is ambiguous up to one torus volume.
Element: facet.
Parameters: none.
Models: linear,quadratic,lagrange.
Ambient dimension: 3.
Hessian: yes.
Orientable: yes.
Example datafile declaration:

### gravity_method, full_gravity_method
Named method. Description: Gravitational energy, integral of p z^2/2 dxdy over a facet, where p is difference in adjacent body densities. Note: this method uses the gravitational constant as the modulus if invoked as full_gravity_method. Just gravity_method does not automatically use the gravitational constant.
Element: facet.
Parameters: none.
Models: linear, quadratic, Lagrange.
Ambient dimension: 3.
Hessian: yes.
Orientable: yes.
Example datafile declaration:

### facet_area_u, density_facet_area_u
Named method. Description: Area of facet. In quadratic model, it is an upper bound of area, by the Schwarz Inequality. For the paranoid. Same as facet_area in linear model. Sets integral_order_2D to 6, since it doesn't work well with less. Using the density_facet_area_u name automatically incorporates the facet tension, but facet_area_u doesn't.
Element: facet.
Parameters: none.
Models: linear, quadratic.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### gap_energy
Named method. Description: Implementation of gap energy, which is designed to keep edges from short-cutting curved constraint surfaces. This method serves the same purpose as declaring a constraint convex. Automatically incorporates the gap_constant set in the datafile or by the k command.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration: As an alternative to gap_energy, you should consider a system of "guide lines", i.e. a plane level set constraint whose coefficients are extra attributes of vertices. This can keep the contact line vertices evenly spaced without adding extra energy, and permitting Hessian operations.

### metric_facet_area
Named method. Description: For a Riemannian metric, this is the area of a facet.
Element: edge.
Parameters: none.
Models: linear,quadratic,simplex.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### klein_area
Named method. Description: Facet area in Klein hyperbolic 3D space model. Does not depend on klein_metric being declared in the datafile. Vertices should be inside the unit sphere.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### circle_willmore
Named method. Description: Alexander Bobenko's circle-based discrete Willmore energy, which is conformally invariant. At each vertex, energy is (sum of the angles between facet circumcircles) - 2*pi. More simply done as edge quantity, since angles at each end are the same. For edge e, if adjacent facet edge loops are a,e,d and b,c,-e, then circle angle beta for edge has

```text

   cos(beta) = (<a,c><b,c>-<a,b><c,d>-<b,c><d,a>)/|a|/|b|/|c|/|d|


```
For now, assumes all vertices are faceted, and fully starred. Severe numerical difficulties: Not smooth when angle beta is zero, which is all too common. Set of zero angles should be codimension 2, which means generally avoided, but still crops up.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### dirichlet_area
Named method. Description: Same as the facet_tension method, but the Hessian is modified to be guaranteed positive definite, after the scheme of Polthier and Pinkall [PP]. The energy is taken to be the Dirichlet integral of the perturbation from the current surface, which is exactly quadratic and positive definite. Hence the hessian command always works, but final convergence may be slow (no faster than regular iteration) since it is only an approximate Hessian. Also see the dirichlet command.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### sobolev_area
Named method. Description: Same as the facet_tension method, but the Hessian is modified to be guaranteed positive definite, after the scheme of Renka and Neuberger. [RN]. Hence the hessian command always works, but final convergence may be slow (no faster than regular iteration) since it is only an approximate Hessian. Also see the sobolev command.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### pos_area_hess
Named method. Description: Same as the facet_area method, but the Hessian can be adjusted various ways by setting the variables fgagfa_coeff, gfa_2_coeff, gfagfa_coeff, and gfaafg_coeff. This will make sense if you look at the Dirichlet section of the Technical Reference chapter of the printed manual. The default values of the coefficients are -1, 1, -1, and 0 respectively.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### spherical_area
Named method. Description: Area of the facet projected to unit sphere. The vertices of the facet are assumed to be on the unit sphere.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### stokes2d
Named method. Description: Square of the Laplacian of z viewed as a function of (x,y). Meant for the calculation of two-dimensional Stokes flow of a fluid (i.e. slow steady-state flow where inertia is not significant) by having the Evolver surface be the graph of the velocity potential and minimizing the viscous dissipation, which is the square of the Laplacian of z. Boundary conditions are handled by declaring a vertex attribute "stokes_type" of type integer, and assigning each boundary vertex one of these values:

- 0 - vertex is not on a wall; treat as if on a mirror symmetry plane.
- 1 - vertex is on a slip wall.
- 2 = vertex is on a nonslip wall; normal derivative of potential is zero.
Boundary values of z should be set to constants between 0 and 1 on various sections of boundary that represent walls.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: yes.
Example datafile declaration: Note: Evolver creates a vertex attribute stokes_velocity for internal use.

### stokes2d_laplacian
Named method. Description: The Laplacian of z viewed as a function of (x,y). This is auxiliary to the stokes2d method. It is the same Laplacian, unsquared, with the same boundary rules. Meant for calculating pressures and such after stokes2d energy has been minimized.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: yes.
Example datafile declaration:

## Surface curvature functions

### mean_curvature_integral
Named method. Description: Integral of signed scalar mean curvature of a 2D surface. The computation is exact, in the sense that for a polyhedral surface the mean curvature is concentrated on edges and singular there, but the total mean curvature for an edge is the edge length times its dihedral angle.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration: The method mean_curvature_integral_a does the same thing, but uses a numerical formulation which may be better behaved.
There is an obsolete use of mean_curvature_integral in the top of the datafile to indicate the integral of the mean curvature should be included as an energy, with syntax

```text

  mean_curvature_integral: modulus


```
where modulus is the multiplier for the energy. The modulus winds up as the internal read-write variable mean_curvature_modulus.

### sq_mean_curvature
Named method. Description: Integral of squared mean curvature of a surface. There are several methods implemented for calculating the integral of the squared mean curvature of a surface. The older methods sq_mean_curvature, eff_area_sq_mean_curvature, and normal_sq_mean_curvature, are now deprecated, since they don't have Hessians and the newer methods star_sq_mean_curvature, star_eff_area_sq_mean_curvature, star_normal_sq_mean_curvature, and my current favorite star_perp_sq_mean_curvature, do have Hessians and can now handle incomplete facet stars around vertices. But read the following for general remarks on squared curvature also.
The integral of squared mean curvature in the soapfilm model is calculated for this method as follows: Each vertex v has a star of facets around it of area A. The force F due to surface tension on the vertex is the gradient of area, Since each facet has 3 vertices, the area associated with v is A/3. Hence the average mean curvature at v is
h = (1/2)(F/(A/3)),
where the 1/2 factor comes from the "mean" part of "mean curvature". This vertex's contribution to the total integral is then
E = h 2 A/3 = (3/4)F 2 /A.
Philosophical note: The squared mean curvature on a triangulated surface is technically infinite, so some kind of approximation scheme is needed. The alternative to locating curvature at vertices is to locate it on the edges, where it really is, and average it over the neighboring facets. But this has the problem that a least area triangulated surface would have nonzero squared curvature, whereas in the vertex formulation it would have zero squared curvature.
Practical note: The above definition of squared mean curvature seems in practice to be subject to instablities. One is that sharp corners grow sharper rather than smoothing out. Another is that some facets want to get very large at the expense of their neighbors. Hence a couple of alternate definitions have been added.
Curvature at boundary: If the edge of the surface is a free boundary on a constraint, then the above calculation gives the proper curvature under the assumption the surface is continued by reflection across the constraint. This permits symmetric surfaces to be represented by one fundamental region. If the edge of the surface is a fixed edge or on a 1-dimensional boundary, then there is no way to calculate the curvature on a boundary vertex from knowledge of neighboring facets. For example, the rings of facets around the bases of a catenoid and a spherical cap may be identical. Therefore curvature is calculated only at interior vertices, and when the surface integral is done, area along the boundary is assigned to the nearest interior vertex. However, including IGNORE_FIXED or IGNORE_CONSTRAINTS in the method declaration will force the calculation of energy even at fixed points or ignoring constraints respectively.
If the parameter or vertex attribute h_zero is defined, then the value per vertex is the same as for the following method, eff_area_sq_mean_curvature.

Element: vertex.
Parameters: IGNORE_CONSTRAINTS, IGNORE_FIXED.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### eff_area_sq_mean_curvature
Named method. Description: Integral of squared mean curvature of a surface, with a slightly different definition from sq_mean_curvature or normal_sq_mean_curvature. The area around a vertex is taken to be the magnitude of the gradient of the volume. This is less than the true area, so makes a larger curvature. This also eliminates the spike instability, since a spike has more area gradient but the same volume gradient. Letting N be the volume gradient at vertex v,
h = (1/2)(F/N)),
and
E = h 2 A/3 = (3/4)(F·F/N·N)A.
The facets of the surface must be consistently oriented for this to work, since the evolver needs an `inside' and `outside' of the surface to calculate the volume gradient. There are still possible instabilities where some facets grow at the expense of others.
If the parameter or vertex attribute h_zero is defined, then the value per vertex is
E = (h-h 0) 2 A/3 = (3/4)(F·N/N·N-2h 0) 2 A.
This does not reduce to the non- h_zero formula when h_zero has the value zero, but is actually a pretty good formula in its own right (see star_perp_sq_mean_curvature.
If the vertex is on one or several constraints, the F and N are projected to the constraints, essentially making the constraints act as mirror symmetry planes. If a constraint should not be considered as a mirror plane, it should be given the attribute nonwall in its declaration in the datafile.
WARNING: For some extreme shapes, Evolver may have problems detecting consistent local surface orientation. The assume_oriented toggle lets Evolver assume that the facets have been defined with consistent local orientation.

Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### normal_sq_mean_curvature
Named method. Description: Integral of squared mean curvature of a surface, with a slightly different definition from sq_mean_curvature or eff_area_sq_mean_curvature. To alleviate the instability of eff_area_sq_mean_curvature, normal_sq_mean_curvature considers the area around the vertex to be the component of the volume gradient parallel to the mean curvature vector, rather than the magnitude of the volume gradient. Thus
h = (1/2)(F·F/N·F)
E = h 2 A/3 = (3/4)(F·F/N·F) 2 A.
This is still not perfect, but is a lot better. WARNING: For some extreme shapes, Evolver may have problems detecting consistent local surface orientation. The assume_oriented toggle lets Evolver assume that the facets have been defined with consistent local orientation.
If the parameter or vertex attribute h_zero is defined, then the value per vertex is
E = (h-h 0) 2 A/3 = (3/4)(F·F/N·F - 2h 0) 2 A
If the vertex is on one or several constraints, the F and N are projected to the constraints, essentially making the constraints act as mirror symmetry planes.

Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### mix_sq_mean_curvature
Named method. Description: Integral of squared mean curvature of a surface, with combination of approximate formulas for the mean curvature.
h = ((F·F/N·F)*sq_mean_mix + (F·N/N·N))/2
E = h 2 A/3.
where F is the force or area gradient at a vertex, N is the unit normal vector as determined by the volume gradient, and A is the area of the facets adjacent to the vertex. {\cf sq\_mean\_mix} is a user-defined variable that controls the combination; its default version is 0. WARNING: For some extreme shapes, Evolver may have problems detecting consistent local surface orientation. The assume_oriented toggle lets Evolver assume that the facets have been defined with consistent local orientation.
If the parameter or vertex attribute h_zero is defined, then the value per vertex is
E = (h-h 0) 2 A/3
If the vertex is on one or several constraints, the F and N are projected to the constraints, essentially making the constraints act as mirror symmetry planes.

Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### star_sq_mean_curvature
Named method. Description: Integral of squared mean curvature over a surface. This is a different implementation of sq_mean_curvature, and it has a Hessian. This method no longer requires a complete circle of vertices around a vertex; boundary edges are treated as if they are on mirror symmetry planes, which is usually true. The positive orientation of the surface is determined by the positive orientation of the first facet of the vertex's internal facet list. This method does not do prescribed mean curvature with the h_zero parameter.
The curvature calculation works in any dimension space. If for some reason the space has an ambient dimension greater than 3, and you want to restrict the calculation of curvature to the first three coordinates, the toggle calculate_in_3d will do that.

Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### star_eff_area_sq_mean_curvature
Named method. Description: Integral of squared mean curvature over a surface. This is a different implementation of eff_area_sq_mean_curvature, and it has a Hessian. This method no longer requires a complete circle of vertices around a vertex; boundary edges are treated as if they are on mirror symmetry planes, which is usually true. The positive orientation of the surface is determined by the positive orientation of the first facet of the vertex's internal facet list. This method does not use the h_zero parameter.
The curvature calculation works in any dimension space. If for some reason the space has an ambient dimension greater than 3, and you want to restrict the calculation of curvature to the first three coordinates, the toggle calculate_in_3d will do that.

Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### star_normal_sq_mean_curvature
Named method. Description: Integral of squared mean curvature over a surface. This is a different implementation of normal_sq_mean_curvature which is more suitable for parallel calculation and has a Hessian. This method no longer requires a complete circle of vertices around a vertex; boundary edges are treated as if they are on mirror symmetry planes, which is usually true. The positive orientation of the surface is determined by the positive orientation of the first facet of the vertex's internal facet list. This method can use the h_zero parameter or vertex attribute for prescribed mean curvature.
The curvature calculation works in any dimension space. If for some reason the space has an ambient dimension greater than 3, and you want to restrict the calculation of curvature to the first three coordinates, the toggle calculate_in_3d will do that.

Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration: WARNING: The division by F.N can cause problems sometimes. Usually F and N are close to parallel, but I have seen cases where they get close to parallel and things go awry. I recommend using star_perp_sq_mean_curvature instead.

### star_perp_sq_mean_curvature
Named method. Description: Integral of squared mean curvature over a surface. This is my current favorite implementation of squared mean curvature. It is an implementation specifically designed to agree with the mean curvature computed as the gradient of area when normal motion is on (either the normal_motion toggle for 'g' iteration, or Hessian with hessian_normal). Thus if you get zero squared mean curvature with this method, then switch to area energy, the hessian will report exact convergence. Likewise if you do prescribed curvature and then convert to area minimization with a volume constraint. This method has a Hessian. This method does not require a complete circle of vertices around a vertex; boundary edges are treated as if they are on mirror symmetry planes, which is usually true. This method can use the h_zero parameter or vertex attribute for prescribed mean curvature. The actual formula for the energy at a vertex is
h = (1/2)(F·N/N·N)
E = (h-h 0) 2 A/3 = (3/4)(F·N/N·N - 2h 0) 2 A
where F is the area gradient at the vertex, N is the volume gradient, and A is the area of the adjacent facets. If the vertex is on one or several constraints, the F and N are projected to the constraints, essentially making the constraints act as mirror symmetry planes. The positive orientation of the surface is determined by the positive orientation of the first facet of the vertex's internal facet list.
The curvature calculation works in any dimension space. If for some reason the space has an ambient dimension greater than 3, and you want to restrict the calculation of curvature to the first three coordinates, the toggle calculate_in_3d will do that.

Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### gauss_curvature_integral
Named method. Description: This computes the total Gaussian curvature of a surface with boundary. The Gaussian curvature of a polyhedral surface may be defined at an interior vertex as the angle deficit of the adjacent angles. But as is well-known, total Gaussian curvature can be computed simply in terms of the boundary vertices, which is what is done here. The total Gaussian curvature is implemented as the total geodesic curvature around the boundary of the surface. The contribution of a boundary vertex is

```text
E =  (\sum_i \theta_i) - pi.

```
For reasons due to the Evolver's internal architecture, the sum is actually broken up as a sum over facets, adding the vertex angle for each facet vertex on the boundary and subtracting pi for each boundary edge. The total over all boundary vertices is exactly equal to the total angle deficit of all interior vertices plus 2*pi*chi, where chi is the Euler characteristic of the surface. Boundary vertices are deemed to be those that are fixed or on a parametric boundary. Alternately, one may define a vertex extra attribute gauss_bdry_v and an edge extra attribute gauss_bdry_e and set them nonzero on the relevant vertices and edges; this overrides the fixed/boundary criterion.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### star_gauss_curvature
Named method. Computes the angle deficit around vertices to which this method is applied. The angle deficit is 2*pi minus the sum of all the adjacent angles of facets. No compensation is made for vertices on the boundary of a surface; you just get big deficits there. Deficits are counted as positive, following the convention for gaussian curvature.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### sq_gauss_curvature
Named method. Description: Computes the integral of the squared Gaussian curvature. At each vertex, the Gaussian curvature is calculated as the angle defect divided by one third of the total area of the adjacent facets. This is then squared and weighted with one third of the area of the adjacent facets. This method works only on closed surfaces with no singularities due to the way it calculates the angle defect.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

## Simplex model methods

### simplex_vector_integral
Named method. Description: Integral of a vectorfield over a (n-1)-dimensional simplicial facet in n-space. Vectorfield is dotted with normal of facet; actually the side vectors of the simplex and the integrand vector are formed into a determinant.
Element: facet.
Parameters: vector_integrand.
Models: simplex.
Ambient dimension: any.
Hessian: no.
Orientable: yes. Example datafile declaration, for 4-volume under a 3D surface in 4D:

### simplex_k_vector_integral
Named method. Description: Integral of a simple (n-k)-vector over an oriented k-dimensional simplicial facet in n-space. The vector integrand lists the components of each of the k vectors sequentially. Evaluation is done by forming a determinant whose first k rows are k vectors spanning the facet, and last (n-k) rows are vectors of the integrand.
Element: facet.
Parameters: k_vector_order, vector_integrand.
Models: simplex.
Ambient dimension: any.
Hessian: yes.
Orientable: yes. Example datafile declaration, for 3D surface in 5D:

### edge_k_vector_integral
Named method. Description: Integral of a simple (n-k)-vector over an oriented k-dimensional simplicial edge in n-space. The vector integrand lists the components of each of the k vectors sequentially. Evaluation is done by forming a determinant whose first k rows are k vectors spanning the edge, and last (n-k) rows are vectors of the integrand.
Element: edge.
Parameters: k_vector_order, vector_integrand.
Models: linear, quadratic, simplex.
Ambient dimension: any.
Hessian: yes.
Orientable: yes. Example datafile declaration, for 3D edges of a 4D surface in 5D: >

### knot_energy
Named method. Description: An ``electrostatic'' energy in which vertices are endowed with equal charges. Inverse power law of potential is adjustable via the global parameter `knot_power', default value 2 (which is not electrostatic, but the knot theorists like it). If the extra attribute `node_charge' is defined for vertices, then that value is used for the vertex charge. Use of this energy is not restricted to knots; it has been used to embed complicated network graphs in space.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### uniform_knot_energy or edge_knot_energy
Named method. Description: A knot energy where vertex charge is proportional to neighboring edge length. This simulates an electrostatic charge uniformly distributed along a wire. Inverse power law of potential is adjustable via the global parameter `knot_power' (default 2).
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### uniform_knot_energy_normalizer
Named method. Description: Supposed to approximate the part of uniform_knot_energy that is singular in the continuous limit.
Element: vertex.
Parameters:
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### uniform_knot_normalizer1
Named method. Description: Calculates internal knot energy to normalize singular divergence of integral of uniform_knot_energy. Actually a synonym for uniform_knot_energy_normalizer. No gradient.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### uniform_knot_normalizer2
Named method. Description: Calculates internal knot energy to normalize singular divergence of integral of uniform_knot_energy a different way from uniform_knot_energy_normalizer.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration: >

### edge_edge_knot_energy
Named method. Description: Between pairs of edges, energy is inverse square power of distance between midpoints of edges. Can also be called just edge_knot_energy. See also edge_knot_energy_normalizer. (by John Sullivan)
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### edge_knot_energy_normalizer
Named method. Description: Calculates internal knot energy to normalize singular divergence of integral of edge_edge_knot_energy.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### simon_knot_energy_normalizer
Named method. Description: Another normalization of edge_knot_energy, which I don't feel like deciphering right now.
Element: edge.
Parameters: none.
Models: string linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### facet_knot_energy
Named method. Description: Charge on vertex is proportional to area of neighboring facets. Meant for knotted surfaces in 4D. Power law of potential is adjustable via the global parameter `knot_power'. See also facet_knot_energy_fix.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### facet_knot_energy_fix
Named method. Description: Provides adjacent vertex correction to facet_knot_energy.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### bi_surface
Named method. Named method of the knot energy family. Double integral over surface, i.e. all pairs of vertices weighted with adjacent facet areas. Adapted from facet_knot_energy. Uses an arbitrary formula for energy, a function of the vector between vertices, instead of just power rule. The formula is given by the scalar_integrand in datafile definition. The vertex pairs it is evaluated over can be controlled. If the vertex integer attribute bi_surface_attr is defined, only those with different values of bi_surface_attr will be included; otherwise all pairs are included.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### buck_knot_energy
Named method. Description: Energy between pair of edges given by formula suggested by Greg Buck. Power law of potential is adjustable via the global parameter `knot_power'.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### proj_knot_energy
Named method. Description: This energy is due to Gregory Buck. It tries to eliminate the need for a normalization term by projecting the energy to the normal to the curve. Its form is

```text

   E_{e_1e_2} = {L_1L_2 \cos^p\theta\over |x_1 - x_2|^p}


```
where x_1,x_2 are the midpoints of the edges and \theta is the angle between the normal plane of edge e_1 and the vector x_1 - x_2. The default power is 2. Power law of potential is adjustable via the global parameter `knot_power'.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### circle_knot_energy
Named method. Description: This energy is due to Peter Doyle, who says it is equivalent in the continuous case to the insulating wire with power 2. Its form is

```text

  E_{e_1e_2} = {L_1L_2 (1 - \cos\alpha)^2 \over |x_1 - x_2|^2},


```
where x_1,x_2 are the midpoints of the edges and \alpha is the angle between edge 1 and the circle through x_1 tangent to edge 2 at x_2. Only power 2 is implemented.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### sphere_knot_energy
Named method. Description: This is the 2D surface version of the circle energy. Its most general form is

```text

  E_{f_1f_2} = { A_1A_2(1 - \cos\alpha)^p \over |x_1 - x_2|^q},


```
where A_1,A_2 are the facet areas, x_1,x_2 are the barycenters of the facets, and \alpha is the angle between f_1 and the sphere through x_1 tangent to f2 at x_2. The energy is conformally invariant for p = 1 and q = 4. For p=0 and q=1, one gets electrostatic energy for a uniform charge density. Note that facet self-energies are not included. For electrostatic energy, this is approximately 2.8A^{3/2} per facet. The powers p and q are Evolver variables surface_knot_power and surface_cos_power respectively. The defaults are p=1 and q=4.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### sin_knot_energy
Named method. Description: Another weird way to calculate a nonsingular energy between midpoints of pairs of edges. (by John Sullivan)
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### curvature_binormal
Named method. Description: For string model. The energy evaluates to zero, but the force calculated is the mean curvature vector rotated to the binormal direction.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### ddd_gamma_sq
Named method. Description: Third derivative of curve position as function of arclength, squared.
Element: vertex.
Parameters: none.
Models: string, linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### edge_min_knot_energy
Named method. Description: Between pairs of edges, energy is inverse square power of distance between closest points of edges.

```text
    Energy = 1/d^2 * |e1||e2|


```
This should be roughly the same as edge_edge_knot_energy, but distances are calculated from edge midpoints there. This is not a smooth function, so we don't try to compute a gradient. DO NOT use as an energy; use just for info_only quantities.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### true_average_crossings
Named method. Description: Calculates the average crossing number of an edge with respect to all other edges, averaged over all projections. Knot stuff. No gradient, so use just in info_only quantities.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### true_writhe
Named method. Description: For calculating the writhe of a link or knot. No gradient, so use just in info_only quantities.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### twist
Named method. Description: Another average crossing number calculation. No gradient, so use just in info_only quantities.
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### writhe
Named method. Description: An average crossing number calculation. This one does have a gradient. Suggested by Hermann Gluck. Programmed by John Sullivan. Between pairs of edges, energy is inverse cube power of distance between midpoints of edges, times triple product of edge vectors and distance vector.

```text
     E = 1/d^3 * (e1,e2,d)


```

Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### curvature_function
Named method. Description: Calculates forces as function of mean and Gaussian curvatures at vertices. Function may be changed by user by altering teix.c. No energy, just forces.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### average_crossings
Named method. Description: To calculate the average crossing number in all projections of a knot. (by John Sullivan)
Element: edge.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### knot_thickness
Named method. Description: Calculates global radius of curvature at one vertex v, as the minimum radius of circle containing the vertex and the endpoints of any non-adjacent edge. Because of "min", this has no gradient, so should be used in info_only quantities.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: 3. Gradient: no.
Hessian: no.
Example datafile declaration:

### knot_thickness_0
Named method. Description: Calculates global radius of curvature at one vertex, as Lp integral of radius of curvature of circle containing the vertex and the endpoints of edges not adjacent to the vertex. Integrand raised to -p power. The power p is taken from the global variable knot_power. No factor of length in integral. This method has a gradient.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### knot_thickness_p
Named method. Description: purpose: calculates global radius of curvature at one vertex v, as Lp integral of radius of curvature of v and endpoints of nonadjacent edges. Includes factors of length at v and w. This method has a gradient. The power p is taken from the global variable knot_power.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### knot_thickness_p2
Named method. Description: Calculates the global radius of curvature at one vertex v, as Lp integral of r(v,w1,w2) over all vertices w. Here w1 and w2 are the two neighbors of vertex w. Includes factors of length at v and w. This has not been extended to allow open arcs (valence 1 vertices). This method does have a gradient. The power p is taken from the global variable knot_power.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### knot_thickness2
Named method. Description: calculates global radius of curvature at one vertex v, as the minimum radius of circle containing the vertex and the neighbor vertices of any non-adjacent vertex. Because of "min", this has no gradient, so should be used in info_only quantities.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: 3. Gradient: no.
Hessian: no.
Example datafile declaration:

### knot_local_thickness
Named method. Description: Calculates the radius of curvature at a vertex of the circle containing the vertex and its two neighbor vertices. Meant to investigate the radius at individual vertices.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: 3. Gradient: no.
Hessian: no.
Example datafile declaration:

## Weird and miscellaneous

### wulff_energy
Named method. Description: Method version of wulff energy. If Wulff filename is not given in top section of datafile, then the user will be prompted for it.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### linear_elastic
Named method. Description: To calculate the isotropic linear elastic strain energy for facets based on the Cauchy-Green strain matrix. Let S be Gram matrix of unstrained facet (dots of sides). Let Q be the inverse of S. Let F be Gram matrix of strained facet. Let C = (FQ-I)/2, the Cauchy-Green strain tensor. Let v be Poisson ratio. Then energy density is
(1/2/(1+v))(Tr(C^2) + v*(Tr C)^2/(1-(dim-1)*v))
Each facet has extra attribute poisson_ratio and extra attribute array form_factors[3] = {s11,s12,s22}, which are the entries in S. That is, s11 = dot(v2-v1,v2-v1), s12 = dot(v2-v1,v3-v1), and s22 = dot(v3-v1,v3-v1). If form_factor is not defined by the user, it will be created by Evolver, and the initial facet shape will be assumed to be unstrained. For a version of this method that gives compression zero energy, see relaxed_elastic_A.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: yes.
Example datafile declaration:

### general_linear_elastic
Named method. Description: To calculate the nonisotropic linear elastic strain energy for facets. Let A be the linear transformation from the unstrained shape to the strained shape. Then the Cauchy-Green strain tensor is C = (A T A - I)/2. Let S 1 and S 2 be the sides of the unstrained facet. Let W 1 and W 2 be the transformed facet sides. Let F be the Gram matrix of strained facet. Define
S = [ S 1 S 2], Q = S -1
W = [ W 1 W 2] = AS
F = W T W = S T A T AS
Then
A T A = Q T FQ
C = (Q T FQ - I)/2
The energy density is
(1/2)C ij K ijkl C kl
where K ijkl is the full tensor of elastic constants. By using symmetries, this can be reduced to

(1/2) [ C 11 C 22 C 12] [ E 1 E 3 E 4] [ C 11]

[ E 3 E 2 E 5] [ C 22]

[ E 4 E 5 E 6] [ C 12]

Each facet has extra attribute elastic_coeff of size 6 containing { E 1, E 2, E 3, E 4, E 5, E 6}, and extra attribute array elastic_basis of size 2x2 containing { {s11,s12},{s21,s22}}, which are the two sides of the unstrained facet. Note that the E i are defined with respect to the original sides as defined by the form factors, so it is up to you to make sure everything works out right. Test carefully!!! The elastic_coeff attribute must be created and initialized by the user.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: yes.
Example datafile declaration:

### linear_elastic_B
Named method. Description: A variation of the linear_elastic method. To calculate the linear elastic strain energy for facets based on the Cauchy-Green strain matrix. Let S be Gram matrix of unstrained facet (dots of sides). Let Q be the inverse of S. Let F be Gram matrix of strained facet. Let C = (FQ-I)/2, the Cauchy-Green strain tensor. Let v be Poisson ratio. Then energy density is

```text
 (1/2/(1+v))(Tr(C^2) + v*(Tr C)^2/(1-(dim-1)*v))


```
Each facet has extra attribute poisson_ratio and each vertex has two extra coordinates, the coordinates of the unstrained surface in a plane. Hence the surface must be set up as five dimensional. There can also be a real-valued facet extra attribute LEBweight, which can be used to give a per-facet weighting of the energy. For a version of this method that gives compression zero energy, see relaxed_elastic.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: 5.
Hessian: yes.
Example datafile declaration: relaxed_elastic_A,

### relaxed_elastic1_A, relaxed_elastic2_A
Named method. Description: Calculates the linear elastic strain energy for facets based on the Cauchy-Green strain matrix, with compression counting for zero energy, simulating, say, plastic film. The effect is to permit wrinkling. Let S be the Gram matrix of unstrained facet (dots of sides). Let Q be the inverse of S. Let F be Gram matrix of strained facet. Let C = (FQ-I)/2, the Cauchy-Green strain tensor. Let v be Poisson ratio. Then the energy is

```text
    (1/2/(1+v))(Tr(C^2) + v*(Tr C)^2/(1-(dim-1)*v))


```
Each facet has extra attribute poisson_ratio and extra attribute array form_factors[3] = {s11,s12,s22}, which are the entries in S. That is, s11 = dot(v2-v1,v2-v1), s12 = dot(v2-v1,v3-v1), and s22 = dot(v3-v1,v3-v1). If form_factor is not defined by the user, it will be created by Evolver, and the initial facet shape will be assumed to be unstrained. The compression is detected by doing an eigenvalue analysis of the strain tensor, and discarding any negative eigenvalues. Facets which are stressed in one or two dimensions can be separately counted by the relaxed_elastic1_A (one stress direction, and one wrinkle direction) and relaxed_elastic2_A (two stressed directions) methods, which are meant to be used in info_only mode. There can also be a real-valued facet extra attribute LEBweight, which can be used to give a per-facet weighting of the energy. For a sample datafile, see mylarcube.fe. For a version of this method that gives compression positive energy, see linear_elastic.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: yes.
Example datafile declaration:

### relaxed_elastic, relaxed_elastic1, relaxed_elastic2
Named method. Description: A variation of the linear_elastic method. Calculates the linear elastic strain energy for facets based on the Cauchy-Green strain matrix, with compression counting for zero energy, simulating, say, plastic film. The effect is to permit wrinkling. Let S be Gram matrix of unstrained facet (dots of sides). Let Q be the inverse of S. Let F be Gram matrix of strained facet. Let C = (FQ-I)/2, the Cauchy-Green strain tensor. Let v be Poisson ratio. Then energy density is

```text
   (1/2/(1+v))(Tr(C^2) + v*(Tr C)^2/(1-(dim-1)*v))


```
Each facet has extra attribute poisson_ratio and each vertex has two extra coordinates, the coordinates of the unstrained surface in a plane. Hence the surface must be set up as five dimensional. The compression is detected by doing an eigenvalue analysis of the strain tensor, and discarding any negative eigenvalues. The eigenvalues may be separately accessed by the relaxed_elastic1_A (lower eigenvalue) and relaxed_elastic2_A (higher eigenvalue) methods, which are meant to be used in info_only mode. There can also be a real-valued facet extra attribute LEBweight, which can be used to give a per-facet weighting of the energy. For a sample datafile, see mylarcube.fe. For a version of this method that gives compression zero energy, see linear_elastic_B.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: 5.
Hessian: yes.
Example datafile declaration:

### dirichlet_elastic
Named method. Description: Calculate the Dirichlet elastic strain energy for facets, minimization of which gives conformal mapping. Let S be Gram matrix of unstrained facet (dots of sides). Let Q be the inverse of S. Let F be Gram matrix of strained facet. Let C = FQ, the linear deformation matrix. Then energy density is
Tr(CC T)
Each facet has an extra attribute array form_factors[3] = {s11,s12,s22}, which are the entries in S. That is, s11 = dot(v2-v1,v2-v1), s12 = dot(v2-v1,v3-v1), and s22 = dot(v3-v1,v3-v1). If form_factor is not defined by the user, it will be created by Evolver, and the initial facet shape will be assumed to be unstrained.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: yes.
Example datafile declaration:

### SVK_elastic
Named method. Description: SVK (Saint-Venant - Kirchhoff) potential. The facet energy is
lambda/2*(tr(E))^2+mu*(E:E) - (3 lambda + 2 mu) * alpha*theta*tr(E)
where E=(C-I)/2 is the Green-Lagrange Strain tensor, theta = T-T0 is the temperature deviation, and alpha is the thermal dilation coefficient. Needs real-valued facet attributes SVK_alpha, SVK_mu, SVK_lambda, and SVK_theta. Also needs the facet attribute form_factors, decribed in linear_elastic. Written by Dr. Rabah Bouzidi.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: yes.
Example datafile declaration:

### neo_hookean
Named method. Contributed by Prof. Rabah Bouzidi. I don't seem to have the compact formula for this one. Needs neo_lambda, neo_mu, and form_factors.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### null_length
Named method. Description: Simply returns 0 for any edge. Useful in the string model with length_method_name when you don't want edge energy, but you still want to assign edges tension.
Element: edge.
Parameters: none.
Models: any.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### null_area
Named method. Named method. Description: Simply returns 0 for any facet. Useful with area_method_name when you don't want area as energy, but you still want to assign facets tension.
Element: edge.
Parameters: none.
Models: any.
Ambient dimension: any.
Hessian: yes.
Example datafile declaration:

### area_square
Named method. Description: Energy of a facet is the square of the facet area.
Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### carter_energy
Named method. Description: Craig Carter's energy.

```text

Given bodies $B_1$ and $B_2$ in $R^3$, define the energy
    E = \int_{B_1}\int_{B_2} {1 \over |z_1 - z_2|^{p} } d^3 z_2 d^3 z_1
This reduces to
E = {1\over (3-p)(2-p)}\sum_{F_2\in\partial B_2}\sum_{F_1\in\partial B_1}
    N_1 \cdot N_2 \int_{F_2}\int_{F_1}{1\over |z_1 - z_2|^{p-2}}
    d^2 z_1 d^2 z_2.
And if we crudely approximate with centroids $\bar z_1$ and $\bar z_2$,
E = {1\over (3-p)(2-p)}\sum_{F_2\in\partial B_2}\sum_{F_1\in\partial B_1}
        {A_1 \cdot A_2 \over |\bar z_1 - \bar z_2|^{p-2}},
where $A_1$ and $A_2$ are unnormalized area vectors for the facets.
The power p is set by the variable carter_power (default 6).


```

Element: facet.
Parameters: none.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### charge_gradient
Named method. Description: This energy is the gradient^2 of the knot_energy method, assuming the points are constrained to the unit sphere.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### johndust
Named method. Description: For all point pairs (meant to be on a sphere),

```text
       E = (pi - asin(d/2))/d,


```
where d is chord distance. For point packing problems on the sphere.
Element: vertex.
Parameters: none.
Models: linear.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### stress_integral
Named method. Description: Hmm. Looks like this one calculates integrals of components of a stress tensor. The scalar_integrand value is set as an integer standing for which component to do (a kludge). See the function stress_integral in method3.c for details. Does not have a gradient, so should be used for just info_only quantities.
Element: facet.
Parameters: scalar_integrand.
Models: linear.
Ambient dimension: 3.
Hessian: no.
Example datafile declaration:

### ackerman
Named method. Description: Not actually an energy, but a kludge to put inertia on vertices. Uses extra velocity coordinates to represent vertex in phase space. Invocation actually transfers computed forces from space coordinates to velocity coordinates, so forces become acceleration instead of velocity.
Element: vertex.
Parameters: none.
Models: any.
Ambient dimension: any.
Hessian: no.
Example datafile declaration:

### laplacian_mean_curvature
Named method. Description: Calculates the velocity of a vertex as the Laplacian of the mean curvature of the surface, meant to model the surface diffusion of atoms in sintering. The mean curvature at each vertex is calculated as a scalar, in the same way as for area_normalized area gradient, i.e. area gradient dotted with volume gradient, divided by the area of the surrounding facets. Then finite differences are used to calculate the Laplacian of the mean curvature. This calculates velocity only; the energy is always 0. This method should only be used with fixed scale in the 'g' command.
The relative speed of vertices can be controlled by the vertex attribute lmc_mobility, which the user should declare if wanted. If the user wants to access the values of mean curvature the method finds, the user should define the vertex scalar attribute lmc_mean_curvature. This method conserves volume ideally, but you might want to put on volume constraints anyway due to numerical inaccuracies.
Warning: This method should only be used with a fixed 'g' scale factor. And for stability, the factor should be proportional to the fourth power of the shortest edge, since Laplacian of mean curvature is a fourth-derivative operator, something like 0.001*length^4. This can make for very slow evolution for highly refined surfaces.

Element: vertex.
Parameters: none.
Models: linear string and linear soapfilm.
Ambient dimension: any.
Hessian: no.
Example datafile declaration: Back to top of Surface Evolver documentation. Index.
