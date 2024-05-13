from abc import ABC, abstractmethod

# =============================================================================
# --- Parameters --------------------------------------------------------------
# =============================================================================

ASCII_TREE_INDENT = 5   # Indentation for each level within the behavior tree representation

# =============================================================================
# --- Status ------------------------------------------------------------------
# =============================================================================

class Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class Status:
    SUCCESS = 0
    FAILURE = 1
    RUNNING = 2
    NONE = 3

    SYMBOL = "⦿"

    @staticmethod
    def get_symbol(status):
        if status == Status.SUCCESS:
            return f"{Colors.OKGREEN}{Status.SYMBOL}{Colors.ENDC}"
        elif status == Status.FAILURE:
            return f"{Colors.FAIL}{Status.SYMBOL}{Colors.ENDC}"
        elif status == Status.RUNNING:
            return f"{Colors.OKBLUE}{Status.SYMBOL}{Colors.ENDC}"
        elif status == Status.NONE:
            return " "

# =============================================================================
# --- Nodes -------------------------------------------------------------------
# =============================================================================

class Node(ABC):
    def __init__(self, name):
        self.name = name
        self.status = Status.NONE
        self._blackboard = None

    @property
    def blackboard(self):
        if self._blackboard is None:
            raise RuntimeError("No blackboard assigned!")
        self._blackboard.client = self.name
        return self._blackboard

    @staticmethod
    def get_indent_string(indent):
        chars = ["┊" if (idx - 1) % ASCII_TREE_INDENT == 0 else " " for idx in range(indent)]
        return ''.join(chars)

    @abstractmethod
    def attach_blackboard(self, blackboard):
        pass

    @abstractmethod
    def run(self):
        pass

    def reset(self):
        self.status = Status.NONE

# =============================================================================
# --- Control nodes -----------------------------------------------------------
# =============================================================================

class ControlNode(Node):
    def __init__(self, name):
        super().__init__(name)
        self.children = []

    def tick(self):
        self.reset()
        self.run()

    def reset(self):
        self.status = Status.NONE
        [child.reset() for child in self.children]

    def append(self, child):
        self.children.append(child)
        if self._blackboard is not None:
            child.attach_blackboard(self._blackboard)

    def attach_blackboard(self, blackboard):
        self._blackboard = blackboard
        [child.attach_blackboard(blackboard) for child in self.children]

    def run(self):
        pass

    def get_string_tree(self, indent=0):
        if self.__class__.__name__ == "Selector":
            symbol = "?"
        elif self.__class__.__name__ == "Sequence":
            symbol = "→"
        elif self.__class__.__name__ == "ParallelSequence":
            symbol = "⇉"
        else:
            symbol = " "
        string = f"{self.get_indent_string(indent)}[{Status.get_symbol(self.status)}][{symbol}] {Colors.BOLD}{self.name}{Colors.ENDC}\n"
        indent += ASCII_TREE_INDENT
        for child in self.children:
            string += child.get_string_tree(indent)
        return string[:-1] if indent == ASCII_TREE_INDENT else string


class Sequence(ControlNode):
    def run(self):
        for child in self.children:
            child.run()
            if child.status == Status.RUNNING:
                self.status = Status.RUNNING
                return
            elif child.status == Status.FAILURE:
                self.status = Status.FAILURE
                return
        self.status = Status.SUCCESS


class Selector(ControlNode):
    def run(self):
        for child in self.children:
            child.run()
            if child.status == Status.SUCCESS:
                self.status = Status.SUCCESS
                return
            elif child.status == Status.RUNNING:
                self.status = Status.RUNNING
                return
        self.status = Status.FAILURE


class ParallelSequence(ControlNode):
    def run(self):
        status_list = []
        for child in self.children:
            child.run()
            status_list.append(child.status)
        if Status.FAILURE in status_list:
            self.status = Status.FAILURE
        elif Status.RUNNING in status_list:
            self.status = Status.RUNNING
        else:
            self.status = Status.SUCCESS

# =============================================================================
# --- Leaf nodes --------------------------------------------------------------
# =============================================================================

class LeafNode(Node):
    def attach_blackboard(self, blackboard):
        self._blackboard = blackboard

    def run(self):
        pass

    def get_string_tree(self, indent=0):
        running_flag = f"{Colors.OKBLUE} <---- RUNNING{Colors.ENDC}" if self.status == Status.RUNNING else ""
        wrapper = ("<", ">?") if self.__class__.__bases__[0].__name__ == 'Condition' else ("", "")
        string = f"{self.get_indent_string(indent)}[{Status.get_symbol(self.status)}] {wrapper[0]}{self.name}{wrapper[1]}{running_flag}\n"
        return string[:-1] if indent == 0 else string


class Action(LeafNode):
    @abstractmethod
    def run(self):
        pass


class Condition(LeafNode):
    @abstractmethod
    def run(self):
        pass

# =============================================================================
# --- Decorator ---------------------------------------------------------------
# =============================================================================

class Decorator(Node):
    def __init__(self, name, child=None):
        super().__init__(name)
        self.child = child

    @abstractmethod
    def run(self):
        self.child.run()

    def reset(self):
        self.status = Status.NONE
        self.child.reset()

    def set_child(self, child):
        self.child = child
        if self._blackboard is not None:
            self.child.attach_blackboard(self._blackboard)

    def attach_blackboard(self, blackboard):
        self._blackboard = blackboard
        if self.child is not None:
            self.child.attach_blackboard(blackboard)

    def get_string_tree(self, indent=0):
        running_flag = " <-- RUNNING" if self.status == Status.RUNNING else ""
        string = f"{self.get_indent_string(indent)}[{Status.get_symbol(self.status)}][δ] {self.name}{running_flag}\n"
        indent += ASCII_TREE_INDENT
        string += self.child.get_string_tree(indent)
        return string[:-1] if indent == ASCII_TREE_INDENT else string


class Inverter(Decorator):
    def __init__(self, name):
        super().__init__(name)

    def run(self):
        super().run()
        if self.child.status == Status.SUCCESS:
            self.status = Status.FAILURE
        elif self.child.status == Status.FAILURE:
            self.status = Status.SUCCESS
        elif self.child.status == Status.RUNNING:
            self.status = Status.RUNNING

# =============================================================================
# --- Blackboard --------------------------------------------------------------
# =============================================================================

class Blackboard(dict):
    NO_MEMBER = "<<NoMember>>"
    N_CELL_LEN = 25

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Blackboard.NO_MEMBER
        self.activity = []
        self.activity_len = 1000

    def get_activity_str(self, max_len=None, mode=None, key=None, client=None, expand=False):
        results = [ele for ele in self.activity if (
                    (key is None or key == ele["key"] == key) and (mode is None or mode == ele["mode"]) and (
                        ele["client"] == client or client is None))]
        string = ""
        for result in results:
            if result['mode'] == 'write':
                value_str = f"{result['value']}" if result['value'].__class__.__name__ in ["bool", "int", "float", "str", "None"] or expand else "<<NoExpansion>>"
                string += f">> {Colors.OKBLUE}{result['mode'].upper()}{Colors.ENDC} [{Colors.BOLD}{result['client']}{Colors.ENDC}]{max(0, Blackboard.N_CELL_LEN - len(result['client'])) * '.'} {result['key']} : {value_str}\n"
            else:
                string += f">> {Colors.OKGREEN}{result['mode'].upper()}{Colors.ENDC}  [{Colors.BOLD}{result['client']}{Colors.ENDC}]{max(0, Blackboard.N_CELL_LEN - len(result['client'])) * '.'} {result['key']}\n"
        return string

    def prune_activity(self):
        self.activity = self.activity[-self.activity_len:]

    def __getitem__(self, key):
        self.activity.append({"client": self.client, "mode": "read", "key": key})
        self.client = Blackboard.NO_MEMBER
        self.prune_activity()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        self.activity.append({"client": self.client, "mode": "write", "key": key, "value": value})
        self.client = Blackboard.NO_MEMBER
        self.prune_activity()
        super().__setitem__(key, value)



