Surface Evolver Documentation: single letter main commands

# Surface Evolver Documentation
Back to top of Surface Evolver documentation. Index.

## Single letter main commands
The oldest and most commonly used Surface Evolver commands are just single letters. Case is significant for these. Single letters are always interpreted as commands, so you may not use single letters for variable names. Single letter commands may be redefined.
Single letter commands may be summarized in five groups:

- Reporting:

- C Run consistency checks.
- c Report count of elements.
- e Extrapolate.
- i Information on status.
- v Report volumes.
- v List extra attributes.
- z Do curvature test.

- Model characteristics:

- A Display and set variables and various parameters.
- a Toggle area normalization
- b Set body pressures.
- f Set diffusion constant.
- G Set gravity.
- J Toggle jiggling on every move.
- k Set boundary gap constant.
- M Toggle linear/quadratic model.
- m Toggle fixed motion scale.
- p Set ambient pressure.
- Q Report or set quantities.
- U Toggle conjugate gradient method.
- W Homothety toggle.

- Surface modification

- g Go one iteration step. Often followed by a repetition count.
- j Jiggle once.
- K Skinny triangle long edge divide.
- l Subdivide long edges.
- N Set target volumes to actual.
- n Notch ridges and valleys.
- O Pop non-minimal edges.
- o Pop non-minimal vertices.
- r Refine triangulation.
- t Remove tiny edges.
- u Equiangulate.
- V Vertex averaging.
- w Weed out small triangles.
- y Torus duplication.
- Z Zoom in on vertex.

- Output:

- D Toggle display every iteration.
- d Dump surface to datafile.
- P Graphics output (geomview, Postscript, etc.).
- s Screen display (native graphics).

- Miscellaneous:

- F Toggle command logging.
- H,h,? Help screen.
- q,x Exit.

## Single letter redefinition
It is possible to reassign a single letter to your own command by the syntax

```text
 letter :::= command


```
but this should only be used in special circumstances, such as redefining 'r' to do additional actions along with refinement. The standard meaning can be restored with a null assignment:

```text
 letter :::=


```
Use single quotes around the letter to get the standard meaning, i.e. 'r' will do a standard refine when r has been redefined. Redefinitions are cleared when a new surface is loaded. Be careful when using redefined commands in defining other commands. Redefinition is effective on execution of the redefinition command, not on parsing. Redefinition is not retroactive to uses in previously defined commands, but restoring the standard meaning is retroactive. Examples:

## A
Single letter main command. Lists the current values of variables and named quantity values, moduli, and targets. Only explicitly user-defined named quantities are shown unless show_all_quantities is toggled on. You are allowed you to enter new values (except quantity values). The new value is entered as the number of the variable (from the list) and the new value. Exit by hitting RETURN on a blank line. All changes that can be made here can also be made with assignment commands.

## a
Single letter main command. Toggles area normalization of vertex forces and other gradients, to model motion by mean curvature. Meant to be used with a fixed scale factor. Be sure you have a small enough scale factor or else things tend to blow up. Reduce the scale factor temporarily after refinement, since triangle areas are cut by a factor of 4 but the old creases remain. When this option is ON, there is an optional check that can be made for facets that move too much. This is done by computing the ratio of the length of the normal change to the length of the old normal. If this exceeds the user-specified value, then all vertices are restored to their previous position. The user should reduce the motion scale factor and iterate again.

## b
Single letter main command. Permits user to interactively change body prescribed volumes or pressures. Prints old value for each body and prompts for new.

## C
Single letter main command. Runs various internal consistency checks. Synonym: check. If no problems, just prints "Checks completed." The number of errors found is stored in the variable check_count. The checks are:

- Element list integrity - checks that data structures are intact. This kind of error is probably an Evolver bug and should be reported.
- Facet-edge check - that if a facet adjoins an edge, then the edge adjoins the facet, and that the three edges around a facet link up. This kind of error is probably an Evolver bug and should be reported.
- Facet-body check - whether adjacent facets have the same body on the same side. Probably a user problem due to mis-oriented faces in body definitions in the datafile, or due to the surface getting kinked up at triple lines.
- Collapsed elements - check if endpoints of an edge are the same, and whether neighboring facets share more than one edge and two vertices. Not illegal, but you probably want to avoid.
After "C" or "check" command finishes, there are some variables that hold the number of errors of various types that were found:

- bad_next_prev_count - bad links in element linked lists.
- inconsistent_bodies_count - violations of adjacent facets having same bodies.
- edge_loop_count - edges that are loops on single vertices.
- edges_same_vertices_count - edge pairs with the same endpoints.
- facets_same_vertices_count - facet pairs with the same endpoints.
- bad_error_count - sum of the various types of errors that I consider serious enough that you should revise your evolution to avoid them. Bad links within element lists, and bad links between elements.

## c
Single letter main command. Prints count of elements and memory used. The memory is just the total of the element structures. On some systems, enabling " memdebug " will print more complete statistics on total memory usage. Synonym: counts.

## D
Single letter main command. Toggles updating graphics every iteration or other surface change. Default is to display. Status can also be changed or queried with the autodisplay toggle.

## d
Single letter main command. Dumps data to ASCII file in same format as initial data file. You will be prompted for a filename. An empty reponse will use the default dump name, which is the datafile name with a ".dmp" extension. Same as the dump command, except the dump command requires the filename as part of the command. Useful for checking your input is being read correctly, for saving current configuration, and for debugging.

## e
Single letter main command. Extrapolates total energy to infinite refinement if at least two r commands have been done. Uses last energy values at three successive levels of refinement, and uses a power law fit for the error. For best results, use only the r command to refine, and iterate to complete convergence at each level of refinement. Synonym: extrapolate.

## F
Single letter main command. Toggle logging of commands in file. If starting logging, you will be prompted for the name of a log file. Any existing file of that name will be appended to. Logging stops automatically when the surface is exited. Only correctly parsed commands are logged. Output resulting from commands is not logged. Responses to interactive single-letter commands are logged, but not responses to other interactive commands.

## f
Single letter main command. Sets diffusion constant. Prints old and prompts for new.

## G
Single letter main command. Toggles gravity on or off. Gravity starts ON if any body has a nonzero density; otherwise OFF. If followed by a value, sets gravity to that value. Otherwise prints old value of gravitational constant and prompts for new.

## g
Single letter main command. Do one iteration step. The output consists of the number of iterations left (for people who wonder how close their 1000 iterations are to ending), the area and energy, and the scale factor. g is commonly used with an iteration count, as in " g 100 ". The user can abort repeated iterations by sending an interrupt to the process (SIGINT, to be precise; CTRL-C or whatever on your keyboard). As a special dispensation to lazy users, the syntax " g n " is equivalent to " g n ". Synonym: go

## H,h,?
Single letter main command. Prints a very primitive help message listing common commands. help is much better, as it accesses the full HTML documentation. Or best, use a separate HTML browser on this documentation.

## i
Single letter main command. Prints miscellaneous information:

- Name of datafile
- Total energy
- Total area of facets
- Count of elements and memory usage
- Area normalization, if on
- LINEAR or QUADRATIC model
- Whether conjugate gradient on
- Order of numerical integration
- Scale factor value and option (fixed or optimizing)
- Diffusion option and diffusion constant value
- Gravity option and gravitational constant value
- Jiggling status and temperature
- Gap constant (for gap energy, if active)
- Ambient pressure (if ideal gas model in effect)

## J
Single letter main command. Toggles jiggling on every iteration of the g command. If jiggling gets turned on, prompts for temperature value. Default temperature is the value of the temperature internal variable.

## j
Single letter main command. Jiggles all vertices once. Meant to be used for simulated annealing. Useful for shaking up surfaces that get in a rut, especially crystalline integrands. You will be prompted for a "temperature" which is used as a scaling factor, if you don't give a temperature with the command. Default temperature is the value of the jiggle_temperature internal variable, which starts as 0.05. The actual jiggle is a random displacement of each vertex independently with a Gaussian distribution with deviation being the temperature times the mean edge length. See the longj command for a user-definable perturbation.

## K
Single letter main command. Finds skinny triangles whose smallest angle is less than a specified cutoff. You will be prompted for a value if you don't give a value on the command line. Such triangles will have their longest edge subdivided. Should be followed with tiny edge removal ( t) and equiangulation ( u). By default, the long edge is subdivided at its midpoint, but if you do "k_altitude_mode on" then it will be subdivided at the foot of the altitude from the opposite vertex.

## k
Single letter main command. Sets "gap constant" for gap energy for convex constraints. Adds energy roughly proportional to area between edge and boundary. You will be prompted for a value if you don't give a value on the command line. Normal values are on the order of magnitude of unity. Value k = 1 is closest to true area. Use 0 to eliminate the energy.

## l (lower case L)
Single letter main command. Subdivides long edges, creating new facets as necessary. You will be prompted for a cutoff edge length, if you don't give a value with the command. Existing edges longer than the cutoff will be divided once only. Newly created edges will not be divided. Hence there may be some long edges left afterward. If you enter h, you will get a histogram of edge lengths. If you hit RETURN with no value, nothing will be done. It is much better to use the refine command r than to subdivide all edges. A synonym for " l value " is " edge_divide value ". This command does not respect the no_refine attribute.

## M
Single letter main command. Sets model type to linear, quadratic, or Lagrange. Changing from LINEAR to QUADRATIC adds vertices at the midpoints of each edge. Changing from QUADRATIC to LINEAR deletes the midpoints. Optionally takes new model type ( 1 for LINEAR, 2 for QUADRATIC, > 2 for Lagrange. ) on command line. Otherwise will prompt you.

## m
Single letter main command. Toggles quadratic search for optimal global motion scale factor. If search is toggled OFF, you will be prompted for a fixed scale factor. If you give a value with the command, then you are setting a fixed scale factor.

## N
Single letter main command. Set body target volumes to current actual volumes.

## n
Single letter main command. Notching ridges and valleys. Finds edges that have two adjacent facets, and those facets' normals make an angle greater than some cutoff angle. You will be prompted for the cutoff angle (radians) if you don't give a value with the command. Qualifying edges will have the adjacent facets subdivided by putting a new vertex in the center. Should follow with equiangulation. In the string model, it will refine edges next to vertices with angle between edges (parallel orientation) exceeding the given value. Optionally takes cutoff angle on command line.

## O
Single letter main command. Pop non-minimal edges. Scans for edges with more than three facets attached. Splits such edges into triple-facet edges. Splits propagate along a multiple edge until they run into some obstacle. This command is meant for surfaces that have equal tension on all facets. Also tries to pop edges on walls properly. For finer control on which edges to try, use the pop command. Try octa.fe for an example.

## o
Single letter main command. Pop non-minimal vertices. This command scans the surface for vertices that don't have the topologies of one of the three minimal tangent cones that are legal in soap films (plane, triple edge, tetrahedral point). These are "popped" to proper local topologies. The algorithm is to replace the vertex with a sphere. The facets into the original vertex are truncated at the sphere surface. The sphere is divided into cells by those facets, and the largest cell is deleted, which preserves the topology of the complement of the surface. A special case is two cones meeting at a vertex; if the cones are broad enough, they will be merged, otherwise they will be split. In case of merging cones, if both cone interiors are defined to be part of the same body, then no facet is placed across the neck created by the merger; if they are different bodies or no bodies, a facet will be placed across the neck. Only vertices in the interior of a surface, not fixed or on constraints or boundaries, are tested. Try popstr.fe and octa.fe for examples.

## P
Single letter main command. Produce graphics output files. "P" is for "picture". This brings up a menu, unless you give the menu option on the command line. For the 2D graphics options, the view is the same as seen with the s command. For options that output to a file, you will be prompted for a filename. Some other possible options you may be asked:

Display raw cells, connected bodies or clipped cells? (0,1,2)

If you are doing torus model, you will be asked for a display option, unless you have already set one.

Do normal interpolation?

Some formats are capable of doing interpolation between vertex normals for smoother shading, and you will be asked if you want to do that.

Do inner, outer, or all surfaces? (i,o,a)

When bodies are present, there is an option to plot the inner surfaces(adjacent to two bodies), outer surfaces (adjacent to 0 or 1 bodies), or all surfaces of the bodies.

Do body colors?

This gives you a chance to color the bodies differently. If you do, the current colormap file will be used to color the bodies according to id number. This scheme is a relict of early days of the Evolver, and it is suggested that you use the color, frontcolor and backcolor facet attributes instead.

Enter name of colormap file:

If there is no current colormap file, you will be prompted. The colormap file has the format of RGB values, one set per line, values between 0 and 1. (This map may not be effective on all devices.)

Thicken? (n | y [thickness(0.001)])

You may also be asked if you want thickening. If you do, each facet will be recorded twice, with opposite orientations, with vertices moved from their original positions by the thickening distance (which the option lets you enter) in the normal direction. The normal used at each vertex is the same as used for normal interpolation, so all the facets around a planar vertex will have that vertex moved the same amount. Triple junctions will be separated. Thickening is good for rendering programs that insist on consistently oriented surfaces, or that have problems with show-through of the backside of a surface. Choosing 'y' or 'n' will reset the thicken toggle. If you answer 'y', you can optionally specify the thickness, which defaults to the value of the thickness internal variable.

The menu choices for types of output are:

1. Pixar file

For Pixar format. Actually same format as option 2.

2. OOGL file

This is a file in a file format used by geomview, which is Object Oriented Graphics Language. Suitable for direct input into geomview.

3. PostScript file

Generates a PostScript file.

4. Triangle file

A private format file, just listing data. Not much use any more.

5. Softimage file

Output file in Softimage format.

8. Start simultaneous geomview

If you have the geomview package installed, this command will start geomview and display the current surface. Changes to the surface are automatically displayed unless autodisplay is toggled off.

9. End simultaneous geomview

Terminates any geomview program or pipe.

A. Start OOGL pipe.

Geomview uses a pipe interface at the moment. This starts a named pipe with geomview output, but without invoking geomview. You will be told the name of the pipe, and it is up to you to start a pipe reader. Evolver blocks until a pipe reader is started. This is useful for having a second instance of Evolver feed a second surface to geomview by having geomview load the pipe. Also good for checking exactly what Evolver is sending to geomview. The geompipe command does the same thing. Terminate the pipe with "P 9". Note that only one geomview output at a time is possible, so you can't have a geomview display and separate pipe active at the same time.

B. End OOGL pipe.

Same as option 9.

## p
Single letter main command. Sets ambient pressure in ideal gas model. If you don't give a value with the command, you will be prompted. A large value gives more incompressible bodies.

## Q
Single letter main command. Report current values of user-defined method instances and named quantities. If the show_all_quantities toggle is on, then internal quantities and method instances are also shown. This is particularly informative if convert_to_quantities has been done (same as -q command line option), since then internal values such as constraint integrals are in the form of method instances.

## q
Single letter main command. Syntax:

```text
    q
    q expr


```
Alone, "q" brings up a prompt to enter a new datafile. At this prompt, hitting the Enter key will return to the current surface, another "q" will exit Evolver, and anything else will be taken to be the name of a new datafile. When "quit" is followed by a value, Evolver exits immediately, and uses the value as the exit code, which is useful when running Evolver in a script or from some other program. Quitting Evolver automatically closes any graphics windows, and does not save anything. Same as "quit" command. "quit", "bye", and "exit" are synonyms.

## r
Single letter main command. Refines the triangulation. Edges are divided in two, and facets are divided into four facets with inherited attributes. Edges and facets with the no_refine attribute set are not refined. Reports the number of element structures and amount of memory used by those structures.

## s
Single letter main command. Shows the surface with screen graphics. Goes into the graphics command mode. Torus model surfaces have display options you will be asked for the first time. The graphics window may be closed with the close_show command.

## t
Single letter main command. Eliminates tiny edges and their adjacent facets. You will be prompted for a cutoff edge length if you don't give a value with the command. If you enter h, you will get an edge length histogram. If you hit RETURN without a value, nothing will happen. Some edges may not be eliminable due to being FIXED or endpoints having different attrtibutes from the edge.

## U
Single letter main command. This toggles conjugate gradient mode, which will usually give faster convergence to the minimum energy than the default gradient descent mode. The only difference is that motion is along the conjugate gradient direction. The scale factor should be in optimizing mode. The conjugate gradient history vector is reset after every surface modification, such as refinement or equiangulation. After large changes (say, to volume), run without conjugate gradient a few steps to restore sanity.

## u
Single letter main command. This command, called "equiangulation", tries to polish up the triangulation. In the soapfilm model, each edge that has two neighboring facets (and hence is the diagonal of a quadrilateral) is tested to see if switching the quadrilateral diagonal would make the triangles more equiangular. For a plane triangulation, a fully equiangulated triangulation is a Delaunay triangulation, but the test makes sense for skew quadrilaterals in 3-space also. It may be necessary to repeat the command several times to get complete equiangulation. The edgeswap command can force flipping of prescribed edges.
In the simplex model, equiangulation works only for surface dimension 3. There, two types of move are available when a face of a tetrahedron violates the Delaunay void condition: replacing two tetrahedra with a common face by three, or the reverse operation of replacing three tetrahedra around a common edge by two, depending on how the condition is violated. This command is inoperative in the string model.

## V
Single letter main command. Vertex averaging. For each vertex, computes new position as area-weighted average of centroids of adjacent facets. Only adjacent facets with the same constraints and boundaries are used. Preserves volumes, at least to first order. See the rawv command for vertex averaging without volume preservation, and rawestv for ignoring likeness of constraints. Vertices on triple edges are averaged only with adjacent vertices on the triple edge, and then only if there are exactly two neighboring triple edge vertices. Fixed vertices do not move. Vertices on constraints are projected back onto their constraints. The computation of new vertex positions are all done before any vertex is moved. For sequential movement applied to a subset of vertices, see the vertex_average command.

## v
Single letter main command. Shows target volume, actual volume, and pressure of each body. Also shows named quantities. Pressures are really the Lagrange multipliers. Pressures are computed before an iteration, so the reported values are essentially are one iteration behind. Synonym: show_vol

## W
Single letter main command. Toggles homothety. If homothety ON, then after every iteration, the surface is scaled up so that the total volume of all bodies is 1. Meant to be used on surfaces without any blowup constraints of any kind, to see the limiting shape as surface collapses to a point.

## w
Single letter main command. Tries to weed out small triangles. You will be prompted for the cutoff area value if you don't give a value with the command. If you enter h, you will get a histogram of areas to guide you. If you hit RETURN with no value, nothing will be done. Some small triangles may not be eliminable due to constraints or other such obstacles. The action is to eliminate an edge on the triangle, eliminating several facets in the process. Edges will be tried for elimination in shortest to longest order. WARNING: Although checks are made to see if it is reasonable to eliminate an edge, it is predicated on facets being relatively small. If you tell it to eliminate all below area 5, Evolver may eliminate your entire surface without compunction.

## X
Single letter main command. List the current extra attributes, including name, dimension, type, size in bytes, and offset within the element structure. Some internal attributes are also listed, whose names begin with a double underscore.

## x
Single letter main command. Same as q. Exit Evolver, or start new surface.

## y
Single letter main command. Torus duplication. In torus model, prompts for a period number (1,2, or 3) and then doubles the torus unit cell in that direction. Useful for extending simple configurations into more extensive ones.

## Z
Single letter main command. Zooms in on a vertex. Asks for vertex number and radius. Number is as given in vertex list in datafile. Beware that vertex numbers change in a dump (but correct current zoom vertex number will be recorded in dump). Eliminates all elements outside radius distance from vertex 1. New edges at the radius are made FIXED. Meant to investigate tangent cones and intricate behavior, for example, where wire goes through surface in the overhand knot surface. Zooming is only implemented for surfaces without bodies.

## z
Single letter main command. Do curvature test on QUADRATIC model. Supposed to be useful if you're seeking a surface with monotone mean curvature. Currently checks angle of creases along edges and samples curvature on facet interiors. Orientation is with respect the way facets were originally defined. Deprecated.
Back to top of Surface Evolver documentation. Index.
