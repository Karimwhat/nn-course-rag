Singular Value Decomposition
January 12, 2026 8:32 AM

Consider matrix $A$ which is $m \times n$

The right singular vectors/values of $A$:
$A^T A \vec{v} = \lambda \vec{v}$

The left singular vectors/values
$AA^T \vec{u} = \sigma \vec{u}$

$AA^T(A\vec{v}) = \lambda(A\vec{v})$

$A\vec{v}$ is an eigenvectors of $AA^T$.

$A\vec{v} \propto \vec{u}$

$|A\vec{v}| = \sqrt{(\vec{v} A)^T (A\vec{v})}$
$= \sqrt{\vec{v}^T A^T A \vec{v}}$
$= \sqrt{\vec{v}^T \lambda \vec{v}}$
$= \sqrt{\lambda}$

COMP 4107 W2026 Page 1