Surface Evolver Documentation - Energies

# Surface Evolver Documentation
Back to top of Surface Evolver documentation. Index.

# Energies
The Evolver usually works by minimizing the total energy of the surface, subject to constraints. This energy can have several components:

- Surface tension
- Gravitational potential energy
- Constraint energy integrals
- Named quantity energies
- Convex constraint gap energy
- Prescribed pressure energy
- Compressibility energy
- Crystalline energy

## Surface tension energy
Soap films and interfaces between different fluids have an energy content proportional to their area. Hence they shrink to minimize energy. The energy per unit area can also be regarded as a surface tension, or force per unit length. Each facet has a surface tension, which is 1 unless the datafile specifies otherwise (see TENSION attribute for faces). Different facets may have different surface tensions. Facet tensions may be changed interactively with the set facet tension ... command. The contribution to the total energy is the sum of all the facet areas times their respective surface tensions. The surface tension of a facet may also be specified as depending on the phases of the bodies it separates. In the string model, the tension resides on edges instead of facets.
Example datafile: cube.fe

## Gravitational potential energy
If a body has a density, then that body contributes its gravitational energy to the total. The acceleration of gravity G is under user control with the G command. Letting \rho be the body density, the energy is defined as

```text

  E = \int\int\int_{body} G \rho  z  dV


```
but is calculated using the Divergence Theorem as

```text

  E =  \int\int_{body surface} G\rho {z^2\over 2} \vec k \cdot \vec{dS}.


```
This integral is done over each facet that bounds a body. If a facet bounds two bodies of different density, then the appropriate difference in density is used. Facets lying in the z = 0 plane make no contribution, and may be omitted if they are otherwise unneeded. Facets lying in constraints may be omitted if their contributions to the gravitational energy are contained in constraint energy integrals. In the string model, all this happens in one lower dimension.
Example datafile: mound.fe

## Constraint energy integrals
An edge on a level-set constraint may have an energy given by integrating a vectorfield F over the oriented edge:

```text

           E = \int_{edge} F . dl.


```
The integrand is defined in the constraint declaration in the datafile. The integral uses the innate orientation of the edge, but if the orientation attribute of the edge is negative, the value is negated. This is useful for prescribed contact angles on walls (in place of wall facets with equivalent tension) and for gravitational potential energy that would otherwise require facets in the constraint. The mound example illustrates this.

## Named quantity energies
There are a large number of named methods for calculating various quantities, which all follow the same syntax. These may be used as energy by defining an energy-type named quantity in the datafile.
Example datafile: ringblob.fe

## Convex constraint gap energy
Consider a soap film spanning a circular cylinder. The Evolver must approximate this surface with a collection of facets. The straight edges of these facets cannot conform to the curved wall, and hence the computed area of the surface leaves out the gaps between the outer edges and the wall. The Evolver will naturally try to minimize area by moving the outer vertices around so the gaps increase, ultimately resulting in a surface collapsed to a line. This is not good. Therefore there is provision for a "gap energy" to discourage this. A level-set constraint may be declared CONVEX in the datafile. For an edge on such a constraint, an energy is calculated as

```text
  E = k\left\Vert \vec S \times \vec Q \right\Vert / 6


```
where \vec S is the edge vector and \vec Q is the projection of the edge on the tangent plane of the constraint at the tail vertex of the edge. The constant k is a global constant called the "gap constant". A gap constant of 1 gives the best approximation to the actual area of the gap. A larger value minimizes gaps and gets vertices nicely spread out along a constraint. You can set the value of k in the datafile or with the k command.
The gap energy falls off quadratically as the surface is refined. That is, refining once reduces the gap energy by a factor of four. You can see if this energy has a significant effect on the surface by changing the gap constant.
Note: gap energy is effective only in the linear model.
Example datafile: tankex.fe

## Prescribed pressure energy
Each body with a prescribed pressure P contributes energy E = PV. where V is the actual volume of the body. This can be used to generate surfaces of prescribed mean curvature, since mean curvature is proportional to pressure. Pressure can be prescribed in the bodies section of the datafile, and can be changed with the b command, or by assigning a value to the pressure attribute of a body.

## Compressibility energy
If the ideal gas mode is in effect (set by the PRESSURE keyword in the datafile), then each body contributes an energy

```text

         E = P*V_0*ln(V/V_0)

```
where P is the ambient pressure, V_0 is the target volume of the body, and V is the actual volume. To account for work done against the ambeint pressure, each body also makes a negative contribution of

```text

	 E = -P*V.

```
The ambient pressure can be set in the datafile or with the p command. This energy is calculated only for bodies given a target volume.

## Crystalline energy
The Evolver can model energies of crystalline surfaces. These energies are proportional to the area of a facet, but they also depend on the direction of the normal. The energy is given by the largest dot product of the surface normal with a set of vectors known as the Wulff vectors. Surface area can be regarded as a crystalline integrand whose Wulff vectors are the unit sphere. See the datafile section on Wulff vectors for more. A surface has either crystalline energy or surface tension, not both. Use is not recommended since nonsmoothness makes Evolver work poorly.
Example datafile: crystal.fe Back to top of Surface Evolver documentation. Index.
