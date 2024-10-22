from dataclasses import dataclass
from typing import Optional


@dataclass
class Node:
    letter: int | None = None
    left: Optional['Node'] = None
    right: Optional['Node'] = None
    next: Optional['Node'] = None
    terminal: bool = False


class TrieBuilder:
    def __init__(self, data: bytes):
        self.data = data

    def read_n_be(self, offset: int, n: int) -> int:
        num = 0
        for i in range(n):
            num <<= 8
            num += self.data[offset + i]
        return num

    def parse_block(self, offset: int) -> Node | None:
        if offset >= len(self.data):
            return None

        t = self.data[offset]

        is_terminal = bool(t & 0b10000000)
        has_next = bool(t & 0b01000000)
        has_letter = is_terminal or has_next

        left_len = (t >> 3) & 0b111
        right_len = t & 0b111

        letter = None
        if has_letter:
            letter = self.data[offset + 1]

        left = None
        if left_len:
            left_offset = self.read_n_be(offset + has_letter + 1, left_len)
            left = self.parse_block(offset + left_offset)

        right = None
        if right_len:
            right_offset = self.read_n_be(offset + has_letter + left_len + 1, right_len)
            right = self.parse_block(offset + right_offset)

        next = None
        if has_next:
            next = self.parse_block(offset + has_letter + left_len + right_len + 1)

        return Node(
            letter,
            left,
            right,
            next,
            is_terminal
        )

    def parse(self) -> Node:
        node = self.parse_block(0)

        if node is None:
            raise ValueError("Invalid bytes")

        return node


class TrieTraverser:
    def __init__(self, root: Node):
        self.root = root
        self.words: list[bytes] = []

    def traverse(self) -> list[bytes]:
        self.collect_words(self.root, bytes())
        return self.words

    def collect_words(self, node: Node, current_word: bytes) -> None:
        if node.left:
            self.collect_words(node.left, current_word)

        if node.right:
            self.collect_words(node.right, current_word)

        if node.letter is not None:
            current_word += node.letter.to_bytes(1)

            if node.terminal:
                self.words.append(current_word)

            if node.next:
                self.collect_words(node.next, current_word)


if __name__ == "__main__":
    from sys import argv

    with open(argv[1], "rb") as f:
        data = f.read()

    root = TrieBuilder(data).parse()

    words = TrieTraverser(root).traverse()

    print("\n".join([i.decode("utf-8") for i in sorted(words)]))
