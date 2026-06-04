Surface Evolver Documentation: commands

# Surface Evolver Documentation
Back to top of Surface Evolver documentation. Index.

# Surface Evolver command language
The Surface Evolver has an interactive command language. It has variables, expressions, subroutines, conditionals,iteration constructs, subroutines and functions with arguments, local variables, and arrays. But not structures or objects or pointers. Variables are either floating point, string, or subroutine names. The Evolver command language continues to grow by accretion, and it looks like it's headed towards a full programming language.

- Command input
- Command separator
- Compound commands
- Command repetition
- User-defined commands
- User-defined procedures
- User-defined functions
- Assignment commands

- Permanent assignment commands
- Local scope
- Redirecting and piping output
- Control structures
- Element generators
- Single letter commands
- Toggle commands
- General commands

## Command input
The Surface Evolver command interpreter reads from an input stream, which may be from the end of the datafile, from a file given on the system command line, from stdin (the terminal), or from a file given in a read command.
The interactive command prompt is " Enter command: ".
Commands are read one at a time, parsed, and executed. By default, a line is expected to contain a complete command, so no special end-of-command token is needed.
Multi-line commands may be entered by enclosing them in braces {...}. If a line ends while nested in braces or parenthesis, Evolver will ask for more input with the prompt " more> ". It will also ask for more if the line ends with certain tokens (such as `+') that cannot legally end a command. Unclosed quotes will also ask for more, and embedded newlines will be omitted from the final string. Explicit continuation to the next line may be indicated by ending a line with a backslash ( linesplicing). You may want to use the read command to read long commands from a file, since there is no command line editing.
Successfully parsed commands are saved in a history list, up to 100 commands. They may be accessed with !! for the last command or ! string for the latest command with matching initial string. ! n will repeat a command by history list number. The command will be echoed. The saved history list may be printed with the history command.
Some single-letter commands require interactive input. For those, there are equivalent commands that take input information as part of the command. This is so commands may be read from a script without having to put input data on additional lines after the command, although that can still be done for the single-letter versions.
General note: Some commands will prompt you for a value. A null response (just Enter key) will leave the old value unchanged and return you to the command prompt. On options where a zero value is significant, the zero must be explicitly entered. Commands that need a real value will accept an arbitrary expression.
Many commands that change the surface or change the model will cause energies and volumes to be recalculated. If you suspect a command has not done this, the recalc command will recalculate everything. It will also update any automatic display.
In the command syntax descriptions, keywords are sometimes shown in upper case, although case is irrelevant in actual commands, except for single-letter commands.

## Command separator
Several commands on the same line or within a compound command must be separated by a semicolon. A semicolon is not needed after the last command, but won't hurt. Do not use a semicolon after the first command in an if then else command. Do use a semicolon to separate a compound command from the next. Example:

## Compound commands
Curly braces group a list of commands into one command. The commands are separated by semicolons. A semicolon is needed after a compound command within a compound command to separate it from following commands (note this is different from the C language). Do not use a semicolon after the first command in an if then else command. An empty compound command {} is legal. Examples:

## Command repetition
Certain types of commands can be repeated a number of times by following the command with an integer. Be sure to leave a space between a single-letter command and the expression lest your command be interpreted as one identifier. To avoid several types of confusion, only certain types of commands are repeatable:

- Single letter commands that don't have optional arguments ( K,k,l,t,j,m,n,p,w,y,P,M,G have optional arguments),
- Compound commands in braces,
- User-defined command names.
- Redefined single-letter commands.

## Assignment commands
The assignment operator:= can be used to assign values to various entities. Note that ':= ' is used for assignment, not ' = '. The C-style arithmetic assignments +=, -=, *=, and /= work. For example, " val += 2 " is equivalent to " val := val + 2 ". These also work in other assignment situations where I thought they made sense, such as attribute assignment. Possible assignments:

- User-defined commands, Ex: gogo := {g 100; r; g 100}
- User-defined variables, Ex: foo := 2.3
- Writable internal variables, Ex: scale := 0.1
- Named quantity modulus, target, and volconst. Syntax:

```text
   quantityname.modulus := expr
   quantityname.target := expr
   quantityname.volconst := expr

```

- Method instance modulus. Syntax:

```text
   instancename.modulus := expr


```

## Permanent assignment commands
The permanent assignment operator::= can be used to make assignments to variables and commands that are not forgotten when a new datafile is loaded. Such a command may only make reference to permanent variables, permanent commands, and internal variables. See the permload command for an example of use.

## User-defined commands
Users may define their own commands with the syntax The shortest complete command on the right side is used. Thus " gg := g 10; u " would give gg the same value as " gg := g 10 ". It is wise and strongly advised to use braces to enclose the command on the right side so the parser can tell it's a command and not an expression. Also multiline commands then don't need linesplicing. Do not try to redefine single-letter commands this way; use:::=. Example:

## User-defined procedures
Users may define their own procedures with arguments with the syntax Right now the implemented types for arguments are real and integer. The argument list can be empty. Example: Note that the procedure arguments act as local variables, i.e. their scope is the procedure body, and they have stack storage so procedures may be recursive. Procedure prototypes may be used to declare procedures before their bodies are defined with the same syntax, just replacing the body of the procedure with a semicolon. Prototype syntax:

```text

   PROCEDURE identifier ( type arg1, type arg2, ... );


```
Note that a procedure is used as a command, and a function is used as a value in a numerical expression.

## User-defined functions
Users may define their own functions that have arguments and return values with the syntax

```text

   FUNCTION type identifier ( type arg1, type arg2, ... )
   { commands }


```
Right now the implemented types for return value and arguments are real and integer. The argument list can be empty. The return value is given in a return expr statement. Example: Note that the function arguments act as local variables, i.e. their scope is the function body, and they have stack storage so functions may be recursive. Function prototypes may be used to declare functions before their bodies are defined with the same syntax, just replacing the body of the function with a semicolon. Prototype syntax:

```text

   FUNCTION type identifier ( type arg1, type arg2, ... );


```
Note that a procedure is used as a command, and a function is used in a numerical expression.

## Variable assignment
Values can be assigned to variables. Values can be numeric or string. The variable names must be two or more letters, in order they not be confused with single-letter commands. Syntax:

```text

   identifier := expr
   identifier := stringexpr


```
If the variable does not exist, it will be created. These are the same class of variables as the adjustable parameters in the datafile, hence are all of global scope and may also be inspected and changed with the ' A ' command. Examples:

## Local scope
The scope of a variable name may be restricted to a compound command block by declaring the name to be local. Example: Using local variables is good for avoiding pollution of global namespace and for writing recursive functions (storage space for locals is allocated on the runtime stack). Note that the local declaration is a scope declaration, not a type declaration. Also, it cannot be combined with initialization of the variable (yet). Multiple names may be declared in one local statement, separated by commas:

```text

   local inx,jnx,knx;


```
Array names may also be local, so their storage space is allocated on the stack and automatically deallocated on exit from the function or procedure, but the define statement for size must be separate:

```text

   local myvector;
   define myvector real[32];


```
A local array may have its dimensions be expressions that change for iterations of a loop; the array will be reallocated if necessary each time its define statement is executed.
Function arguments also act as local variables.

## Redirecting and piping command output
The output of a command can be redirected to a file with the unix-style append symbol ' >> '. This appends output to the file; it does not erase any existing file. Syntax:

```text

   command >> stringexpr


```
To write the file from the beginning, overwriting any existing file, the output of a command can be redirected with the symbol ' >>> '. Syntax:

```text

   command >>> stringexpr


```
Redirection with ` > ' is not available due to the use of ` > ' as an comparison operator.
Standard redirection does not apply to error messages, including output done with "errprintf", on the assumption that the user wants them visible on the screen while a script runs. However, error messages can be redirected using ' >>2 ' and ' >>>2 '. The "2" comes from the fact that in popular operating systems the standard error output is internally file number 2. Redirection of error messages could be useful for example in saving the output of the "C" or "chack" commands.
The output of a command can be piped to a system command using the unix-style pipe symbol ` | '. Syntax: The stringexpr is interpreted as a system command.

## Control structures
The following control structures are available in the Evolver commmand language:

- if ... then ... else
- do ... while ....
- while .... do ...
- for
- foreach
- break
- continue
- return

## IF ... THEN ... ELSE
Commands may be conditionally executed by the syntax

```text

   IF expr THEN command

   IF expr THEN command ELSE command


```
expr is true if nonzero. Parentheses around expr are not needed, but do not hurt. Do not use a semicolon to end the first command. Examples;

## WHILE ... DO ...
Command syntax for pretest iteration loop. Syntax:

```text

  WHILE expr DO command


```
expr is true if nonzero. Parentheses around expr are not needed, but do not hurt. Example: DO ... WHILE ... Command syntax for posttest iteration loop. Syntax: expr is true if nonzero. Parentheses around expr are not needed, but do not hurt. Example:

## FOR
This is the Evolver's version of the C language "for" construct. Syntax: The first command is the initialization command; note that it is a single command, rather than an expression as in C. If you want multiple commands in the initialization, use a compound command enclosed in curly braces. The middle expression is evaluated at the start of each loop iteration; if its value is true (i.e. nonzero) then the loop is executed; otherwise the flow of control passes to the command after command3. The command2 is executed at the end of each loop iteration; again, it is a single command. The body of the loop is the single command command3, often a compound command. Note: Command3 should end with a semicolon, unless it is the if clause of an if-then statement. Examples:

## FOREACH
Repeat a command for each element produced by an element generator. Syntax:

```text

   FOREACH generator DO command


```

## BREAK
Command syntax for exiting loops. Syntax:

```text

   BREAK

   BREAK n


```
The first form exits the innermost current loop. The second form exits n loops. Note: Commands with repetition counts do not qualify as loops. Example:

## CONTINUE
Command syntax for skipping the rest of the body of the current loop, and going to the next iteration of the loop.

```text

   CONTINUE

   CONTINUE n


```
The second form exits the innermost n -1 loops, and skips to the loop control of the n th innermost loop. Note: Commands with repetition counts do not qualify as loops. Example:

## RETURN
Command syntax for exiting the current command or procedure or function. Syntax:

```text

   RETURN

   RETURN expr


```
This is essentially a return from a subroutine. If the current command is a user-defined command called by another command, the parent command continues. Example: If one is returning from a procedure, then one needs a numeric return value, e.g.

## Element generators
One feature different from ordinary C is the presence of generators of sets of geometric elements. These occur wherever an element type ( vertices, edges, facets, bodies, singular or plural) appears in a command. Attributes of the iteration element may be used later in the command. The general syntax of a generator is

```text

  elementgen name WHERE expr


```
elementgen may be

- a multiple element generator, which can be

- an element type, vertex, edge, facet, or body, which generates all elements of that type in the surface. But new elements created during a loop will not be generated, so " refine edges " will refine all existing edges just once.
- a single element subelement. The implemented subelements are:

- of a vertex: edge, facet (in no particular order),
- of an edge: vertex (in tail, head order), facet (in geometric order),
- of a facet: vertex, edge, body (all in order around the facet),
- of a body: facet (in no particular order).

- a single element, which can be

- an element name of an active generator.
- an indexed element type, vertex, edge, facet, or body. Indexing starts at 1. The index may be negative, in which case the generated element has negative orientation.
- an indexed subelement of an element (error if no element of that index). Indexing starts at 1. The indexing is the same as the order produced by the foreach generator. Indexed subelements of an edge or facet follow the orientation of the edge or facet.

name is an optional identifier which can be used in the body of a loop to refer to the generated element. expr is interpreted as a boolean expression, zero for false, nonzero for true. Only elements for which expr is true are generated. The where expr clause is optional. The innermost generator generates a default element, which can have its attributes referred to just by attribute name. But be sure to remember that in a nested iteration, an unqualified element type generates all elements of that type, not just those associated with the parent element. Examples:

## General commands
Many commands in the Evolver command language have a sentence-like structure and start with a verb.

- ABORT
- ADDLOAD
- AREAWEED
- BINARY_PRINTF
- BODY_METIS
- BREAKPOINT
- CHDIR
- CLOSE_SHOW
- DEFINE
- DELETE
- DELETE_TEXT
- DETORUS
- DIRICHLET
- DIRICHLET_SEEK
- DISPLAY_TEXT
- DISSOLVE
- DUMP
- DUMP_MEMLIST
- EDGE_MERGE
- EDGESWAP
- EDGEWEED
- EIGENPROBE
- EQUIANGULATE
- ERRPRINTF
- EXEC
- EXPRINT
- FACET_CROSSCUT
- FACET_MERGE
- FIX
- FLUSH_COUNTS
- FREE_DISCARDS
- GEOMPIPE
- GEOMVIEW
- HELP
- HESSIAN

- HESSIAN_MENU
- HESSIAN_SEEK
- HISTOGRAM
- HISTORY
- KMETIS
- LAGRANGE
- LANCZOS
- LINEAR
- LIST
- LIST ATTRIBUTES
- LIST BOTTOMINFO
- LIST PROCEDURES
- LIST TOPINFO
- LOAD
- LONGJ
- MATRIX_INVERSE
- MATRIX_MULTIPLY
- METIS
- MOVE
- NEW_VERTEX
- NEW_EDGE
- NEW_FACET
- NEW_BODY
- NOTCH
- OMETIS
- OOGLFILE
- OPTIMIZE
- PAUSE
- PERMLOAD
- POP
- POP_EDGE_TO_TRI
- POP_QUAD_TO_QUAD
- POP_TRI_TO_EDGE
- POSTSCRIPT
- PRINT

- PRINTF
- QUADRATIC
- QUIT
- RAWESTV
- RAWEST_VERTEX_AVERAGE
- RAWV
- RAW_VERTEX_AVERAGE
- READ
- REBODY
- RECALC
- REFINE
- REPLACE_LOAD
- RESET_COUNTS
- REVERSE_ORIENTATION
- RITZ
- RENUMBER_ALL
- REORDER_STORAGE
- SADDLE
- SET
- SHELL
- SHOW
- SHOW_EXPR
- SHOWQ
- SIMPLEX_TO_FE
- SOBOLEV
- SPRINTF
- SUBCOMMAND
- SYSTEM
- T1_EDGESWAP
- UNFIX
- UNSET
- VERTEX_AVERAGE
- VERTEX_MERGE
- WHEREAMI
- WRAP_VERTEX
- ZOOM

## ABORT
Main prompt command. Causes immediate termination of the executing command and any enclosing commands and returns to the command prompt. Meant for stopping execution of a command when an error condition is found. There will be an error message output, giving the file and line number where the abort occurred, but it is still wise to have a script or procedure or function print an error message using errprintf before doing the abort command, so the user knows why.

## ADDLOAD
Main prompt command. Loads a new datafile without deleting the current surface, permitting the simultaneous loading of multiple copies of the same datafile or different datafiles. Syntax:

```text

   ADDLOAD filenamestring


```
where filenamestring is either a sting literal in double quotes, or a string variable name such as datafilename. Elements in the new datafile are re-numbered to not conflict with existing elements. This is actually the same as the default behavior of Evolver when loading a single datafile. Thus the -i command line option or the keep_originals keyword is not obeyed for the new datafile. The read section of the new datafile is not executed; this permits a datafile to use the addload command in its read section to load more copies of itself. The loading script is responsible for all initialization that would ordinarily be done in the read section of the new datafile. Declarations in the top section of the new datafile will overwrite any existing declarations. This is usually not a problem when loading multiple copies of the same datafile, but requires attention when loading different datafiles. For example, numbered constraints are a bad idea; use named constraints instead. For variables you don't want written, you can set the no_dump property of a variable to prevent it from being dumped in the top of the datafile; it will be dumped in the bottom section instead. Example (as commands, not in the top of the datafile): See the sample datafile addload_example.fe for an example of how to load and distinguish between multiple copies of the same surface.

## AREAWEED
Main prompt command. For deleting facets with less than a given area. Syntax:

```text
   AREAWEED expr

```
Same as the ' w ' command, except does not need interactive response. Also the same as " delete facets where area < expr ". Examples:

## BINARY_PRINTF
Main prompt command. For printing formatted binary output to files. Syntax:

```text

   BINARY_PRINTF string,expr,expr,...


```
Prints to standard output using a binary interpretation of the standard C formats:

- %c one byte
- %d two byte integer
- %ld four byte integer
- %f four byte float
- %lf eight byte float
- %s string, without the trailing null
- non-format characters are copied verbatim as single bytes.
The byte order for numbers can be set with the big_endian or little_endian toggles. NOTE: Either big_endian or little_endian must be set for binary_printf to work! The format string can be a string variable or a quoted string. There is a limit of 1000 characters on the format string, otherwise there is no limit on the number of arguments. Meant to be use with redirection to a file. In Microsoft Windows, the output file type is temporarily changed from TEXT to BINARY so newline bytes don't get converted. Example:

## BODY_METIS
Main prompt command. Partitions the set of bodies into n parts using the METIS library of Karypis and Kumar, if this library has been compiled into the Evolver. The partition number of each body is left in its extra attribute bpart (which will be created if it does not already exist). Body_metis works only in the soapfilm model; for the string model, partition facets using metis or kmetis. Body_metis uses the PMETIS algorithm. Meant for experiments in partitioning the surface for multiprocessors. Syntax:

```text
   BODY_METIS n


```

## BREAKPOINT
Main prompt command. The user may set a breakpoint in an already loaded script or function or procedure at a given line number. The syntax is

```text

  BREAKPOINT scriptname linenumber


```
where scriptname is the name of the function or procedure and linenumber is the line number in the file where the breakpoint is to be set. There must be executable code on the line, or you will get an error. linenumber may be an expression.
Breakpoints may be unset individually with

```text

  UNSET BREAKPOINT scriptname linenumber


```
or as a group with

```text

  UNSET BREAKPOINTS


```
When a breakpoint is reached, Evolver will enter into a subcommand prompt, at which the user may enter any Evolver commands (although some commands, such as load would be very unwise). To exit from the subcommand prompt and resume execution, use q or exit or quit.

## CHDIR
Main prompt command. Changes the current directory, which is used for searching for files before EVOLVERPATH is used. Syntax:

```text
   CHDIR stringexpr

```
In MS-Windows, use a front slash '/' or a double backslash '\\' instead of a single backslash as the path character. Example:

## CLOSE_SHOW
Main prompt command. Closes the native graphics window started by the ` s ' or show commands. Does not affect geomview version. Synonym: show_off.

## CONVERT_TO_QUANTITIES
Main prompt command. This will do an automatic conversion of old-style energies to new-style named quantities. This has the same effect as the -q command line option, but can be done from the Evolver command prompt. Useful when hessian complains about not being able to do a type of energy. A few energies don't convert yet. It is my intention that this will be the default sometime in the near future, if it can be made sufficiently fast and reliable. If everything has been converted to quantities one way or another, the internal variable everything_quantities} is set to 1. Convert_to_quantities} cannot be undone. Useful when hessian complains about not being able to do a type of energy. It is also useful when setting up a datafile, since the `Q' command will show all the internal quantities individually (when the show_all_quantities toggle is on), so you can tell what each constraint integral is and so forth.

## DEFINE
Main prompt command. For runtime defining of variables, arrays, level set constraints, boundaries, named quantities, named method instances, and extra attributes of elements. The syntax for defining single variables is

```text
    DEFINE variable type

```
where type is real, integer, or string. Note that this way of declaring a variable does not take an initial value; thus it is a way of making sure a variable is defined without overwriting an existing value of the variable. The syntax for defining arrays and extra attributes is the same as in the top of the datafile; for constraints, boundaries, named quantities, and method instances, it is the same as in the top of the datafile except the word "define" comes first. Multi-line definitions should be enclosed in brackets and terminated with a semicolon. Or they can be enclosed in quotes and fed to the exec command. Of course, using exec means the parser doesn't know about the define until the exec is executed, so you cannot use the defined item in commands until then. It is legal to re-define an existing array or array extra attribute with different dimensions (but the same number of dimensions); data will be preserved as best as possible in the resized array. An array may be given the dimension 0 to free its memory allocation. Examples:

## DELETE
Main prompt command. For collapsing edges or facets. Syntax:

```text

   DELETE  generator


```
Deletes edges by shrinking the edge to zero length (as in the t or edgeweed commands) and facets by eliminating one edge of the facet (as in the t or edgeweed commands). Facet edges will be tried for elimination in shortest to longest order. Edges will not be deleted if both endpoints are fixed, or both endpoints have different constraints or boundaries from the edge. Delete maintains the continuity and connectedness of the surface, as opposed to dissolve. Example:

## DELETE_TEXT
Command to delete a text string from the graphics display. Syntax: where text_id is the value returned by the call to display_text that created the string.

## DETORUS
Main prompt command. Converts the displayed surface to a real surface. It is meant for situations like the torus model where one wants to unwrap the torus in reality in order to write an export file for some other program. After detorus, the torus model is not in effect. Detorus also works with view transforms. Beware that after detorus vertices and edges may be removed from boundaries and constraints, so considerable patching up may be necessary to get an evolvable surface. But quantities, colors, and other attributes are inherited, and they may need patching up also.
Simply replicating everything usually leads to duplicate vertices where there should only be one. There is a toggle detorus_sticky that makes detorus merge vertices, edges, and facets that coincide; it defaults to on. When detorus_sticky is on, any vertices within distance detorus_epsilon are identified. The default value of detorus_epsilon is 1e-6.

## DIRICHLET
Main prompt command. Does one iteration of minimizing the Dirichlet integral of the surface. The current surface is the domain, and the Dirichlet integral is of the map from the current surface to the next. This is according to a scheme of Konrad Polthier and Ulrich Pinkall [PP]. At minimum Dirichlet integral, the area is minimized also. Works only on area with fixed boundary; no volume constraints or anything else. Seems to converge very slowly near minimum, so not a substitute for other iteration methods. But if you have just a simple soap film far, far from the minimum, then this method can make a big first step. dirichlet_seek will do an energy-minimizing search in the direction.

## DIRICHLET_SEEK
Main prompt command. Calculates a motion as in the dirichlet command, but uses this as a direction of motion instead of as the motion itself. Dirichlet_seek then uses a line-search along this direction to find a minimum of energy.

## DISPLAY_TEXT
Main prompt command. Causes the display of simple text on the graphics display. Currently implemented for OpenGL and PostScript graphics. Syntax:

```text

  text_id := DISPLAY_TEXT(x,y,height,string)


```
The x,y coordinates of the start of the string are in window units, i.e. the window coordinates run from (0,0) in the lower left to (1,1) in the upper right. "Height" is the font height in window units, so 0.04 is a reasonable value. The return value should be saved in a variable in case you want to delete_text it later; even if you don't want to delete it, you must have something on the left of the assignment for syntax purposes. No font type or color implemented. Meant for captioning images, for example a timer in frames of a movie.

## DISSOLVE
Main prompt command. Removes elements from the surface without closing the gap left. Syntax: The effect is the same as if the line for the element were erased from a datafile. Hence no element will be dissolved that is used by a higher dimensional element. (There are three exceptions: dissolving an edge on a facet in the string model, and dissolving a facet on one body or with both adjacent bodies the same in the soapfilm model.) Thus " dissolve edges; dissolve vertices " is safe because only unused edges and vertices will be dissolved. No error messages are generated by doing this. Good for poking holes in a surface. Example:

## DUMP
Main prompt command. Dumps current surface to named file in datafile format. Syntax:

```text

  DUMP filename


```
The filename is a string. With no filename, dumps to the default dump file, which is the current datafile name with a ".dmp" extension. Same as the ' d ' command, except ' d ' requires a response from the user for the filename. Examples: See no_dump for suppressing dumping of particular variables.

## DUMP_MEMLIST
Main prompt command. Lists the currently allocated memory blocks. For my own use in debugging memory problems.

## EDGE_MERGE
Main prompt command. Merges two edges into one in a side-by-side fashion. Meant for joining together surfaces that bump into each other. Should not be used on edges already connected by a facet, but merging edges that already have a common endpoint(s) is fine. Syntax:

```text

  EDGE_MERGE(integer,integer)


```
Note the arguments are signed integer ids for the elements, not element generators. The tails of the edges are merged, and so are the heads. Orientation is important. Example:

## EDGESWAP
Main prompt command. For switching around the endpoints of edges, that is, forcing an equiangulation type move. Syntax:

```text

 EDGESWAP edgegenerator


```
If any of the qualifying edges are diagonals of quadrilaterals, they are flipped in the same way as in equiangulation, regardless of whether equiangularity is improved. " edgeswap edge " will try to swap all edges, and is not recommended, unless you like weird things. Various conditions will prevent an edge from being swapped:

- The edge is fixed.
- There are not exactly two facets adjacent to the edge.
- The adjacent facets do not have equal tension.
- The adjacent facets are not on the same level set constraints as the edge.
- The adjacent facets are not on the same parametric boundary as the edge.
- Swapping would create an edge with both endpoints the same (a loop).
- Swapping would create two edges with the same endpoints (an "ear").
All but the first two reasons print messages. This is a compromise between informing the user why edges were not switched and preventing a cascade of messages. When edge swapping is invoked through the ' u ' command, none of these messages are printed. Examples:

## EDGEWEED
Main prompt command. Deletes edges shorter than given value. Syntax: Same as the ' t ' command, except it does not need an interactive response. Same as " delete edge where length < expr ".

## EIGENPROBE
Main prompt command. For finding the number of eigenvalues of the energy Hessian that are less than, equal to, and greater than a given value. Syntax:

```text

   EIGENPROBE expr
   EIGENPROBE(expr,expr)


```
The first form prints the number of eigenvalues of the energy Hessian that are less than, equal to, and greater than expr. It is OK to use an exact eigenvalue (like 0, often) for the value, but not really recommended. Useful for probing stability. Second form will further do inverse power iteration to find an eigenvector. The second argument is the limit on the number of iterations. The eigenvalue will be stored in the last_eigenvalue internal variable, and the eigenvector can be used by the move command. The direction of the eigenvector is chosen to be downhill in energy, if the energy gradient is nonzero.

## EPRINT
Main prompt function. Same as print, except it acts as a function and evaluates to the value of the printed expression. Syntax:

```text

   EPRINT expr


```

## EQUIANGULATE
Main prompt command. This command tests the given edges to see if flipping them would improve equiangularity. It is the u command applied to a specified set of edges. It differs from the edgeswap command in that only edges that pass the test are flipped. Syntax:

```text

  EQUIANGULATE edge_generator


```

## ERRPRINTF
Main prompt command. Same as printf, except it sends its output to stderr instead of stdout. Useful in reporting error messages in scripts that have their output redirected to a file.

## EXEC
Main prompt command. Executes a command in string form. Good for runtime generation of commands. Syntax:

```text

   EXEC stringexpr


```

## EXPRINT
Main prompt command. Prints the original input string defining a user-defined command, including comments. Syntax:

```text

   EXPRINT commandname


```

## FACET_CROSSCUT
Function. In the string model, it subdivides a facet by constructing a diagonal edge between given vertices. The return value is the id number of the new edge. The new facet will be on the same body as the old facet. Syntax:

```text

   newedge := FACET_CROSSCUT(facet_id,tail_id,head_id)


```

## FACET_MERGE
Main prompt command. Merges two soapfilm model facets into one in a face-to-face fashion. Meant for joining together surfaces that bump into each other. The pairs of vertices to be merged are selected in a way to minimize the distance between merged pairs subject to the orientations given, so there are three choices the algorithm has to choose from. It is legal to merge facets that already have some endpoints or edges merged. Syntax:

```text

  FACET_MERGE(integer,integer)


```
Note the syntax is a procedure taking signed integer facet id arguments, not element generators. IMPORTANT: The frontbody of the first facet should be equal to the backbody of the second (this includes having no body); this is the body that will be squeezed out when the facets are merged. If this is not true, then facet_merge will try flipping the facets' orientations until it finds a legal match. Example:

## FIX
Main prompt command. For setting the fixed attribute of elements. Syntax:

```text

   FIX generator


```
Example: Can also convert a parameter from optimizing to non-optimizing. Example: Can also convert a named quantity from info_only to fixed.
See also unfix.

## FLUSH_COUNTS
Main prompt command. Causes the printing of various internal counters that have become nonzero. Syntax:

```text

   FLUSH_COUNTS


```
The counters are: fix_count, unfix_count, where_count, equi_count, edge_delete_count, facet_delete_count, edge_refine_count, facet_refine_count, notch_count, vertex_dissolve_count, edge_dissolve_count, facet_dissolve_count, body_dissolve_count, vertex_pop_count, edge_pop_count, pop_tri_to_edge_count, pop_edge_to_tri_count, pop_quad_to_quad_count, edgeswap_count and, t1_edgeswap_count. Normally, these counts are accumulated during the execution of a command and printed at the end of the command. Flush_counts can be used to display them at some point within a command. Flush_counts is usually followed by reset_counts, which resets all these counters to 0.

## FREE_DISCARDS
Main prompt command. Syntax:

```text

   FREE_DISCARDS


```
Frees deleted elements in internal storage. Ordinarily, deleting elements does not free their memory for re-use until the command completes, so that element iteration loops do not get disrupted. If for some reason this behavior leads to excess memory usage or some other problem, the user may use the free_discards command to free element storage of deleted elements. Just be sure not to do this inside any element iteration loop that might be affected.

## GEOMPIPE
Main prompt command. Redirects Evolver's geomview output to a command in place of sending it to geomview. Syntax:

```text

   GEOMPIPE stringexpr


```
The redirection can be closed with the command " P 9 ". Geompipe is useful for debugging geomview data; but be sure to toggle gv_binary OFF to get ascii data to look at.

## GEOMVIEW
Main prompt command. The plain form " geomview " toggles the geomview display on and off. The syntax

```text
   GEOMVIEW stringexpr


```
will send a command to an already started geomview. This string must be in the geomview command language, for which consult the geomview documentation.

## HELP
Main prompt command. Main prompt command. Prints what Evolver knows about an identifier or keyword. User-defined variables, named quantities, named methods, named constraints, and element attributes are identified as such. Information for syntax keywords comes from a file evhelp.txt in the doc subdirectory of your Evolver installation, so that subdirectory should be on your EVOLVERPATH environment variable. Syntax:

```text

   HELP keyword


```
The keyword need not be in quotes, unless there are embedded blanks. After printing the help section exactly matching the keyword, a list of related terms is printed. These are just the keywords containing your keyword as a substring.

## HESSIAN
Main prompt command. Does one step using Newton's method with the Hessian matrix of the energy. If the Hessian is not positive definite, a warning will be printed, but the move will be made anyway. If the check_increase toggle is on, then no move will be made if it would increase energy. Hessian_seek will use a variable step size to seek minimum energy in the direction of motion. The motion vector is stored, and may be accessed with the move command. Not all energies and constraints have Hessian calculations yet. See the Hessian tutorial for more.

## HESSIAN_MENU
Main prompt command. Brings up a menu of commands involving the energy Hessian matrix. Not all of it works well, and may disappear in future versions. A one-line prompt with options appears. Use option ' ? ' to get a fuller description of the choices. For those options that calculate an eigenvalue, the eigenvalue (or first, if several) is saved in the internal variable last_eigenvalue. A quick summary of the current options:

1. Fill in hessian matrix.

Allocation and calculation of Hessian matrix.

2. Fill in right side. (Do 1 first)

Calculates gradient and constraint values.

3. Solve. (Do 2 first)

Solves system for a motion direction.

4. Move. (Do 3, A, B, C, E, K, or L first)

Having a motion direction, this will move some stepsize in that direction. Will prompt for stepsize. The direction of motion is saved and is available in the move command.

7. Restore original coordinates.

Will undo any moves. So you can move without fear.

9. Toggle debugging. (Don't do this!)

Prints Hessian matrix and right side as they are calculated in other options. Produces copious output, and is meant for development only. Do NOT try this option.

B. Chebyshev (For Hessian solution ).

Chebyshev iteration to solve system. This option takes care of its own initialization, so you don't have to do steps 1 and 2 first. Not too useful.

C. Chebyshev (For most negative eigenvalue eigenvector).

Chebyshev iteration to find most negative eigenvalue and eigenvector. Will ask for number of iterations, and will prompt for further iterations. End by just saying 0 iterations. Prints Rayleigh quotient every 50 iterations. After finding an eigenpair, gives you the chance to find next lowest. Last eigenvector found becomes motion for step 4. Self initializing. Not too useful.

E. Lowest eigenvalue. (By factoring. Do 1 first)

Uses factoring to probe the inertia of the shifted Hessian H-cI until it has the lowest eigenvalue located within .01. Then uses inverse iteration to find eigenpair.

F. Lowest eigenvalue. (By conjugate gradient. Do 1 first)

Uses conjugate gradient to minimize the Rayleigh quotient.

L. Lanczos. (Finds eigenvalues near probe value. )

Uses Lanczos method to solve for 15 eigenvalues near the probe value left over from menu choices 'P' or 'V'. These are approximate eigenvalues, but the first one is usually very accurate. Do not trust apparent multiplicities. From the main command prompt, you can use the lanczos command.

R. Lanczos with selective reorthogonalization.

Same as 'L', but a little more elaborate to cut down on spurious multiplicities by saving some vectors to reorthogonalize the Lanczos vectors. Not quite the same as the official "selective reorthogonalization" found in textbooks.

Z. Ritz subspace iteration for eigenvalues. (Do 1 first)

Calculate a number of eigenpairs near a probe value. Will prompt for probe value and number of eigenpairs. Same as ritz main command. Can be interrupted gracefully by keyboard interrupt. Afterwards, one can use the X option to pick a particular eigenvector to look at.

X. Pick Ritz vector for motion. (Do Z first)

Selects an eigenvector calculated by the Z option for use in motion (option 4). First eigenvalue listed is number 1, etc. Particularly useful for discriminating among high multiplicity eigenvalues, which the V option does not let you do. You can enter the eigenvector by its number in the list from the Z option. As a special bonus useful when there are multiple eigenvectors for an eigenvalue, you can enter the vector as a linear combination of eigenvectors, e.g. ``0.4 v1 + 1.3 v2 - 2.13 v3''.

P. Eigenvalue probe. (By factoring. Do 1 first)

Reports the inertia of the shifted Hessian H-cI for user-supplied values of the shift c. The Hessian H includes the effects of constraints. Will prompt repeatedly for c. Null response exits. From the main command prompt, you can use the eigenprobe command.

V. Eigenvalue probe with eigenvector. (By factoring. Do 1 first)

Reports the inertia of the shifted Hessian H-cI for user-supplied values of the shift c, and calculates the eigenvector for the eigenvalue nearest c by inverse power iteration. You will be prompted for c and for the maximum number of iterations to do. From the main command prompt, you can use the eigenprobe command.

S. Seek along direction. (Do 3, A, B, E, C, K, or L first)

Can do this instead of option 4 if you want Evolver to seek to lowest energy in an already found direction of motion. Uses the same line search algorithm as the optimizing ` g ' command.

Y. Toggle YSMP/alternate minimal degree factoring.

Default Hessian factoring is by Yale Sparse Matrix Package. The alternate is a minimal degree factoring routine of my own devising that is a little more aware of the surface structure, and maybe more efficient. If YSMP gives problems, like running out of storage, try the alternate. This option is available at the main prompt as the ysmp toggle.

U. Toggle Bunch-Kaufman version of min deg.

YSMP is designed for positive definite matrices, since it doesn't do any pivoting or anything. The alternate minimal degree factoring method, though, has the option of handling negative diagonal elements in a special way. This option is available at the main prompt as the bunch_kaufman toggle.

M. Toggle projecting to global constraints in move.

Toggles projecting to global constraints, such as volume constraints. Default is ON. Don't mess with this. Actually, I don't remember why I put it in.

G. Toggle minimizing square gradient in seek.

For converging to unstable critical points. When this is on, option ' S ' will minimize the square of the energy gradient rather than minimizing the energy. Also the regular saddle and hessian_seek commands will minimize square gradient instead of energy.

=. Subshell.

Starts a command prompt while still in hessian_menu. You can do pretty much any command, but you should not do anything that changes the surface, thus invalidating the Hessian data. This is meant, for example, for creating a graphics file of an eigenvalue perturbation and then returning to the hessian_menu prompt. You exit the subshell with the " q " command.

0. Exit hessian.

Exits the menu. ` q ' also works.

For example, to inspect what eigenvectors look like, one would do steps 1 and z, then repeatedly use x to pick an eigenvector, 4 to move, and 7 to restore.

## HESSIAN_SEEK
Main prompt command. Seeks to minimize energy along the direction found by Newton's method using the Hessian. Otherwise same as the hessian command. Syntax:

```text

  HESSIAN_SEEK maxscale


```
where maxscale is an optional upper bound for the distance to seek. The default maxscale is 1, which corresponds to a plain hessian step. The seek will look both ways along the direction, and will test down to 1e-6 of the maxscale before giving up and returning a scale of 0. This command is meant to be used when the surface is far enough away from equilibrium that the plain i hessian command is unreliable, as hessian_seek guarantees an energy decrease, if it moves at all.

## HISTOGRAM, LOGHISTOGRAM
Main prompt command. For printing histograms in text form to standard output. Syntax:

```text

   HISTOGRAM(generator, expr)
   LOGHISTOGRAM(generator, expr)


```
Prints a histogram of the values of expr for the generated elements. It uses 20 bins evenly divided between minimum and maximum values. It finds its own maximum and minimum values, so the user does not have to specify binsize. The log version will lump all zero and negative values into one bin. Examples:

## HISTORY
Main prompt command. Print the saved history list of commands. Syntax:

```text

   HISTORY


```

## LAGRANGE
Main prompt command. Changes to Lagrange model from quadratic or linear models. Syntax:

```text

   LAGRANGE n


```
where n is the lagrange_order, which is between 1 and some built-in maximum (currently 8). This command can also convert between Lagrange models of different orders. Note that lagrange 1 gives the Lagrange model of order 1, which has a different internal representation than the linear model. Likewise, lagrange 2 does not give the quadratic model.

## LANCZOS
Main prompt command. For finding eigenvalues of the energy Hessian near a given value. Syntax:

```text

   LANCZOS expr

   LANCZOS (expr,expr)


```
Does a little Lanczos algorithm and reports the nearest approximate eigenvalues to the given probe value. In the first form, expr is the probe value, and 15 eigenvalues are found. In the second form, the first argument is the probe value, the second is the number of eigenvalues desired. The output begins with the number of eigenvalues less than, equal to, and greater than the probe value. Then come the eigenvalues in distance order from the probe. Not real polished yet. Beware that multiplicities reported can be inaccurate. The eigenvalue nearest the probe value is usually very accurate, but others can be misleading due to incomplete convergence. Since the algorithm starts with a random vector, running it twice can give an idea of its accuracy.

## LINEAR
Main prompt command. Changes to linear model from quadratic or Lagrange models. Syntax:

```text

    LINEAR


```

## LIST
Main prompt command. List elements on the screen in the same format as in the datafile, or lists individual constraint, boundary, quantity, or method instance definitions. Syntax:

```text

   LIST  generator
   LIST constraintname
   LIST CONSTRAINT constraintnumber
   LIST boundaryname
   LIST BOUNDARY boundarynumber
   LIST quantityname
   LIST instancename


```
On unix and Windows systems, piping to more can be used for long displays. Examples: See also list attributes, list bottominfo, list procedures, and list topinfo.

## LIST ATTRIBUTES
Prints a list of the extra attributes of each type of element. Syntax:

```text

   LIST ATTRIBUTES


```
Besides user-defined extra attributes, this list also contains internal attributes that make use of the extra attribute mechanism (being of variable size), such as coordinates, parameters, forces, and velocities. It does not list permanent, fixed-size attributes such as color or fixedness, or possible attributes that are not used at all.

## LIST BOTTOMINFO
Main prompt command. Prints what would be dumped in the " read " section at the end of a dumpfile: command definitions and various toggle states. Syntax:

```text

   LIST BOTTOMINFO


```

## LIST PROCEDURES
Main prompt command. Prints names of all current user-defined commands, functions, and procedures. Syntax:

```text

   LIST PROCEDURES


```

## LIST TOPINFO
Main prompt command. Prints the first section of the datafile on the screen. This is everything before the vertices section. Syntax:

```text

   LIST TOPINFO


```

## LOAD
Main prompt command. For loading a new surface. Terminates the current surface and loads a new datafile. Syntax:

```text

   LOAD filenamestring


```
The filenamestring is the datafile name, and can be either a quoted string or a string variable. This completely re-initializes everything, including the command interpreter. In particular, the currently executing command ends. Wildcard matching is in effect on some systems (Windows, linux, maybe others), but be very careful when using wildcards since there can be unexpected matches. Useful only as the last command in a script. For loading a new surface and continuing with the current command, see replace_load. For loading a new surface on top of the current surface, see addload.

## LOGFILE
Main prompt command. Syntax:

```text

   LOGFILE filenamestring
   LOGFILE OFF


```
Starts recording all input and output to the file specified by filenamestring, which must be a quoted string or a string variable or expression. Appends to an existing file. To end logging, use logfile off. To record just input keystrokes, use keylogfile.

## KEYLOGFILE
Main prompt command. Syntax:

```text

   KEYLOGFILE filenamestring
   KEYLOGFILE OFF


```
Starts recording all input keystrokes to the file specified by filenamestring, which must be a quoted string or a string variable or expression. Appends to an existing file. To end logging, use keylogfile off. To record both input and output, use logfile.

## METIS, KMETIS
Main prompt command. Partitions the set of facets (or edges in the string model) into n parts using the METIS library of Karypis and Kumar, if this library has been compiled into the Evolver (it is in the Windows version). Meant for experiments in partitioning the surface for multiprocessors. Syntax:

```text

  METIS n
  KMETIS n


```
The partition number of facet is left in the facet extra attribute fpart (edge epart for string model), which will be created if it does not already exist. METIS uses the PMETIS algorithm, KMETIS uses the KMETIS algorithm. Example: For partitioning bodies, see body_metis.

## LONGJ
Main prompt command. For perturbing the surface. This does a "long jiggle", which provides long wavelength perturbations that can test a surface for stability. The parameters are a wavevector, a phase, and a vector amplitude. The user will be prompted for values. Numbers for vectors should be entered separated by blanks, not commas. An empty reply will accept the defaults. A reply of r will generate random values. Any other will exit the command without doing a jiggle. In the random cases, a random amplitude $\vec A$ and a random wavelength $\vec L$ are chosen from a sphere whose radius is the size of the object. The wavelength is inverted to a wavevector $\vec w$. A random phase $\psi$ is picked. Then each vertex $\vec v$ is moved by $\vec A\sin(\vec v \cdot \vec w + \psi)$. This command is archaic. More control over perturbations may be had with the " set vertex x ... " type of command.

## MATRIX_INVERSE
Main prompt function. For computing the inverse of a square matrix. Currently applies only to global matrices, not element attribute matrices. Return value is 1 if inversion is successful, 0 if the matrix is singular. Syntax:

```text

   retval := MATRIX_INVERSE(matrix1, matrix2)


```
Here matrix1 is the name of the original matrix, and matrix2 is the name of the inverse matrix. They may be the same matrix to get an in-place inverse. Examples:

## MATRIX_MULTIPLY
Main prompt command. For computing the product of matrices. Currently applies only to stand-alone matrices, not element attribute matrices. Syntax:

```text

  MATRIX_MULTIPLY(matrix1, matrix2, matrix3)


```
Here matrix1 and matrix2 are the names of the multiplicands, and matrix3 is the name of the product matrix. The product matrix may be the same as one (or both) of the multiplicands. The matrices can be one-dimensional or two-dimensional, so you can do vector-matrix or matrix-vector multiplication (but you can't do vector times vector). Examples: This command has been superseded by the ordinary multiplication operator * now applying to matrices, both stand-alone and attribute.

## MOVE
Main prompt command. For moving along the current direction of motion. Syntax:

```text

  MOVE expr


```
Moves the surface along the previous direction of motion by the stepsize given by expr. The previous direction can be either from a gradient step ( g command) or a hessian step ( hessian, saddle, hessian_seek, hessian_menu option 4, etc.). The stepsize does not affect the current scale factor. A negative step is not a perfect undo, since it cannot undo projections to constraints. Move sometimes does not work well with optimizing parameters and hessian together.

## NEW_VERTEX
Main prompt command. For creating a new vertex. The syntax is that of a function instead of a verb, since it returns the id number of the new vertex. The arguments are the coordinates of the vertex. The new vertex is not connected to anything else; use the new_edge command to connect it. Syntax:

```text

  newid := NEW_VERTEX(expr, expr,...)


```

## NEW_EDGE
Main prompt command. For creating a new edge. The syntax is that of a function instead of a verb, since it returns the id number of the new edge. The arguments are the id's of the tail and head vertices. Syntax:

```text

  newid := NEW_EDGE(expr, expr)


```
The new edge has the same default properties as if it had been created in the datafile with no attributes, so you will need to explicitly add any attributes you want. Example to create a set of coordinate axes in 3D:

## NEW_FACET
Main prompt command. For creating a new facet. The syntax is that of a function instead of a verb, since it returns the id number of the new facet. The arguments are the oriented id's of the edges around the boundary of the facet, in the same manner that a face is defined in the datafile. The number of edges is arbitrary, and they need not form a closed loop in the string model. In the soapfilm model, if more than three edges are given, the new face will be triangulated by insertion of a central vertex. In that case, the returned value will be the original attribute of the new facets. In the simplex model, the arguments are the id's of the facet vertices. Syntax:

```text

  newid := NEW_FACET(expr, expr,...)


```
The new facet has the same default properties as if it had been created in the datafile with no attributes, so you will need to explicitly add any attributes you want. Example:

## NEW_BODY
Main prompt command. For creating a new body. The syntax is that of a function instead of a verb, since it returns the id number of the new body. There are no arguments. Syntax:

```text

  newid := NEW_BODY


```
The body is created with no facets. Use the set facet frontbody and set facet backbody commands to install the body's facets. The new body has the same default properties as if it had been created in the datafile with no attributes, so you will need to explicitly add any attributes you want, such as density or target volume. Example:

## NOTCH
Main prompt command. For refining a surface in regions of high curvature. Syntax:

```text

 NOTCH expr


```
Notches all edges with dihedral angle greater than given value. Same as ' n ' command, or

```text
   foreach edge ee where ee.dihedral > expr do refine ee.facet


```
Notching is done by adding a vertex in the middle of adjacent facets. Should be followed by equiangulation.

## OMETIS
Obsolete main prompt command. Computes an ordering for Hessian factoring using the METIS library of Karypis and Kumar, if this library has been compiled into the Evolver (it is in the Windows version). Prints ordering tree. To actually use METIS ordering during factoring, use the toggle metis_factor. Note: ometis no longer works for Metis version 3 or later, since Metis does not return the tree any more. But metis_factor still works. Syntax:

```text

  OMETIS n  // n is smallest partition size
  OMETIS           // defaults to n = 100


```

## OOGLFILE
Main prompt command. Writes a file containing OOGL-formatted graphics data for the surface as a POLY or CPOLY quad file. This is a non-interactive version of the P 2 command. Syntax:

```text

   OOGLFILE stringexpr


```
The string gets ".quad" appended to form the filename. This command does not ask any of the other questions the P 2 command asks; it uses the default values, or whatever the last responses were to the previous use of the interactive P 2 command. Good for use in scripts. Example:

## OPTIMIZE
Main prompt command. Set gradient descent iteration to optimizing mode, with an upper bound on the scale factor. Optimise is a synonym. Syntax:

```text
  OPTIMIZE expr


```

## PAUSE
Main prompt command. Pauses execution until the user hits Enter. Useful in scripts to give the user a chance to look at some output before proceeding. Syntax:

```text

   PAUSE


```

## PERMLOAD
Main prompt command. Loads a new datafile and continues with the current command after the read section of the datafile finishes. The filename is the datafile name, and can be either a quoted string or a string variable. Since the automatic re-initialization makes Evolver forget all non-permanent variables, care should be taken that the current command only uses permanently assigned variables (assigned with::=). Useful for writing scripts that run a sequence of evolutions based on varying parameter values. Using permload is a little tricky, since you don't want to be redefining your permanent commands and variables every time you reload the datafile, and your permanent command cannot refer directly to variables parameterizing the surface. One way to do it is to read in commands from separate files. For example, the catenoid of cat.fe has height controlled by the variable zmax. You could have a file permcat.cmd containing the overall series script command and a file permcat.gogo containing the evolution commands

```text

  u; zmax := height; recalc; r; g 10; r; g 10; hessian;
  printf "height: %f  area: %18.15f\n",height,total_area >> "permcat.out";


```
Then at the Evolver command prompt,

```text

  Enter command: read "permcat.cmd"
  Enter command: run_series


```
For loading a new surface and not continuing with the current command, see load. Wildcard matching is in effect on some systems (Windows, linux, maybe others), but be very careful when using wildcards since there can be unexpected matches.
NOTE: permload does not work well; I suggest using replace_load instead.

## POP
Main prompt command. Pops an individual edge or vertex or set of edges or vertices, giving finer control than the universal popping of the O and o commands. Syntax:

```text

   POP generator


```
The specified vertices or edges are tested for not being minimal in the soap film sense. For vertices, this means having more than four triple edges adjacent; higher valence edges are automatically popped. For edges, this means having more than three adjacent facets when not on constraints or otherwise restricted. It tries to act properly on constrained edges also, but beware that my idea of proper behavior may be different from yours. Normally, popping puts in new edges and facets to keep originally separated regions separate, but that behavior can be changed with the pop_disjoin toggle. The style of popping a cone over a triangular prism can be controlled with the pop_to_edge and pop_to_face commands. The pop_enjoin toggle forces joining cones to be popped by widening the vertex into a neck. Examples: Under some circumstances, popping a vertex can leave two regions connected by a tunnel; if the septum_flag toggle is on, it will force a surface to be placed across the tunnel.
The number of pops done is recorded in the vertex_pop_count, edge_pop_count, and pop_count variables.
If you want more information reported on pops, including why potential pops did not happen, do verbose on before pop. (And don't forget to do verbose off afterwards, or you could get inundated later.)

## POP_EDGE_TO_TRI
Main prompt command. This command does a particular topological transformation common in three-dimensional foam evolution. Syntax:

```text

   POP_EDGE_TO_TRI generator


```
An edge with tetrahedral point endpoints is transformed to a single facet. A preliminary geometry check is made to be sure the edge satisfies the necessary conditions, one of which is that the triple edges radiating from the endpoints have no common farther endpoints. If run in verbose mode, messages are printed when a specified edge fails to be transformed. This command is the inverse of the pop_tri_to_edge command. Works in linear and quadratic models. Examples:

## POP_QUAD_TO_QUAD
Main prompt command. This command does a particular topological transformation common in three-dimensional foam evolution. Syntax:

```text

   POP_QUAD_TO_QUAD generator


```
A quadrilateral bounded by four triple edges is transformed to a quadrilateral oriented in the opposite direction. The shortest pair of opposite quadrilateral edges are shrunk to zero length, converting the quadrilateral to an edge, then the edge is expanded in the opposite direction to form the new quadrilateral. The new quadrilateral inherits attributes such as color from the first quadrilateral, although all the facet numbers are different. A preliminary geometry check is made to be sure the edge satisfies the necessary conditions, one of which is that the triple edges radiating from the quadrilateral corners have no common farther endpoints. If run in verbose mode, messages are printed when a specified quadriteral fails to be transformed. The specified facet can be any one of the facets of the quadrilateral with a triple line on its border. It doesn't hurt to apply the command to all the facets of the quadrilateral, or to facets of multilple quadrilaterals. Quadrilaterals may be arbitrarily subdivided into facets; in particular, they may have some purely interior facets. Works in linear and quadratic models. Examples:

## POP_TRI_TO_EDGE
Main prompt command. This command does a particular topological transformation common in three-dimensional foam evolution. Syntax:

```text

   POP_TRI_TO_EDGE generator


```
A facet with three tetrahedral point vertices is transformed to a single facet. A preliminary geometry check is made to be sure the edge satisfies the necessary conditions, one of which is that the triple edges radiating from the vertices have no common farther endpoints. If run in verbose mode, messages are printed when a specified edge fails to be transformed. This command is the inverse of the pop_edge_to_tri command. Works in linear and quadratic models. Examples:

## POSTSCRIPT
Main prompt command. Creates a PostScript file of the current surface in a file. Syntax:

```text
  POSTSCRIPT stringexpr

```
The string gives the name of the file; a.ps extension will be appended if it is missing. It is the same as the P option 3 command, except that there are no interactive responses needed. Output options are controlled by the ps_colorflag, ps_gridflag, ps_crossingflag, ps_labelflag, and full_bounding_box toggles. Example:

## PRINT
Main prompt command. For default-format printing of expression values, strings, commands, arrays, or accumulated warning messages. Syntax:

```text

   PRINT expr
   PRINT stringexpr
   PRINT commandname
   PRINT arrayslice
   PRINT WARNING_MESSAGES


```
The arrayslice option takes an array name or a partially indexed array name. If more than one element results, the slice is printed in nested curly braces. The arrayslice can also be that of an array attribute of an element. The warning_messages option is handy for reviewing warning messages that occur early in the loading of a datafile but scroll off the screen too rapidly to see. Examples:

## PRINTF
Main prompt command. For printing formatted output. Syntax:

```text

   PRINTF string,expr,expr,...


```
Prints to standard output using the standard C sprintf function. All string, integer, and floating point formats are valid. Integer formats force numeric arguments to be converted to integer. The format string can be a string variable or a quoted string. There is a limit of 1000 characters on the format string, otherwise there is no limit on the number of arguments. Example:

## QUADRATIC
Main prompt command. Changes to quadratic model from linear or Lagrange models. Synonym of the M 2 command. Syntax:

```text

   QUADRATIC


```

## QUIT, BYE, EXIT
Main prompt command. Syntax:

```text
    quit
    quit expr


```
Alone, "quit" brings up a prompt to enter a new datafile. At this prompt, hitting the Enter key will return to the current surface, 'q' will exit Evolver, and anything else will be taken to be the name of a new datafile. When "quit" is followed by a value, Evolver exits immediately, and uses the value as the exit code, which is useful when running Evolver in a script or from some other program. Quitting Evolver automatically closes any graphics windows, and does not save anything. "quit", "bye", and "exit" are synonyms. Same as ` q ' command.

## RAWESTV
Main prompt command. Does vertex averaging for all vertices without regard for conserving volume or whether averaged vertices have like constraints. But doesn't move vertices on boundaries. Syntax:

```text

   RAWESTV


```
To do a selected group of vertices, use rawest_vertex_average.

## RAWEST_VERTEX_AVERAGE
Main prompt command. Does vertex averaging on selected vertices without conserving volume on each side of surface, or attention to being on like constraints. Doesn't move vertices on boundaries. Using the verbose toggle will print messages. Syntax:

```text

   RAWEST_VERTEX_AVERAGE generator


```

## RAWV
Main prompt command. Does vertex averaging for all vertices without conserving volume on each side of surface. Will only average vertices with those of like type of constraints. Doesn't move vertices on boundaries. Syntax:

```text

   RAWV


```
To do a selected group of vertices, use raw_vertex_average.

## RAW_VERTEX_AVERAGE
Main prompt command. Does vertex averaging on selected vertices without conserving volume on each side of surface. Will only average vertices with those of like type of constraints. Doesn't move vertices on boundaries. Using the verbose toggle will print messages. Syntax:

```text

   RAW_VERTEX_AVERAGE generator


```

## READ
Main prompt command. For reading commands from a file. Syntax: The filename can be either a quoted string or a string variable. The effect is as if the file were typed in at the keyboard. Hence main commands, responses to commands, and graphics mode commands can be included. Read commands may be nested, i.e. a file being read in can have read commands in it. On the occurence of an error, input reverts to the original standard input. Example:

## REBODY
Main prompt command. Recalculates connected bodies. Syntax: Useful after a body has been disconnected by a neck pinching off. Facets of an old body are divided into edge-connected sets, and each set defines a new body (one of which gets the old body id). The new bodies inherit the attributes of the old body. If the original body volume was fixed, then the new bodies' target volumes become the new actual volumes. If the original body had a volconst, the new bodies will inherit the same value. This will likely lead to incorrect values, so you will have to adjust the volconsts by hand. In commands, you may specify the new bodies descended from an original body by using the original atttribute.

## RECALC
Main prompt command. Recalculates and redisplays everything. Syntax:

```text

   RECALC


```
Useful after changing some variable or something and recalculation is not automatically done. Evolver tries to automatically recalculate when some significant change is made, but doesn't always know. Also see autorecalc.

## REFINE
Main prompt command. For subdividing sets of edges or facets. Syntax:

```text

   REFINE generator


```
Subdivides the generated edges or facets. Subdivides edges by putting a vertex in the middle of each edge, and splitting neighboring facets in two in the soapfilm model. It is the same action as the long edge subdivide command (command l). Facets will be subdivided by putting a vertex in the center and creating edges out to the old vertices. It is strongly suggested that you follow this with equiangulation to groom the triangulation. Edge refinement is better than facet refinement as facet refinement can leave long edges even after equiangulation. This command does not respect the no_refine attribute. Example:

## REPLACE_LOAD
Main prompt command. Replaces the current surface with a new surface from a datafile without a total re-initialization. Syntax:

```text
 replace_load  filename


```
where filename is a double-quoted string or a string variable. The replace_load command actually dissolves all the elements of the current surface and then does the addload command to read in the desired datafile. Thus only the top section and the elements of the new file are read in; the "read" section of the new datafile is not read. All variables, constraints, quantities, and commands from the original file are remembered, although they may be re-initialized in the top of the new datafile. This command can be used in loops to repeatedly evolve a surface under different conditions, for example It is necessary that htvar NOT appear in the top of the datafile, so that it does not get re-initialized when replace_load is done. You can set the no_dump property of a variable to prevent it from being dumped in the top of the datafile; it will be dumped in the bottom section instead. Example (as commands, not in the top of the datafile): Replace_load is meant as a replacement for permload, which I never have been able to get to work right.

## RESET_COUNTS
Main prompt command. Resets to 0 various internal counters. The counters are:

- fix_count,
- unfix_count,
- where_count,
- equi_count,
- edge_delete_count,
- facet_delete_count,
- edge_refine_count,
- facet_refine_count,
- notch_count,
- vertex_dissolve_count,
- edge_dissolve_count,
- facet_dissolve_count,
- body_dissolve_count,
- vertex_pop_count,
- edge_pop_count,
- pop_tri_to_edge_count,
- pop_edge_to_tri_count,
- pop_quad_to_quad_count,
- edgeswap_count,
- t1_edgeswap_count.
Normally, a count is set to 0 at the start of a command that potentially affects it, accumulated during the execution of the command, and printed at the end of the command. To be precise, each counter has a "reported" bit associated with it, and if the "reported" bit is set when the appropriate command (such as ' u ' for equi_count) is encountered, the counter will be reset to 0 and the "reported" bit cleared. The "reported" bit is set by either flush_counts or the end of a command. The idea is to have the counts from previous commands available to subsequent commands as long as possible, but still have the counter reflect recent activity.

## REVERSE_ORIENTATION
Main prompt command. For reversing the orientation of sets of edges or facets. Syntax:

```text

   REVERSE_ORIENTATION generator


```
Reverses the internal orientation of selected edges or facets, as if they had been entered in the datafile with the opposite orientation. Useful, for example, when edges come in contact with a constraint and you want to get them all oriented in the same direction. Relative orientations of constraint and quantity integrals change to compensate, so energy, volumes, etc. should be the same after the command, but it would be wise to check in your application. Examples:

## RITZ
Main prompt command. For finding eigenvalues of the energy Hessian near a given value. Syntax:

```text

   RITZ(expr,expr)


```
Applies powers of inverse shifted Hessian to a random subspace to calculate eigenvalues near the shift value. First argument is the shift. Second argument is the dimension of the subspace, which is the desired number of eigenvalues. It first prints out the number of eigenvalues less than, equal to, and greater than the shift value, as in the eigenprobe command. Prints out eigenvalues as they converge to machine accuracy. This may happen slowly, so you can interrupt it by hitting whatever your interrupt key is, such as CTRL-C, and the current values of the remaining eigenvalues will be printed out. Good for examining multiplicities of eigenvalues. It is legal to shift to an exact eigenvalue, but not wise, as they will not be printed. See the Hessian tutorial for more. The first eigenvalue is subsequently available in the last_eigenvalue internal variable. The full list of eigenvalues produced is available in the eigenvalues[] array. Example: To get the lowest 5 eigenvalues of a Hessian you know is positive definite:

## RENUMBER_ALL
Reassigns element id numbers of all types of elements in accordance with order in storage, i.e. as printed with the list commands. Syntax:

```text

   RENUMBER_ALL


```
Besides renumbering after massive topology changes, this can be used with the reorder_storage command to number elements as you desire. Do NOT use this command inside an element generator loop!

## REORDER_STORAGE
Reorders the storage of element data structures, sorted by the extra attributes vertex_order_key, edge_order_key, facet_order_key, body_order_key, and facetedge_order_key. Originally written for testing dependence of execution speed on storage ordering, but could be useful for other purposes, particularly when renumber_all is used afterwards. Example:

## SADDLE
Main prompt command. Seek to minimum energy along the eigenvector of the lowest negative eigenvalue of the Hessian. If there is no negative eigenvalue, then the surface is unchanged. The alternate form

```text

   SADDLE expr


```
will limit the step size to expr. The motion vector is available afterwards through the move command.

## SET
Main prompt command. For setting element attributes to values, or set boolean attributes to true. Syntax:

```text

   SET generator attrib expr1 [ WHERE expr2 ]

   SET generator attrib [ WHERE expr ]

   SET quantityname attrib expr

   SET quantityname attrib

   SET instancename attrib expr


```
Here generator refers to an element generator without a where clause; I thought the commands read more naturally with the where clause last. The first form set the value of the attribute attrib to the value expr1 for all elements of the given type that satisfy expr2. The second form is used to set boolean attributes to true. SET can change the following attributes: constraint, coordinates, density, orientation, user-defined extra attributes, body target volume, body volconst, fixed, frontbody, backbody, pressure, color, frontcolor, backcolor, etc. Boolean attributes include fixed, bare, no_refine, named quantities, named method instances, etc.. Setting the pressure on a body automatically unfixes its target volume, and vice versa. For constraint, the expr is the constraint number. If using set to put a vertex on a parametric boundary, set the vertex's boundary parameters p1, p2, etc. first. Examples:
The last two forms set the value of a named quantity or named method instance attribute. For a named quantity, the settable attributes are target, modulus, volconst, and tolerance. For a named method instance, only modulus. There is no implicit reference to the quantity in the expression, so say

```text

   set myquant target myquant.value


```
rather than set myquant target value. Probably easier to use ordinary assignment syntax, for example But set is useful for setting quantity boolean attributes fixed, energy, info_only, and conserved. Example:
Also see unset.

## SHELL
Main prompt command. Invokes a system subshell for the user on systems where this is possible. No arguments. Syntax:

```text

   SHELL


```
See the system command for execution of an explicit shell command.

## SHOW
Main prompt command. Which edges and facets are actually shown in graphics displays can be controlled by defining boolean expressions that edges or facets must satisfy in order to be passed to the graphics display. There are two expressions internally: one for edges and one for facets. They may be set with the syntax

```text

   SHOW EDGES [name] WHERE expr

   SHOW FACETS [name] WHERE expr


```
The default is to show all facets, and to show all special edges: fixed edges, constraint edges, boundary edges, and edges without exactly two adjacent facets. The defaults can be restored with " show facets " and " show edges ". Some graphics modules (like geomview) can show edges of facets on their own initiative. This is separate from the edge show criterion here; to show the colors of edges, the edges must satisfy the criterion. Show causes graphics to be redrawn. If a graphics display is not active, show will start screen graphics. Show_expr is the same as show in setting the show expressions, except it does not start graphics. Show alone will just start screen graphics. Examples: The string model will show facets (default is not to show them) as the facet show expression specifies, but the triangulation algorithm is fairly simple.
As an edge or facet attribute, show is a Boolean read-only attribute giving the current status of the edge or facet. For example, to report the number of edges being shown, do

## SHOW_EXPR
Main prompt command. This does the same as show, except it does not start or redraw graphics; it just sets a show expression. Good for use in the read section of the datafile for controlling which elements will be displayed without automatically starting a display.

## SHOW_TRANS
Main prompt command. Applies string of graphics commands to the image transformation matrix without doing any graphic display. Syntax:

```text

   SHOW_TRANS string


```
The string must be in double quotes or be a string variable, and is the same format as is accepted by the regular graphics command prompt. Example:

## SHOWQ
Main prompt command. Displays screen graphics, but returns immediately to the main prompt and does not go into graphics command mode. Syntax:

```text

   SHOWQ


```
Good for scripts, or the read section of the datafile to start graphics automatically.

## SIMPLEX_TO_FE
Main prompt command. Converts a simplex model surface to a string or soapfilm model surface. Syntax:

```text

   SIMPLEX_TO_FE


```
Only works for dimension 1 or 2 surfaces, but works in any ambient dimension.

## SOBOLEV
Main prompt command. Uses a positive definite approximation to the area Hessian to do one Newton iteration, following a scheme due to Renka and Neuberger [RN]. Works only on area with fixed boundary; no volume constraints or anything else. Seems to converge very slowly near minimum, so not a substitute for other iteration methods. But if you have just a simple soap film far, far from the minimum, then this method can make a big first step. sobolev_seek will do an energy-minimizing search in the direction.

## SPRINTF
Main prompt command. Prints to a formatted string using the standard C sprintf function. May be used whereever a stringexpr is called for in syntax. Otherwise same as printf. Syntax:

```text

   SPRINTF stringexpr,expr,expr,...


```

## SUBCOMMAND
Main prompt command. Invokes a subsidiary command interpreter. Syntax: Useful if you want to pause in the middle of a script to give the user the chance to enter commands. A subcommand interpreter gives the prompt Subcommand: instead of Enter command:. Subcommands may be nested several deep, in which case the prompt will display the subcommand level. To exit a subcommand prompt, use q, quit, or exit. The abort command will return to the prompt on the same subcommand level.

## SYSTEM
Main prompt command. For executing a program outside Evolver. Syntax:

```text

  SYSTEM stringexpr


```
Invokes a subshell to execute the given command, on systems where this is possible. Command must be a quoted string or a string variable. Will wait for command to finish before resuming.

## TRANSFORM_DEPTH
Main prompt command. Quick way of generating all possible view transforms from view transform generators, to a given depth n. Syntax:

```text

  TRANSFORM_DEPTH n


```
where n is the maximum number of generators to multiply together. This will toggle immediate showing of transforms, if they are not already being shown.

## TRANSFORM_EXPR
Main prompt command. If view transform generators were included in the datafile, then a set of view transforms may be generated by an expression with syntax much like a regular expression. Syntax:

```text

   TRANSFORM_EXPR stringexpr


```
The expression in the string generates a set of transform matrices, and are compounded by the following rules. Here a lower-case letter stands for one of the generators, and an upper-case letter for an expression. The expression syntax:

a Generates set {I,a}.

!a Generates set {a}.

AB Generates all ordered products of pairs from A and B.

nA Generates all n-fold ordered products.

A|B Generates union of sets A and B.

(A) Grouping; generates same set as A.

The precedence order is that nA is higher than AB which is higher than A|B. The "!" character suppresses the identity matrix in the set of matrices generated so far. Note that the expression string must be enclosed in double quotes or be a string variable. Examples: All duplicate transforms are removed (see view_transforms_use_unique_point for the definition of duplicate), so the growth of the sets does not get out of hand. Note the identity transform is always included. The letter denoting a single generator may be upper or lower case. The order of generators is the same as in the datafile. In the torus model, transforms along the three period vectors are always added to the end of the list of generators given in the datafile. If 26 generators are not enough for somebody, let me know. The current value of the expression may be accessed as a string variable transform_expr, and the number of transformations generated can be accessed as transform_count. For example,

## T1_EDGESWAP
Main prompt command. Does a T1 topological transition in the string model. When applied to an edge joining two triple points, it reconnects edges so that opposite faces originally adjacent are no longer adjacent, but two originally non-adjacent faces become adjacent.

```text

      \_/   =>   \ /
      / \         |
                 / \


```
It will silently skip edges it is applied to that don't fulfill the two triple endpoint criteria, or whose flipping is barred due to fixedness or constraint incompatibilities. The number of edges flipped can be accessed through the t1_edgeswap_count internal variable. Running with the verbose toggle on will print details of what it is doing. Syntax:

```text

   T1_EDGESWAP edge_generator


```

## UNFIX
Main prompt command. Removes the fixed attribute from a set of elements. Syntax:

```text

   UNFIX generator


```
Example: Can also convert a parameter from non-optimizing to optimizing. Example: Can also convert a named quantity from fixed info_only.

## UNSET
Main prompt command. Removes a boolean attribute from a set of elements. Syntax:

```text

   UNSET elements [name] attrib where clause


```
Unsettable attributes are fixed ( vertices, edges, or facets) , body target volume, body pressure, body gravitational density, non-global named quantities, non-global named methods, level-set constraints, parametric boundary, frontbody, or backbody. A use for the last is to use a boundary or constraint to define an initial curve or surface, refine to get a decent triangulation, then use "unset vertices boundary 1" and "unset edges boundary 1" to free the curve or surface to evolve. The form "unset facet bodies ..." is also available to disassociate given facets from their bodies. Examples:

## VERTEX_AVERAGE
Main prompt command. Does vertex averaging for one vertex at a time. Syntax:

```text
  VERTEX_AVERAGE vertex_generator


```
The action is the same as the V command, except that each new vertex position is calculated sequentially, instead of simultaneously, and an arbitrary subset of vertices may be specified. Fixed vertices do not move. Examples:

## VERTEX_MERGE
Main prompt command. Merges two soapfilm-model vertices into one. Meant for joining together surfaces that bump into each other. Should not be used for vertices already joined by an edge. Syntax:

```text

  VERTEX_MERGE(expr,expr)


```
Note the syntax is a function taking integer vertex id arguments, not element generators. The first vertex exists after execution.. Example:

## WHEREAMI
Main prompt command. If Evolver is at a debugging breakpoint, then whereami will print a stack trace of the sequence of commands invoked to get to the current breakpoint. Syntax:

```text

   WHEREAMI


```

## WRAP_VERTEX
Main prompt command. Syntax:

```text

   WRAP_VERTEX(vexpr,wexpr)


```
In a symmetry group model (usually the torus model), transforms the coordinates of vertex number vexpr by symmetry group element wexpr and adjusts wraps of adjacent edges accordingly. Good for tidying up vertices that have wandered too far outside the unit cell during evolution. See the file rewrap.cmd in the Evolver distribution for an example of its use.

## ZOOM
Main prompt command. For isolating a region of a surface. Syntax: Zooms in on vertex whose id is the given integer, with radius the given expr. Same as the ' Z ' command, but not interactive. Back to top of Surface Evolver documentation. Index.
