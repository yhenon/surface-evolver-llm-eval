Surface Evolver Documentation: toggle commands

# Surface Evolver Documentation
Back to top of Surface Evolver documentation. Index. on

## Toggle commands
There are a large number of Surface Evolver features that can be turned on or off with simple "toggle" commands. The general syntax is "togglename ON" or "togglename OFF", with just "togglename" being a synonym for "togglename ON". The toggle names below have brief descriptions of their actions in the ON state. Toggles will usually print their previous state. A togglename used in an arithmetic expression is the current value of the toggle, 0 for OFF and 1 for ON. The current value of a toggle may be found by "print togglename".
Almost all toggles are reset when a surface is loaded. Default values are OFF unless otherwise noted. A few toggles are initialized to an "unset" state, which prints as -1. These will generally prompt for a value when needed.
These full-word toggle commands are not to be confused with various single-letter toggle commands, which always change the state. All single-letter toggles have full word toggle equivalents.
Toggles

- ambient_pressure
- approximate_curvature
- area_normalization
- assume_oriented
- augmented_hessian
- autochop
- autodisplay
- autopop
- autopop_quartic
- autorecalc
- backcull
- bezier_basis
- big_endian
- blas_flag
- boundary_curvature
- break_after_warning
- break_on_warning
- bunch-kauffman
- calculate_in_3d-kauffman
- check_increase
- circular_arc_draw
- clip_view
- clipped
- colormap
- conf_edge
- conj_grad
- connected
- debug
- detorus_sticky
- deturck
- diffusion
- dirichlet_mode
- effective_area

- estimate
- facet_colors
- force_deletion
- force_edgeswap
- full_bounding_box
- nction_quantity_sparse
- gravity
- gv_binary
- hessian_diff
- hessian_normal
- hessian_normal_one
- hessian_normal_perp
- hessian_quiet
- hessian_special_normal
- homothety
- immediate_autopop
- interp_normals
- interp_bdry_param
- itdebug
- jiggle
- k_altitude_mode
- kusner
- linear_metric
- little_endian
- memdebug
- metis_factor
- metric_convert
- no_dump
- normal_motion
- old_area
- quantities_only
- quiet
- quietgo
- quietload
- pinning

- pop_disjoin
- pop_enjoin
- post_project
- ps_cmykflag
- ps_colorflag
- ps_crossingflag
- ps_gridflag
- ps_labelflag
- raw_cells
- rgb_colors
- ribiere
- rotate_lights
- runge_kutta
- self_similar
- shading
- show_all_edges
- show_all_quantities
- show_inner
- show_outer
- slice_view
- smooth_graph
- sobolev_mode
- sparse_constraints
- squared_gradient
- star_finagling
- thicken
- torus_filled
- transforms
- view_4D
- view_transforms_use_unique_point
- verbose
- visibility_test
- volgrads_every
- ysmp

## AMBIENT_PRESSURE
Toggles ideal gas mode with ambient pressure outside bodies. The external pressure can be set with the pressure phrase in the top of the datafile, or at runtime with the p command, e.g. p 10.

## APPROXIMATE_CURVATURE
Evolver toggle command. Uses polyhedral curvature (linear interpolation over facets for metric) for mean curvature vector. Actually establishes the inner product for forms or vectors to be integration over facets of euclidean inner products of linear interpolation of values at vertices. Synonyms: APPROX_CURV, APPROX_CURVATURE.

## AREA_NORMALIZATION
Evolver toggle command. Convert the force on vertex to a mean curvature velocity vector by dividing the force by the area associated to the vertex, which is one-third of the area of its adjacent vertices. The string model divides by one-half of the sum of the lengths of adjacent edges. Useful in doing grain growth simulations.

## ASSUME_ORIENTED
Evolver toggle command. Tells squared mean curvature routines that they can assume the surface is locally consistently oriented. Significant only for extreme shapes.

## AUGMENTED_HESSIAN
Evolver toggle command. Solves constrained Hessians by putting the body and quantity constraint gradients in an augmented matrix with the Hessian, and using sparse matrix techniques to factor. Vastly speeds things up when there are thousands of sparse constraints, as in a foam. The default state is unset (prints as a value of -1), in which case augmentation is used for 50 or more constraints, but not for less.

## AUTOCHOP
Evolver toggle command. Evolver toggle command. Do automatic refining of long edges each iteration. Use "autochop_length := expr " to set autochop length. Each iteration, any edge that projected to become longer than the cutoff is bisected. If any bisections are done, the motion calculation is redone. The autochop length may be accessed by the read/write internal variable autochop_length; but note that simply assigning a value to autochop_length does not toggle autochop on.

## AUTODISPLAY
Evolver toggle command. Toggles automatic redrawing of graphics whenever the surface changes. Default ON. Same function as the ' D ' command.

## AUTOPOP
Evolver toggle command. Toggles automatic deletion of short edges and popping of improper vertices each iteration. Before each iteration, any edge projected to shorten to under the critical length is deleted by identifying its endpoints. The critical length is calculated as L = sqrt(2*dt), where dt is the time step or scale factor. Hence this should be used only with a fixed scale, not optimizing scale factor. The critical length is chosen so that instabilities do not arise in motion by mean curvature. If any edges are deleted, then vertices are examined for improper vertices as in the ' o ' command. Useful in string model.
Autopop is also implemented for small facets as of Evolver version 2.30. The critical area is calculated as sqrt(2*dt)*perimeter/2, where perimeter is the sum of the lengths of the three sides of the facet.
See also the immediate_autopop and autopop_quartic toggles.

## AUTOPOP_QUARTIC
Toggle. Modifies the autopop mode. The critical length for edges is set to 2*sqrt(sqrt(dt)) and the critical area for facets is 2*sqrt(sqrt(dt))*perimeter/2; meant for quantities such as laplacian_mean_curvature where velocity is proportional to fourth derivative of surface.

## AUTORECALC
Evolver toggle command. Toggles automatic recalculation of the surface whenever adjustable parameters or energy quantity moduli are changed. Default is OFF.

## BACKCULL
Evolver toggle command. Prevents display of facets with normal away from viewer. May have different effects in different graphics displays. For example, to see the inside back of a body only, "set frontcolor clear" alone works in 2D displays, but needs backcull also for direct 3D.

## BEZIER_BASIS
Evolver toggle command. When Evolver is using the Lagrange model for geometric elements, this toggle replaces the Lagrange interpolation polynomials (which pass through the control points) with Bezier basis polynomials (which do not pass through interior control points, but have positive values, which guarantees the edge or facet is within the convex hull of the control points). This is experimental at the moment, and not all features such as graphing or refinement have been suitably adjusted.

## BIG_ENDIAN
Evolver toggle command. Controls the order of bytes in binary_printf numerical output. Big-endian is most significant byte first. To change to little-endian, use little_endian, not "little_endian off".

## BLAS_FLAG
Evolver toggle command. Toggles using BLAS versions of some matrix routines, if the Evolver program has been compiled with the -DBLAS option and linked with some BLAS library. For developer use only at the moment.

## BOUNDARY_CURVATURE
Evolver toggle command. When doing integrals of mean curvature or squared curvature, the curvature of a boundary vertex cannot be defined by its neighbor vertices, so the area of the boundary vertex star instead is counted with an adjacent interior vertex.

## BREAK_AFTER_WARNING
Causes Evolver to cease execution of commands and return to command prompt after any warning message. The break does not happen until the executing command or subcommand completes; use break_on_warning for an instantanous break. Same effect as option -y.

## BREAK_ON_WARNING
Runtime toggle command. Causes Evolver to cease execution of commands and return to command prompt immediately after any warning message. Does not delay until completion of current command as break_after_warning does.

## BUNCH_KAUFMAN
Evolver toggle command. Toggles Bunch-Kaufman factoring of the Hessian in the alternative minimal degree factoring method ( ysmp off). This factors the Hessian as LBL^T where L is lower triangular with ones on the diagonal, and B is block diagonal, with 1x1 or 2x2 blocks. Supposed to be more stable when factoring indefinite Hessians.

## CALCULATE_IN_3D
Evolver toggle command. The squared mean curvature named methods star_sq_mean_curvature, star_eff_area_sq_mean_curvature, star_normal_mean_curvature, and star_perp_sq_mean_curvature work in any dimension space, but if for some reason the space has an ambient dimension greater than 3, and you want to restrict the calculation of curvature to the first three coordinates, the toggle "calculate_in_3d" will do that.

## CHECK_INCREASE
Evolver toggle command. Toggles checking for increase of energy in an iteration step. If energy increases, then the step is undone and any iteration loop is halted. Meant for early detection of instabilities and other problems causing the surface to misbehave. Useful in doing a multiple iteration with a fixed scale. Also applies to the hessian command. Caution: there are circumstances where an energy increase is appropriate, for example when there are volume or quantity constraints and conforming to the constraints means an energy increase initially.

## CIRCULAR_ARC_DRAW
Evolver toggle command. If on, then in quadratic string mode, an edge is drawn as a circular arc (actually 16 subsegments) through the endpoints and midpoint, instead of a quadratic spline.

## CLIP_VIEW
Evolver toggle command. Toggles use of clipping planes in graphics display.

## CLIPPED
Evolver toggle command. Sets torus model display to clip to the fundamental region. Not an on-off toggle. 3-way toggle with raw_cells and connected. Synonym: clipped_cells. The origin (lower left back corner) of the clip parallelogram can be set by setting entries in the display_origin vector. Default is unset, so it prompts the user when graphics are first displayed. The setting persists when loading a new surface. But loading a torus model when a non-torus model is currently displayed will not prompt.

## COLORMAP
Evolver toggle command. Use colormap from file in certain graphics output. See the P command. Use COLORFILE := "filename" to set file.

## CONF_EDGE
Evolver toggle command. Calculation of squared curvature by fitting sphere to edge and adjacent vertices (conformal curvature).

## CONJ_GRAD
Evolver toggle command. Use conjugate gradient method in g command. See also U command and RIBIERE.

## CONNECTED
Evolver toggle command. Sets torus model display to do each body as a connected, wrapped surface. Not an on-off toggle. 3-way toggle with clipped and raw_cells. Synonym: connected_cells. Since slight motions during evolution can cause the wrap to change suddenly, there is a body boolean attribute "centerofmass" that causes the center of mass of a body to be remembered, and the next time a body is plotted, the wrap is adjusted so the center of mass is close to the previous center of mass. Default is ON.

## DETORUS_STICKY
Evolver toggle command. Controls whether the detorus command will identify coincident vertices, edges, and facets. The tolerance for identifying vertices is given by the variable detorus_epsilon.

## DETURCK
Evolver toggle command. Motion by unit velocity along normal, instead of by curvature vector.

## DIFFUSION
Evolver toggle command. Activates diffusion step each g command.

## DIRICHLET_MODE
When the facet_area method is being used to calculate areas in hessian commands, this toggles using an approximate facet_area hessian that is positive definite. This permits hessian iteration to make big steps in a far-from-minimal surface without fear of blowing up. However, since it is only an approximate hessian, final convergence to the minimum can be slow. Linear model only. Does convert_to_quantities implicitly. Another variant of this is triggered by sobolev_mode.

## EFFECTIVE_AREA
Evolver toggle command. In area normalization, the resistance factor to motion is taken to be only the projection of the vertex star area perpendicular to the motion. If squared mean curvature is being calculated, this projected area is used in calculating the curvature.

## ESTIMATE
Evolver toggle command. Activates estimation of energy decrease in each gradient descent step ( g command). For each "g" iteration, it prints the estimated and actual change in energy. The estimate is computed by the inner product of energy gradient with actual motion. Useful only for a fixed scale factor much less than optimizing, so linear approximation is good. The internal variable estimated_change records the estimated value.

## FACET_COLORS
Evolver toggle command. Enables coloring of facets in certain graphics interfaces (e.g. xgraph). If off, facet color is white. Default on.

## FORCE_DELETION
Evolver toggle command. In the soapfilm model, overrides the refusal of the delete command to delete edges or facets when that would create two edges with the same endpoints. Sometimes it is necessary to have such edges, for example in pinching off necks. But usually it is a bad idea. Also see star_finagling. Default is off.

## FORCE_EDGESWAP
Evolver toggle command. Toggle. Makes the "u" or "equiangulate" or "edgeswap" commands skip certain tests and do the swap anyway. The skipped tests are: (1) the two vertices of the flipped edge are distinct, (2) creating two facets with the same vertices. Meant only for rare cases when you really know what you are doing. You should not leave this toggle in the ON state; turn it OFF after you have done the recalcitrant edge swap.

## FULL_BOUNDING_BOX
Evolver toggle command. Causes bounding box in PostScript output to be the full window, rather than the actual extent of the surface within the window. Default off.

## FUNCTION_QUANTITY_SPARSE
Evolver toggle command. For named quantities defined as functions of named methods, this toggles the use of sparse matrices in calculating hessians.

## GRAVITY
Evolver toggle command. Includes the gravitational energy of bodies with density in total energy. The gravitational constant can be set in the top of the datafile with "gravity_constant = value", or with the runtime command "G value".

## GV_BINARY
Evolver toggle command. Toggles sending data to geomview in binary format, which is faster than ascii. Default is binary on SGI, ascii on other systems, since there have been problems with binary format on some systems. Ascii is also useful for debugging.

## HESSIAN_DIFF
Evolver toggle command. Toggles computing the hessian matrix by finite differences. Used only for debugging, since it is very slow.

## HESSIAN_DOUBLE_NORMAL
Evolver toggle command. When hessian_normal is also on, and the space dimension is even, then the normal vector components in the last half of the dimensions are copies of the components in the first half. Sounds weird, huh? But it is useful in calculating the stability of cylindrically symmetric surfaces using a string model in 4D.

## HESSIAN_NORMAL
Evolver toggle command. Constrains Hessian to move each vertex perpendicular to the surface. This eliminates all the fiddly sideways movement of vertices that makes convergence difficult. Perpendicular is usually defined as the volume gradient, but at triple (and higher) junction lines it is a subspace perpendicular to the line, and singular points where several triple lines meet have full degrees of freedom. See hessian_normal_one to alter this behavior.

## HESSIAN_NORMAL_ONE
Evolver toggle command. If this and hessian_normal are on, then the normal at any point will be one dimensional. This is meant for soap films with Plateau borders, where there are triple junctions with tangent films. Ordinary hessian_normal permits lateral movement of such triple junctions, but hessian_normal_one does not. Valid only for string model in 2D and soapfilm model in 3D. The normal vector is computed as the eigenvector of the largest eigenvalue of the sum of the normal projection matrices of all edges or facets adjoining a vertex.

## HESSIAN_NORMAL_PERP
Evolver toggle command. If this is on, then the Hessian linear_metric uses only the component of the normal perpendicular to the facet or edge. This raises eigenvalues slightly.

## HESSIAN_QUIET
Evolver toggle command. Toggles suppression of printing of information during hessian calculations. Default is on.

## HESSIAN_SPECIAL_NORMAL
Evolver toggle command. When hessian_normal is on, this toggles using a special vectorfield for the direction of the perturbation, rather than the usual surface normal. The vectorfield is specified in the hessian_special_normal_vector section of the datafile header. Beware that hessian_special_normal also applies to the normal calculated by the vertex_normal attribute and the normal used by regular vertex averaging.

## HOMOTHETY
Evolver toggle command. Adjust total volume of all bodies to fixed value after each iteration by uniformly scaling entire surface.

## IMMEDIATE_AUTOPOP
Evolver toggle command. Modifies the autopop mode. Causes deletion of a short edge or small facet immediately upon detection, before proceeding with further detection of small edges or facets. Original behavior was to do all detection before any elimination, which could cause bad results if a lot of edges got short simultaneously. Default off for backward compatibility, but you should probably turn it on.

## INTERP_BDRY_PARAM
Evolver toggle command. For edges on parametric boundaries, calculate the parameter values of new vertices (introduced by refining) by interpolating parameter values, rather than extrapolating from one endpoint. Useful only when parameters are not periodic.

## INTERP_NORMALS
Evolver toggle command. Display using interpolated vertex normals for shading for those graphics interfaces that support it.

## ITDEBUG
Evolver toggle command. Prints some debugging information during a 'g' step. For gurus only.

## JIGGLE
Evolver toggle command. Toggles jiggling on every iteration.

## KRAYNIKPOPEDGE
Toggles edge-popping mode ( O or pop commands) in which poppable edges look for adjacent facets of different edge_pop_attribute values to split off from the original edge; failing that it reverts to the regular mode of popping the edge. This is meant to give the user greater control on how edge popping is done. It is up to the user to declare the edge_pop_attribute integer facet attribute and assign values.

## KRAYNIKPOPVERTEX
Toggles 3D vertex popping mode in which a poppable vertex is examined to see if it is a special configuration of six edges and 9 facets. If it is, a special pop is done that is much nicer than the default pop.

## K_ALTITUDE_MODE
Evolver toggle command. When on, the 'K' command uses the altitude from a vertex rather than the median to subdivide a skinny triangle.

## KUSNER
Evolver toggle command. Calculation of squared curvature by edge formula rather than vertex formula.

## LABELFLAG
Evolver toggle command. When on, the postscript command will print element labels in the postscript file. Synonym for ps_labelflag.

## LITTLE_ENDIAN
Evolver toggle command. Controls the order of bytes in binary_printf numerical output. Little-endian is least significant byte first. To change to big-endian, use big_endian, not "little_endian off".

## LINEAR_METRIC
Evolver toggle command. Eigenvalues and eigenvectors of the Hessian are defined with respect to a metric. This command toggles a metric that imitates the smooth surface natural metric of L_2 integration on the surface. Use with hessian_normal to get eigenvalues and eigenvectors similar to those on smooth surfaces.

## MEMDEBUG
Evolver toggle command. When ON, the ' c ' command prints full memory usage statistics on some systems. Also, each allocation or freeing of memory is printed. Causes heap checking to be done on some systems at each memory operation.

## METIS_FACTOR
Evolver toggle command. Computes and uses an ordering for Hessian factoring using the METIS library of Karypis and Kumar, if this library has been compiled into the Evolver.

## METRIC_CONVERT
Evolver toggle command. If a Riemannian metric is defined, whether to use the metric to do gradient form to vector conversions. Synonym: metric_conversion.

## NO_DUMP
This is a per-edge or per-facet toggle, or boolean attribute. When set, it prevents the value of a variable from being written out by the "dump" or "d" commands. Useful with the "replace_load" and "add_load" commands when reloading dumps of the current file and you want to preserve variable values that would otherwise be overwritten by loading the dump file, which has variables declared in the top of the datafile by default. "no_dump" variables are instead written in the "read" section of the dump file, so the dump file will load as a stand-alone file Works on global variables and arrays. Syntax (run-time commands; not in top of datafile):

```text
   variable.no_dump on
   variable.no_dump off


```
The no_dump declaration must come after the variable exists. Example: replace_load "temp.dmp"

## NORMAL_CURVATURE
Evolver toggle command. Calculation of squared curvature by taking area of vertex to be the component of the volume gradient parallel to the mean curvature vector. This applies to the sqcurve vertex attribute and the old-style specification of squared mean curvature in the top of the datafile by the keyword squared_curvature.

## NORMAL_MOTION
Evolver toggle command. Projects motion to surface normal, defined as the volume gradient. May be useful with squared curvature if vertices tend to slither sideways into ugly patterns.

## OLD_AREA
Evolver toggle command. In the string model with area normalization, at a triple vertex Evolver normally tries to calculate the motion so that Von Neumann's Law will be obeyed, that is, the rate of area change is proportional to the number of sides of a cell. If old_area is ON, then motion is calculated simply by dividing force by star area.

## PINNING
Evolver toggle command. Check for vertices that can't move because adjacent vertices are not on same constraint when they could be. Obscure.

## POP_DISJOIN
Evolver toggle command. Changes the behavior of popping edges and vertices to act like merging Plateau borders, i.e. produce disjoined films instead of films joined with cross-facets. In the edge case, if four facets meet along an edge and two opposite bodies are the same body, then popping the edge will join the bodies if pop_disjoin is in effect. In the vertex case, if the vertex has one body as an annulus around it, then the vertex will be separated into two vertices so the annulus becomes a continuous disk. This is all done regardless of the angles at which facets meet. Applies to pop, o, and O commands.

## POP_ENJOIN
Evolver toggle command. Changes the behavior of popping vertices in the soapfilm model so that when two distinct cones are detected meeting at a common vertex, the popping result is a widening of the cone vertex into a neck rather than a disjoining of the cones. meet. Applies to pop and o commands.

## POP_TO_EDGE
Evolver toggle command. The non-minimal cone over a triangular prism frame can pop in two ways. If this toggle is on, then popping to an edge rather that a facet will be done. Default off.

## POP_TO_FACE
Evolver toggle command. The non-minimal cone over a triangular prism frame can pop in two ways. If this toggle is on, then popping to a facet rather that an edge will be done. Default off.

## PS_CROSSINGFLAG
Evolver toggle command. When on and the string model is in effect, the postscript command will show background edges with a break where foreground edges pass in front. "crossingflag" is an old name for "ps_crossingflag".

## DEBUG
Evolver toggle command. Print YACC debug trace of parsing of commands. You really don't want to do this; it is for my private use in development.

## PS_GRIDFLAG
Evolver toggle command. If toggled on, the postscript command will show all edges of displayed facets, instead of just those satisfying the current edge show condition. "gridflag" is an old name for "ps_gridflag".

## PS_LABELFLAG
Evolver toggle command. When on, the postscript command will print element labels in the postscript file. Synonym for labelflag.

## PS_CMYKFLAG
Evolver toggle command. When on, the postscript command will do CMYK color instead of RGB in the file it creates. Default is OFF.

## PS_COLORFLAG
Evolver toggle command. When on, the postscript command will do color.

## QUANTITIES_ONLY
Evolver toggle command. Inactivates all energies except named quantities. Meant for programmer's debugging use.

## QUIET
Evolver toggle command. Suppresses all normal output messages automatically generated by commands. Good while running scripts, or for loading datafiles with long read sections. Explicit output from print, printf, and list commands will still appear, as will prompts for user input. Applies to redirected output as well as console output. An error or user interrupting a command (i.e. with CTRL-C) will turn QUIET off, for sanity.

## QUIETGO
Evolver toggle command. Suppresses only g iteration step output.

## QUIETLOAD
Evolver toggle command. Suppresses echoing of files being read in. This applies to the read section at the end of the datafile and any files read in with the read command. This toggle does not get reset at the start of a new datafile. This toggle can be set with the -Q command line option, to suppress echoing in the first datafile loaded. Default is OFF.

## POST_PROJECT
Evolver toggle command. Introduces extra projections to volume and fixed quantity constraints each g iteration. If convergence fails after 10 iterations, you will get a warning message, repeated iterations will stop, and the internal variable iteration_counter will be negative.

## RAW_CELLS
Evolver toggle command. Sets torus model display for plain, unwrapped facets. Not an on-off toggle; 3-way toggle with clipped and connected.

## RGB_COLORS
Evolver toggle command. Toggles graphics to use user-specified red-green-blue components of color for elements rather than the color attribute indexing the pre-defined 16 color palette. The individual element rgb values are in element extra attributes: ergb for edges, frgb for facets, and fbrgb for facet backcolor. It is up to the user to define these attributes; if they are not defined, then they are not used and do not take up space. If frgb is defined but not fbrgb, then frgb is used for both front and back color. The attributes are real of dimension 3 or 4; if 4 dimensional, the fourth component is passed to the graphics system as the alpha value, but probably won't have any effect. The value range is 0 to 1. Be sure to initialize the rgb attributes, or else you will get an all-black surface. The attribute definitions to use are:

```text

   define edge attribute ergb real[3]
   define facet attribute frgb real[3]
   define facet attribute fbrgb real[3]


```

## RIBIERE
Evolver toggle command. Makes the conjugate gradient method use the Polak-Ribiere version instead of Fletcher-Reeves. (The toggle doesn't turn on conjugate gradient.) Polak-Ribiere seems to recover much better from stalling. Ribiere is the default mode.

## ROTATE_LIGHTS
Evolver toggle command. When ON, this makes the lights rotate with the object in the graphics display. Default OFF.

## RUNGE_KUTTA
Evolver toggle command. Use Runge-Kutta method in a g iteration step (fixed scale factor only).

## SELF_SIMILAR
Evolver toggle command. If squared mean curvature energy is being used, this scales the velocity toward a self-similar motion. Applies only when the old top-of-datafile "squared_curvature" declaration is used, or the sqcurve named method. The global read-write variable self_sim_coeff is used as a multiplier.

## SEPTUM_FLAG
Evolver toggle command. For the "pop" command, this toggle will force the insertion of a dividing surface when the pop would otherwise leave an open passage between two sides.

## SHADING
Evolver toggle command. Toggles facet shading in certain graphics interfaces (xgraph, psgraph). Darkness of facet depends on angle of normal from vertical, simulating a light source above surface. Default is ON.

## SHOW_ALL_EDGES
Evolver toggle command. Controls the showing of all edges in the graphics window, regardless of the current "show edges ..." condition. Same as the 'e' key in the graphics window.

## SHOW_ALL_QUANTITIES
Evolver toggle command. By default, only explicitly user-defined named quantities are shown by the Q or v commands. If show_all_quantities is on, then all internal quantities created by option -q or by doing convert_to_quantities are also shown.

## SHOW_BOUNDING_BOX
Evolver toggle command. Controls showing the bounding box in graphics. Corresponds to the "o" key in the graphics window and the "b" command at the graphics prompt. Its advantage is that it lets a script set the bounding box state to a definite value.

## SHOW_INNER
Evolver toggle command. Display interior facets, those on 2 bodies.

## SHOW_OUTER
Evolver toggle command. Display outer facets, those on 0 or 1 body.

## SLICE_VIEW
Toggles use of slice view in graphics display.

## SMOOTH_GRAPH
Evolver toggle command. In string quadratic and Lagrange model, causes edges to be plotted with many subdivisions for smooth look. In soapfilm Lagrange model, causes edges and facets to be plotted with 8-fold subdivision rather than Lagrange order subdivision. Is not implemented in quadratic soapfilm model. Default off.

## SOBOLEV_MODE
Evolver toggle command. When the facet_area method is being used to calculate areas in hessian commands, this toggles using an approximate facet_area hessian that is positive definite. This permits hessian iteration to make big steps in a far-from-minimal surface without fear of blowing up. However, since it is only an approximate hessian, final convergence to the minimum can be slow. Linear model only. Does convert_to_quantities implicitly. Another variant of this is triggered by dirichlet_mode.

## SPARSE_CONSTRAINTS
Evolver toggle command. Toggles using sparse matrix techniques to accumulate and handle body and quantity gradients in iteration and hessian commands. Now the default.

## SQUARED_GRADIENT
Evolver toggle command. In hessian_seek, use minimizing the square of the gradient of the energy as the objective rather than minimizing the energy.

## STAR_FINAGLING
Evolver toggle command. In the soapfilm model, the delete command for edges or facets normally will not do the deletion if it would result in the creation of two edges with the same endpoints. Some simple configurations that cause this are detected and handled automatically, namely a "star" configuration in which there are three facets forming a triangle adjacent to the edge being deleted. Such a star is automatically removed by deleting one of its internal edges before deleting the original edge. But sometimes there are more complicated configurations that such unstarring won't handle, and then Evolver will not delete the edge unless the force_deletion toggle is on. An alternative is to first refine the edges that would have the common endpoints, and this is what the star_finagling toggle enables. Default off.

## THICKEN
Evolver toggle command. Whether to display differently colored sides of a facet separated by thickness. Default on. This helps prevent weird striping due to limited resolution of depth buffers.

## TORUS_FILLED
Evolver toggle command. Whether Evolver should treat one fixed volume as not fixed, for the purpose of avoiding redundant constraints in the case of a torus space being completely filled with bodies of fixed volume, for example a periodic foam.

## TRANSFORMS
Evolver toggle command. Toggles graphing multiple images of the surface, according to the view transforms defined in the datafile, or according to the current transform expression applied to the view transform generators defined in the datafile.

## VIEW_4D
Evolver toggle command. Toggles sending 4D information to geomview.

## VIEW_TRANSFORMS_USE_UNIQUE_POINT
Evolver toggle command. When view transforms are generated with transform_expr, Evolver weeds out duplicate transforms. By default, "duplicate" means the same transform matrix, but there are circumstances where different transform matrices carry the surface to the same spot. This toggle enables a mode whereby two transform matrices are deemed identical if they transform the point given by the vector view_transforms_unique_point[] to the same image point. The standard use is to make view_transforms_unique_point[] a vertex on the surface being transformed, for example The vector view_transforms_unique_point[] is pre-defined, so the use does not need to define it.

## VERBOSE
Evolver toggle command. Toggles printing of progress messages during surface modification commands such as refine, delete, notch, edgeswap, o, O.

## VISIBILITY_TEST
Evolver toggle command. Toggles an occluded-triangle test for graphics output that uses the Painter's Algorithm to produce 2D output (PostScript, Xwindows). This can greatly reduce the size of a PostScript file, but inspect the output since the implementation of the algorithm may have flaws.

## VOLGRADS_EVERY
Evolver toggle command. Toggles recalculating volume constraint gradients every projection step during constraint enforcement. Good for stiff problems.

## YSMP
Evolver toggle command. Toggles between Yale Sparse Matrix Package routines for factoring hessians, and my own minimal degree factoring. Default is YSMP off.

## ZENER_DRAG
Evolver toggle command. Toggles Zener drag feature, in which the velocity of the surface is reduced by a magnitude given by the variable zener_coeff, and the velocity is set to zero if it is smaller than zener_coeff. Back to top of Surface Evolver documentation. Index.
