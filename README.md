# Clique Cover SAT Solver Project - Propositional and Predicate Logic[NAIL062]

This repository contains a solution to a homework project for Propositional and Predicate Logic(NAIL062) class. The provided Python code encodes, solves, and decodes the Clique Cover problem via reduction to SAT i.e propositional logic in CNF form.

The SAT Solver used Glucose(Glucose 4.2.1 version). 

Encoding approach implemented in this solution is based on equivalenting clique cover to graph coloring of the complement graph. 
SAT Encoding Solves: Does there exist a clique cover of size at most k?

# Problem Description
Given an undirected graph G=(V,E), a clique cover is a partition of the vertices V into disjoint cliques such that every vertex belongs to exactly one clique. The Cluque Cover Problem solves following:
"For a given graph G and integer k, decide whether G can be covered by at most k cliques."

More details on Clique Cover can be found here: https://en.wikipedia.org/wiki/Clique_cover

-- Valid Input Format
n m k
u v
u v
...

where n - number of vertices, m - number of edges, k - maximum allowed number of cliques, next m lines are edges of the graph, such that for all v in V v in {1,..n}(i.e vertices are numbered 1,..,n)

-- Output Format
SAT: Clique cover found with ${number_of_cliques} cliques
Clique 1 : [v1, v2, ...]
Clique 2 : [v3, v4, ...]
...

# Encoding
Clique cover with k cliques in graph G <=> partition of V into at most k cliques in graph G 
<=> partition of V into at most k disjoint sets in complement G <=> proper k-coloring of complement G.
Hence, we encode SAT fromula that checkes whether complement G is k-colorable.

-- Propositional Variables
X_v,c ​≡ vertex v is assigned to clique c

X_v,c = 1 iff v is colored with c
X_v,c = 0 if v is not colored with c

-- Logical Constraints
1) Each vertex belongs to at least one clique(or Each vertex has at least one color)
For all v in V Clause = X_v,1 ∨ X_v,2 ∨ ....

2) Each vertex is assigned to at most one clique(or Each vertex has at most one color)
For all v in V, for all c,d in {1,...k} | c < d
¬(X_v,c ∧ X_v,d) ​≡ ¬X_v,c ∨ ¬X_v,d

3) Adjecent vertices in complement G cannot share a clique
for all (u,v) in E(complement G), for all c in {1,..k}
¬(X_u,c ∧ X_v,c) ​≡ ¬X_u,c ∨ ¬X_v,c

# User Documentation
-- Basic Usage
- To execute the script, implement the following code:
    python3 clique_cover_sat.py --input <instance-file>

    Command - Line Options:
    * `-h`, `--help` : Show a help message.
    * `--input INPUT` : The  instance file to be processed
    * `--printcnf` : Instead of running the SAT solver, print the DIMACS CNF encoding of the instance.

- To generate CNF Formula
    To have a CNF encoding for your specific SAT instance, paste your instance in the valid input format to "small_sat.txt" file
    and run the following command in your comand line:

    python3 clique_cover_sat.py --input instances/small_sat.txt --printcnf > formula.cnf

    The file "formula.cnf" contains DIMACS CNF encoding.

-- Included Instances
* small_sat.txt - Simple graph with clique cover - Result: SAT
* small_unsat.txt - Graph requiring more than k cliques - Result: UNSAT
* hard_sat.txt - Large instance - Result: SAT
* hard_sat_big.txt - Very large instance - Result(SAT)

# Experiments
Experiments were run on Intel Core i5 CPU inside WSL(Windows 11), Ubuntu Linux environment.
Performance - Table for included instances was created using:
time python3 clique_cover_sat.py --input instances/<$instance$.txt>

| Instance            | Vertices          | Cliques Allowed(k) | Solvable? | Time (s) |
| small_sat.txt       | 4                 | 2                  | Yes       | 0.129    |
| small_unsat.txt     | 4                 | 1                  | No        | 0.078    |
| hard_sat.txt        | 80                | 4                  | Yes       | 0.039    |
| hard_sat_big.txt    | 200               | 5                  | Yes       | 0.189    |

-- Comment:
To search for an instance that runs on non-trivial amount of time(at least 10s), I developed simple instance generator (`generate_hard_instance.py`) that constructs a disjoint union of k cliques, with size N(each). This ensures that a clique cover of size k exists, and the size of the encoding grows with N and k.

I made experiemnts with different number of vertices(for example up to N = 20 and k = 4, i.e n = 80 vertices). Even for the largest instances I tried, Glucose 4.2.1 solved the resulting formulas well under one second on my CPU (for `hard_sat_big.txt`, the runtime was 0.189s, though it was 200 vertices, and 3900 edges).
