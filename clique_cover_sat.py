#!/usr/bin/env python3
import argparse
import subprocess
import sys
import tempfile


# Parsing input file
def parse_input(path):
    edges = []
    with open(path, "r") as f:
        first = f.readline().strip().split()
        if len(first) != 3:
            raise ValueError("First line valid input format: n m k")

        n = int(first[0])
        m = int(first[1])
        k = int(first[2])

        for _ in range(m):
            u, v = map(int, f.readline().strip().split())
            edges.append((u, v))

    return n, k, edges

# Create Complement graph of graph G
def complement_graph(edges, n):
    edge_set = {frozenset((u, v)) for (u, v) in edges}
    comp = []
    for u in range(1, n + 1):
        for v in range(u + 1, n + 1):
            if frozenset((u, v)) not in edge_set:
                comp.append((u, v))
    return comp

# Variable mapping function
def var(v, c, k):
    # for all v in [1,n], for all c in [1,k]
    return (v - 1) * k + c


# Generate CNF form
def generate_cnf(n, k, comp_edges):
    clauses = []

    #1) Each vertex has at least one color
    for v in range(1, n + 1):
        clause = [var(v, c, k) for c in range(1, k + 1)]
        clauses.append(clause)

    #2) Each vertex has at most one color
    for v in range(1, n + 1):
        for c in range(1, k + 1):
            for d in range(c + 1, k + 1):
                clauses.append([-var(v, c, k), -var(v, d, k)])

    #3) Adjacent vertices in complement graph cannot share a color
    for (u, v) in comp_edges:
        for c in range(1, k + 1):
            clauses.append([-var(u, c, k), -var(v, c, k)])

    num_vars = n * k
    return num_vars, clauses

# Write DIMACS CNF
def write_dimacs(num_vars, clauses, path):
    with open(path, "w") as f:
        f.write(f"p cnf {num_vars} {len(clauses)}\n")
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")


# Call Glucose
def call_glucose(cnf_path):
    try:
        proc = subprocess.run(
            ["glucose", "-model", cnf_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
    except FileNotFoundError:
        print("ERROR: Glucose not found. Ensure it's installed and in PATH.")
        sys.exit(1)

    output = proc.stdout.strip().splitlines()

    if not output:
        return None

    # Find out whether it is UNSAT
    for line in output:
        if "UNSAT" in line:
            return None

    # SAT -> return model
    model = []
    for line in output:
        if line.startswith("v"):
            model.extend(map(int, line.split()[1:]))

    return model


# Decode model into clique cover
def decode_model(model, n, k):
    colors = {c: [] for c in range(1, k + 1)}

    for assignment in model:
        if assignment > 0:
            v = (assignment - 1) // k + 1
            c = ((assignment - 1) % k) + 1
            colors[c].append(v)

    return {c: sorted(vs) for c, vs in colors.items() if len(vs) > 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input graph file")
    parser.add_argument("--printcnf", action="store_true", help="Print CNF and exit")
    args = parser.parse_args()

    n, k, edges = parse_input(args.input)
    comp = complement_graph(edges, n)
    num_vars, clauses = generate_cnf(n, k, comp)

    with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
        cnf_path = tmp.name

    write_dimacs(num_vars, clauses, cnf_path)

    if args.printcnf:
        with open(cnf_path) as f:
            print(f.read())
        return

    model = call_glucose(cnf_path)

    if model is None:
        print("UNSAT: No clique cover of size", k)
    else:
        cover = decode_model(model, n, k)
        print("SAT: Clique cover exists with", len(cover), "cliques")
        for c, verts in cover.items():
            print("Clique", c, ":", verts)


if __name__ == "__main__":
    main()
