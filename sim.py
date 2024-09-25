import sys
import nfa


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} <nfa_file.txt> <input_string>")
        exit(1)
    filename, input_str = sys.argv[1], sys.argv[2]
    with open(filename) as file:
        automate = nfa.NFA().read_from_file(file)
        print(automate.accepts(input_str))
