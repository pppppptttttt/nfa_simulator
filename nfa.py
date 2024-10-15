from collections import defaultdict


class NFA:
    def __init__(self, states_size=0, alphabet_size=0,
                 start_states={}, accept_states={}, transitions={}):
        if states_size < 0 or alphabet_size < 0:
            raise ValueError

        self._states_size = states_size
        self._alphabet_size = alphabet_size
        self._start_states = start_states
        self._accept_states = accept_states
        self._transitions = transitions
        self.__processed_list = []
        self.__normalized = True

    def read_from_file(self, file):
        self = NFA(
            states_size=int(file.readline().strip()),
            alphabet_size=int(file.readline().strip()),
            start_states=set(map(int, file.readline().strip().split())),
            accept_states=set(map(int, file.readline().strip().split()))
        )

        for line in file.readlines():
            a, b, c = map(int, line.strip().split())
            self.add_transition(a, b, c)
        return self

    def add_transition(self, a_state, symbol, b_state):
        if self._transitions.get(a_state) is not None:
            if self._transitions[a_state].get(symbol) is not None:
                self._transitions[a_state][symbol].add(b_state)
            else:
                self._transitions[a_state][symbol] = {b_state}
        else:
            self._transitions[a_state] = {symbol: {b_state}}

    def _move(self, current_states, symbol):
        next_states = set()

        for state in current_states:
            if self._transitions.get(state) is not None:
                if symbol in self._transitions[state]:
                    next_states.update(self._transitions[state][symbol])
        return next_states

    def accepts(self, input):
        current_states = self._start_states.copy()

        for sym in input:
            sym = int(sym)
            current_states = self._move(current_states, sym)
            if not current_states:
                return False

        return bool(current_states & self._accept_states)

    def _get_reachable_states(self):
        reachable_states = set()
        states_stack = list(self._start_states)

        while states_stack:
            state = states_stack.pop()
            if state not in reachable_states:
                reachable_states.add(state)
                for symbol in self._transitions.get(state, {}):
                    for next_state in self._transitions[state][symbol]:
                        if next_state not in reachable_states:
                            states_stack.append(next_state)
        return reachable_states

    def to_DFA(self):
        """
        This method converts `self` to DFA. Even some types of fields
        changes because we are merging states together (e.g. set -> frozenset,
        because set is not hashable)

        To normalize self, call `normalize` method
        """

        self.__normalized = False

        dfa_states = {}
        dfa_transitions = defaultdict(dict)
        # Note: start state is one, but there we can add transition by empty
        # string from it to actual start states
        dfa_start_state = frozenset(
            self._start_states & self._get_reachable_states()
        )
        dfa_accept_states = set()

        states_queue = [dfa_start_state]
        processed = set()
        while states_queue:
            current = states_queue.pop(0)

            if current in processed:
                continue

            processed.add(current)

            if current & self._accept_states:
                dfa_accept_states.add(current)

            for symbol in range(self._alphabet_size):
                next_state = self._move(current, symbol)

                if next_state:
                    next_state_frozenset = frozenset(next_state)

                    if next_state_frozenset not in dfa_states:
                        states_queue.append(next_state_frozenset)

                    dfa_transitions[current][symbol] = next_state_frozenset

        def is_dead(state):
            return not any(dfa_transitions[state].values())

        dfa_states = {state: dfa_transitions[state]
                      for state in processed if not is_dead(state)}

        self.__processed_list = list(processed)

        self._start_states = dfa_start_state
        self._accept_states = dfa_accept_states
        self._transitions = dfa_states

    def normalize(self):
        """
        Normalize all states. Should be called after self.to_DFA(),
        but for testing purposes moved to separate method. For that
        reason also having `processed` in separate field and `normalized`
        flag
        """
        if self.__normalized:
            return

        self._start_states = {
            self.__processed_list.index(self._start_states)
        }

        self._accept_states = {self.__processed_list.index(ast)
                               for ast in self._accept_states}

        normalized_transitions = {}
        for state, transit in self._transitions.items():
            state = self.__processed_list.index(state)
            normalized_transitions[state] = {}
            for k, v in transit.items():
                v = self.__processed_list.index(v)
                normalized_transitions[state].update({k: {v}})

        self._transitions = normalized_transitions
        self.__normalized = True

    def write_to_file(self, filename):
        if not self.__normalized:
            self.normalize()

        with open(filename, "w") as file:
            file.write(f"{self._states_size} \n")

            file.write(f"{self._alphabet_size} \n")

            file.write(" ".join(list(map(str, self._start_states))))
            file.write("\n")

            file.write(" ".join(list(map(str, self._accept_states))))
            file.write("\n")

            for state, transit in self._transitions.items():
                # poor naming but i'm out of ideas:(
                for k, v in transit.items():
                    for vv in v:
                        file.write(f"{state} {k} {vv}")
                        file.write("\n")

    def minimize(self):
        # convert self to dfa first. for testing purposes (for lecture example
        # to work), removed (need normal state names,i'm confused otherwise:( )
        # self.to_DFA()
        # if not self.__normalized:
        #     self.normalize()

        reachable_states = self._get_reachable_states()
        self._transitions = {
            state: trans
            for state, trans in self._transitions.items()
            if state in reachable_states}
        self._start_states.intersection_update(reachable_states)
        self._accept_states.intersection_update(reachable_states)

        states = list(self._transitions.keys())
        n = len(states)
        M = [[None for _ in range(n)] for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                if (states[i] in self._accept_states) !=\
                   (states[j] in self._accept_states):
                    M[i][j] = -1
                    M[j][i] = -1

        changed = True
        while changed:
            changed = False
            for i in range(n):
                for j in range(i + 1, n):
                    for symbol in range(self._alphabet_size):
                        ii = list(self._transitions[states[i]][symbol])[0]
                        ji = list(self._transitions[states[j]][symbol])[0]

                        if M[i][j] is None and M[ii][ji] is not None:
                            M[i][j] = symbol
                            M[j][i] = symbol
                            changed = True
                            break

        new_states_map = {}
        new_transitions = defaultdict(dict)
        new_accept_states = set()

        new_state_index = 0
        for i in range(n):
            for j in range(i + 1, n):
                if M[i][j] is None:
                    state = states[i]
                    if state not in new_states_map:
                        new_states_map[state] = new_state_index
                        new_state_index += 1
                    new_state = new_states_map[state]

                    if states[j] not in new_states_map:
                        new_states_map[states[j]] = new_state

                    for symbol in self._transitions[states[i]]:
                        target_states = self._transitions[states[i]][symbol]
                        if target_states:
                            target_state = next(iter(target_states))
                            new_transitions[new_state][symbol] = (
                                new_states_map.get(target_state, target_state)
                            )

                    if states[i] in self._accept_states:
                        new_accept_states.add(new_state)

        self._transitions = new_transitions
        self._start_states = {
            new_states_map.get(state) for state in self._start_states
        }
        self._accept_states = new_accept_states
