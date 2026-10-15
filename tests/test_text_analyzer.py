"""Pruebas unitarias de src/text_analyzer.py."""

import unittest

from src import text_analyzer as ta


class CharacterCountTests(unittest.TestCase):
    def test_counts_spaces_and_letters(self):
        self.assertEqual(ta.count_characters("hola mundo"), 10)

    def test_empty_text_has_zero_characters(self):
        self.assertEqual(ta.count_characters(""), 0)
        self.assertEqual(ta.count_characters_without_whitespace(""), 0)

    def test_newlines_are_characters(self):
        self.assertEqual(ta.count_characters("a\nb"), 3)

    def test_decomposed_accent_counts_as_one_character(self):
        decomposed = "café"  # "e" + tilde combinable
        self.assertEqual(ta.count_characters(decomposed), 4)

    def test_without_whitespace_excludes_spaces_tabs_and_newlines(self):
        self.assertEqual(ta.count_characters_without_whitespace("hola  mundo\n\tfin"), 12)

    def test_without_whitespace_keeps_punctuation_and_accents(self):
        self.assertEqual(ta.count_characters_without_whitespace("¡Sí, señor!"), 10)


class TokenizeAndWordCountTests(unittest.TestCase):
    def test_removes_edge_punctuation_and_lowercases(self):
        self.assertEqual(
            ta.tokenize("Hola, mundo! ¿Cómo estás?"), ["hola", "mundo", "cómo", "estás"]
        )

    def test_repeated_spaces_do_not_create_words(self):
        self.assertEqual(ta.count_words("  uno   dos  \n\n  tres "), 3)

    def test_empty_and_whitespace_only_text(self):
        self.assertEqual(ta.count_words(""), 0)
        self.assertEqual(ta.count_words("   \n\t  "), 0)

    def test_punctuation_only_fragments_are_not_words(self):
        self.assertEqual(ta.count_words("... ¡¿ --- — !!!"), 0)

    def test_internal_hyphen_and_apostrophe_are_kept(self):
        self.assertEqual(ta.tokenize("bien-estar O'Higgins"), ["bien-estar", "o'higgins"])

    def test_numbers_are_words(self):
        self.assertEqual(ta.tokenize("Tengo 3 gatos en 2026."), ["tengo", "3", "gatos", "en", "2026"])

    def test_spanish_unicode_is_preserved(self):
        self.assertEqual(ta.tokenize("Ñandú, pingüino y canción"), ["ñandú", "pingüino", "y", "canción"])

    def test_words_joined_by_punctuation_without_space_are_one_word(self):
        self.assertEqual(ta.tokenize("hola,mundo"), ["hola,mundo"])

    def test_normalize_word(self):
        self.assertEqual(ta.normalize_word("«(Casa)»,"), "casa")
        self.assertEqual(ta.normalize_word("..."), "")


class LineTests(unittest.TestCase):
    def test_line_counts(self):
        self.assertEqual(ta.count_lines(""), 0)
        self.assertEqual(ta.count_lines("a"), 1)
        self.assertEqual(ta.count_lines("a\n"), 1)
        self.assertEqual(ta.count_lines("a\nb"), 2)
        self.assertEqual(ta.count_lines("a\n\nb\n"), 3)

    def test_windows_line_endings(self):
        self.assertEqual(ta.split_lines("uno\r\ndos\r\n"), ["uno", "dos"])

    def test_empty_lines_include_whitespace_only_lines(self):
        self.assertEqual(ta.count_empty_lines("a\n\n   \nb"), 2)

    def test_single_newline_is_one_empty_line(self):
        self.assertEqual(ta.count_lines("\n"), 1)
        self.assertEqual(ta.count_empty_lines("\n"), 1)


class WordMetricTests(unittest.TestCase):
    def test_average_word_length(self):
        self.assertEqual(ta.average_word_length("ab abcd"), 3.0)

    def test_average_ignores_edge_punctuation(self):
        self.assertEqual(ta.average_word_length("hola,"), 4.0)

    def test_average_of_empty_text_is_zero(self):
        self.assertEqual(ta.average_word_length(""), 0.0)

    def test_shortest_and_longest(self):
        self.assertEqual(
            ta.shortest_and_longest_words("El murciélago come fruta."), ("el", "murciélago")
        )

    def test_ties_keep_first_word(self):
        self.assertEqual(ta.shortest_and_longest_words("sol mar luz"), ("sol", "sol"))

    def test_shortest_and_longest_without_words(self):
        self.assertEqual(ta.shortest_and_longest_words("¡!"), (None, None))


class FrequencyTests(unittest.TestCase):
    def test_frequencies_ignore_case_and_punctuation(self):
        self.assertEqual(ta.word_frequencies("Casa casa CASA, perro."), {"casa": 3, "perro": 1})

    def test_accents_are_not_removed(self):
        self.assertEqual(ta.word_frequencies("canción cancion"), {"canción": 1, "cancion": 1})

    def test_most_common_words(self):
        self.assertEqual(ta.most_common_words("b a b c a b", 2), [("b", 3), ("a", 2)])

    def test_most_common_ties_are_alphabetical_in_spanish(self):
        self.assertEqual(ta.most_common_words("zeta árbol", 2), [("árbol", 1), ("zeta", 1)])

    def test_most_common_limit_larger_than_vocabulary(self):
        self.assertEqual(ta.most_common_words("uno dos", 10), [("dos", 1), ("uno", 1)])

    def test_most_common_invalid_limit(self):
        with self.assertRaises(ValueError):
            ta.most_common_words("hola", 0)

    def test_most_common_on_empty_text(self):
        self.assertEqual(ta.most_common_words("", 5), [])


class WordSearchTests(unittest.TestCase):
    TEXT = "Sol, solo, girasol. El SOL sale."

    def test_contains_whole_word_case_insensitive(self):
        self.assertTrue(ta.contains_word(self.TEXT, "sol"))
        self.assertFalse(ta.contains_word(self.TEXT, "gira"))

    def test_whole_word_vs_substring_count(self):
        self.assertEqual(ta.count_word_occurrences(self.TEXT, "sol"), 2)
        self.assertEqual(ta.count_substring_occurrences(self.TEXT, "sol"), 4)

    def test_substring_case_sensitive(self):
        self.assertEqual(ta.count_substring_occurrences(self.TEXT, "SOL", case_sensitive=True), 1)

    def test_substring_occurrences_do_not_overlap(self):
        self.assertEqual(ta.count_substring_occurrences("aaaa", "aa"), 2)

    def test_empty_fragment_is_rejected(self):
        with self.assertRaises(ValueError):
            ta.count_substring_occurrences("texto", "")

    def test_query_is_normalized_like_words(self):
        self.assertEqual(ta.normalize_query("  ¿Hola?  "), "hola")
        self.assertEqual(ta.count_word_occurrences("hola Hola HOLA", "¡HOLA!"), 3)

    def test_invalid_queries(self):
        for invalid in ("", "   ", "!!!", "dos palabras"):
            with self.subTest(query=invalid):
                with self.assertRaises(ValueError):
                    ta.normalize_query(invalid)

    def test_find_lines_with_word(self):
        text = "uno dos\ntres\nDos y tres\n\ndosis"
        self.assertEqual(ta.find_lines_with_word(text, "dos"), [(1, "uno dos"), (3, "Dos y tres")])

    def test_find_lines_without_matches(self):
        self.assertEqual(ta.find_lines_with_word("a\nb", "c"), [])


if __name__ == "__main__":
    unittest.main()
